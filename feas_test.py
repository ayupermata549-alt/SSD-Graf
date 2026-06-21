"""feas_test.py — uji batas ATAS konjektur: untuk tiap (k,n) set ub = formula,
minimkan S. Kalau CP-SAT menemukan pelabelan valid dgn span <= formula, maka
rn(k,n) <= formula TERBUKTI utk kasus itu (membaiki incumbent yg lebih tinggi).
Kalau span == formula DAN proven optimal, rn = formula utk kasus itu.
"""
import sys, os, time
sys.path.insert(0, os.getcwd())
import networkx as nx
from ortools.sat.python import cp_model
from supersubdivision_graf_algorithm import build_ssd_ladder
from lower_bound_ladder import params, lower_bound_W


def rn_conj(k, n):
    return k * (7 * n - 2) * (n - 1) // 2 + (n * n + 2 * n - 1)


def solve(k, n, tl):
    G, _, _ = build_ssd_ladder(k, n)
    nV, p, d = params(k, n)
    dist = dict(nx.all_pairs_shortest_path_length(G))
    nodes = list(G.nodes())
    ub = rn_conj(k, n)
    lb = lower_bound_W(k, n)
    m = cp_model.CpModel()
    f = {v: m.NewIntVar(0, ub, f"f_{i}") for i, v in enumerate(nodes)}
    S = m.NewIntVar(max(lb, 0), ub, "S")
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
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = tl
    s.parameters.num_search_workers = 8
    t0 = time.time(); st = s.Solve(m); el = time.time() - t0
    val = int(s.ObjectiveValue()) if st in (cp_model.OPTIMAL,
                                            cp_model.FEASIBLE) else None
    return nV, d, p, ub, val, s.StatusName(st), el, st == cp_model.OPTIMAL


CASES = [(1, 5), (1, 6), (1, 7), (2, 5), (3, 4)]
if len(sys.argv) > 1:
    CASES = [tuple(map(int, a.split(","))) for a in sys.argv[1:]]
TL = 120.0

print(f"{'k':>2} {'n':>2} | {'|V|':>4} {'formula':>7} | {'span':>5} | "
      f"{'<=form?':>7} {'proven':>7} {'time':>6}  status")
print("-" * 70)
for (k, n) in CASES:
    nV, d, p, ub, val, name, el, proven = solve(k, n, TL)
    le = "YES" if (val is not None and val <= ub) else "NO/none"
    print(f"{k:>2} {n:>2} | {nV:>4} {ub:>7} | {str(val):>5} | "
          f"{le:>7} {str(proven):>7} {el:>5.0f}s  [{name}]", flush=True)
