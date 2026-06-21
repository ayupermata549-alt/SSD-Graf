"""dump_label.py — selesaikan rn via CP-SAT lalu cetak pelabelan optimal
TERURUT menurut label, dgn nama kanonik + gap, untuk merekayasa-balik pola.

pakai:  python dump_label.py k n [ub] [tl]
"""
import sys, os
sys.path.insert(0, os.getcwd())
import networkx as nx
from ortools.sat.python import cp_model
from supersubdivision_graf_algorithm import build_ssd_ladder, graph_center
from lower_bound_ladder import params

k = int(sys.argv[1]); n = int(sys.argv[2])
ub = int(sys.argv[3]) if len(sys.argv) > 3 else None
tl = float(sys.argv[4]) if len(sys.argv) > 4 else 60.0

G, _, _ = build_ssd_ladder(k, n)
nV, p, d = params(k, n)
dist = dict(nx.all_pairs_shortest_path_length(G))
nodes = list(G.nodes())
if ub is None:
    ub = p * (d + 1)

m = cp_model.CpModel()
f = {v: m.NewIntVar(0, ub, f"f_{i}") for i, v in enumerate(nodes)}
S = m.NewIntVar(0, ub, "S")
for v in nodes:
    m.Add(S >= f[v])
zmin = m.NewIntVar(0, ub, "zmin")
m.AddMinEquality(zmin, [f[v] for v in nodes]); m.Add(zmin == 0)
for i in range(len(nodes)):
    for j in range(i + 1, len(nodes)):
        u, w = nodes[i], nodes[j]
        need = d + 1 - dist[u][w]
        b = m.NewBoolVar(f"b_{i}_{j}")
        m.Add(f[u] - f[w] >= need).OnlyEnforceIf(b)
        m.Add(f[w] - f[u] >= need).OnlyEnforceIf(b.Not())
m.Minimize(S)
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = tl
solver.parameters.num_search_workers = 8
st = solver.Solve(m)

center = set(graph_center(G))
print(f"SSD_{k}(L_{n})  |V|={nV} d={d} p={p}  span={int(solver.ObjectiveValue())}"
      f"  [{solver.StatusName(st)}]  center={sorted(center)}")
lab = sorted(nodes, key=lambda v: solver.Value(f[v]))
prev = None
print(f"{'#':>3} {'vertex':>10} {'label':>6} {'gap':>4} "
      f"{'d_to_prev':>9} {'role':>5}")
for idx, v in enumerate(lab):
    val = solver.Value(f[v])
    gap = "" if prev is None else val - solver.Value(f[prev])
    dpv = "" if prev is None else dist[prev][v]
    role = "C" if v in center else ("orig" if v[0] in "uv" else "sub")
    print(f"{idx:>3} {v:>10} {val:>6} {str(gap):>4} {str(dpv):>9} {role:>5}")
    prev = v
