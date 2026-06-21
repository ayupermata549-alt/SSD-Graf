"""
resolve_n5.py — EKSPERIMEN PENENTU: apakah konjektur benar utk n>=5?

Minimkan span SSD_1(L_n) dgn batas atas = incumbent terbaik (longgar, bukan
nilai formula), waktu panjang, banyak worker. Tanpa kendala tambahan yg
menghambat (tak ada paku zmin / batas S bawah ketat).

  - kalau span turun ke nilai formula  -> konjektur BERTAHAN
  - kalau terbukti optimal > formula    -> konjektur SALAH utk n itu
  - kalau optimal = formula             -> rn = formula TERBUKTI utk n itu
"""
import sys, os, time
sys.path.insert(0, os.getcwd())
import networkx as nx
from ortools.sat.python import cp_model
from supersubdivision_graf_algorithm import build_ssd_ladder
from lower_bound_ladder import params


def rn_conj(k, n):
    return k * (7 * n - 2) * (n - 1) // 2 + (n * n + 2 * n - 1)


def solve(k, n, ub, tl, workers=12):
    G, _, _ = build_ssd_ladder(k, n)
    nV, p, d = params(k, n)
    dist = dict(nx.all_pairs_shortest_path_length(G))
    nodes = list(G.nodes())
    m = cp_model.CpModel()
    f = {v: m.NewIntVar(0, ub, f"f_{i}") for i, v in enumerate(nodes)}
    S = m.NewIntVar(0, ub, "S")
    for v in nodes:
        m.Add(S >= f[v])
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
    s.parameters.num_search_workers = workers
    t0 = time.time(); st = s.Solve(m); el = time.time() - t0
    val = int(s.ObjectiveValue()) if st in (cp_model.OPTIMAL,
                                            cp_model.FEASIBLE) else None
    bound = int(s.BestObjectiveBound())
    return nV, d, p, val, bound, s.StatusName(st), el, st == cp_model.OPTIMAL


# (k, n, ub_incumbent_longgar, time_limit)
CASES = [(1, 5, 102, 600), (1, 6, 154, 600)]
if len(sys.argv) > 1:
    # python resolve_n5.py k,n,ub,tl ...
    CASES = [tuple(map(int, a.split(","))) for a in sys.argv[1:]]

print(f"{'k':>2} {'n':>2} | {'|V|':>4} {'formula':>7} {'ub0':>4} | "
      f"{'span':>4} {'bound':>5} | {'proven':>6} {'time':>6}  status")
print("-" * 72)
for c in CASES:
    k, n, ub, tl = c
    fc = rn_conj(k, n)
    nV, d, p, val, bnd, name, el, proven = solve(k, n, ub, tl)
    print(f"{k:>2} {n:>2} | {nV:>4} {fc:>7} {ub:>4} | "
          f"{str(val):>4} {bnd:>5} | {str(proven):>6} {el:>5.0f}s  [{name}]",
          flush=True)
