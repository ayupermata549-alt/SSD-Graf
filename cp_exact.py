"""
cp_exact.py — rn EKSAK untuk SSD_k(L_n) via CP-SAT (OR-Tools).

Kendala radio |f_u - f_w| >= d+1-dist(u,w) diposting sbg disjungsi reified
(bukan big-M), jadi CP-SAT memberi optimal TERBUKTI jauh lebih cepat dari CBC.

Status OPTIMAL dari CP-SAT = benar-benar optimal (ada sertifikat bound),
beda dgn CBC yang sering melaporkan incumbent sbg 'Optimal'.
"""
import sys, os, time
sys.path.insert(0, os.getcwd())
import networkx as nx
from ortools.sat.python import cp_model
from supersubdivision_graf_algorithm import build_ssd_ladder
from lower_bound_ladder import params, lower_bound_W
from radio_bounds import upper_bound_greedy


def exact_rn_cpsat(G, d, ub, dist, tl, workers=8):
    nodes = list(G.nodes())
    m = cp_model.CpModel()
    f = {v: m.NewIntVar(0, ub, f"f_{i}") for i, v in enumerate(nodes)}
    S = m.NewIntVar(0, ub, "S")
    for v in nodes:
        m.Add(S >= f[v])
    # patok salah satu titik ke 0 utk pecah simetri translasi (aman: optimal
    # selalu bisa digeser agar label minimum = 0, dan nodes[0] boleh jadi
    # titik berlabel 0? TIDAK aman. Pakai: paksa min=0 via salah satu f=0).
    # Aman & memecah simetri: tambahkan kesetaraan min.
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
    name = solver.StatusName(st)
    val = int(solver.ObjectiveValue()) if st in (cp_model.OPTIMAL,
                                                  cp_model.FEASIBLE) else None
    proven = (st == cp_model.OPTIMAL)
    return val, name, el, proven


CASES = [
    (1, 2), (2, 2), (3, 2), (1, 3),
    (4, 2), (2, 3), (1, 4), (3, 3),
    (1, 5), (2, 4), (1, 6),
]
TL = float(sys.argv[1]) if len(sys.argv) > 1 else 120.0

print(f"{'k':>2} {'n':>2} | {'|V|':>4} {'d':>3} {'p':>4} | "
      f"{'LB_W':>6} {'UB':>5} | {'rn':>5} {'M':>5} | {'time':>6} {'proven':>7}")
print("-" * 74)
for (k, n) in CASES:
    G, _, _ = build_ssd_ladder(k, n)
    nV, p, d = params(k, n)
    dist = dict(nx.all_pairs_shortest_path_length(G))
    ub, viol = upper_bound_greedy(G, d, dist)
    rn, name, el, proven = exact_rn_cpsat(G, d, ub, dist, TL)
    M = (p * (d + 1) - rn) if rn is not None else None
    print(f"{k:>2} {n:>2} | {nV:>4} {d:>3} {p:>4} | "
          f"{lower_bound_W(k, n):>6} {ub:>5} | {str(rn):>5} {str(M):>5} | "
          f"{el:>5.1f}s {str(proven):>7}  [{name}]", flush=True)
