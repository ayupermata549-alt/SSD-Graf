"""
cp_prove.py — buktikan rn EKSAK dgn CP-SAT, memakai batas atas KETAT (incumbent
dari run sebelumnya) + batas bawah LB_W untuk memangkas ruang pencarian.

ub ketat = f_v in [0, ub], S in [lb, ub]. Makin sempit -> makin cepat terbukti.
"""
import sys, os, time
sys.path.insert(0, os.getcwd())
import networkx as nx
from ortools.sat.python import cp_model
from supersubdivision_graf_algorithm import build_ssd_ladder
from lower_bound_ladder import params, lower_bound_W


def prove_rn(G, d, ub, lb, dist, tl, workers=10):
    nodes = list(G.nodes())
    m = cp_model.CpModel()
    f = {v: m.NewIntVar(0, ub, f"f_{i}") for i, v in enumerate(nodes)}
    S = m.NewIntVar(max(lb, 0), ub, "S")
    for v in nodes:
        m.Add(S >= f[v])
    zmin = m.NewIntVar(0, ub, "zmin")
    m.AddMinEquality(zmin, [f[v] for v in nodes])
    m.Add(zmin == 0)
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
    solver.parameters.num_search_workers = workers
    t0 = time.time()
    st = solver.Solve(m)
    el = time.time() - t0
    val = int(solver.ObjectiveValue()) if st in (cp_model.OPTIMAL,
                                                  cp_model.FEASIBLE) else None
    bound = int(solver.BestObjectiveBound())
    return val, bound, solver.StatusName(st), el, (st == cp_model.OPTIMAL)


# (k, n, ub_ketat) dari incumbent run sebelumnya
CASES = [
    (3, 2, 25), (4, 2, 31),
    (2, 3, 52), (1, 4, 62), (3, 3, 71),
    (2, 4, 101), (1, 5, 102), (1, 6, 154),
]
TL = float(sys.argv[1]) if len(sys.argv) > 1 else 280.0

print(f"{'k':>2} {'n':>2} | {'|V|':>4} {'d':>3} {'p':>4} | "
      f"{'lb_W':>5} {'ub':>5} | {'rn':>5} {'bound':>5} | {'time':>6} {'proven':>7}")
print("-" * 74)
for (k, n, ub) in CASES:
    G, _, _ = build_ssd_ladder(k, n)
    nV, p, d = params(k, n)
    dist = dict(nx.all_pairs_shortest_path_length(G))
    lb = lower_bound_W(k, n)
    rn, bound, name, el, proven = prove_rn(G, d, ub, lb, dist, TL)
    print(f"{k:>2} {n:>2} | {nV:>4} {d:>3} {p:>4} | "
          f"{lb:>5} {ub:>5} | {str(rn):>5} {bound:>5} | "
          f"{el:>5.0f}s {str(proven):>7}  [{name}]", flush=True)
