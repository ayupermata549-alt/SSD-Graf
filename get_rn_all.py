"""
get_rn_all.py — kumpulkan rn EKSAK (ILP) untuk semua SSD_k(L_n) yang layak
dihitung (|V| kecil), dengan verifikasi optimalitas yang jujur.

Untuk tiap kasus dicetak:
    |V|, d, p, LB_W (=p(d+1)-2W),  UB_greedy,  M (=p(d+1)-rn),  rn,  status

Status "TRUSTED OPTIMAL" hanya bila CBC selesai < 90% time-limit. Kalau timeout,
nilai hanya batas atas (incumbent), BUKAN rn terbukti.
"""
import sys, os, time
sys.path.insert(0, os.getcwd())
import networkx as nx
import pulp
from supersubdivision_graf_algorithm import build_ssd_ladder
from lower_bound_ladder import params, lower_bound_W
from radio_bounds import upper_bound_greedy


def exact_rn(G, d, ub, dist, tl):
    nodes = list(G.nodes())
    M = ub + d + 1
    prob = pulp.LpProblem("rn", pulp.LpMinimize)
    f = {v: pulp.LpVariable(f"f{i}", 0, ub, cat="Integer")
         for i, v in enumerate(nodes)}
    S = pulp.LpVariable("S", 0, ub, cat="Integer")
    prob += S
    for v in nodes:
        prob += S >= f[v]
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            u, w = nodes[i], nodes[j]
            need = d + 1 - dist[u][w]
            y = pulp.LpVariable(f"y{i}_{j}", cat="Binary")
            prob += f[u] - f[w] >= need - M * (1 - y)
            prob += f[w] - f[u] >= need - M * y
    t0 = time.time()
    prob.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=tl))
    el = time.time() - t0
    st = pulp.LpStatus[prob.status]
    val = int(round(pulp.value(S))) if pulp.value(S) is not None else None
    trusted = (st == "Optimal" and el < 0.9 * tl)
    return val, st, el, trusted


# (k, n, time_limit_detik) — urut dari |V| terkecil
CASES = [
    (1, 2, 60),
    (2, 2, 120),
    (1, 3, 300),
    (3, 2, 300),
    (1, 4, 600),
    (4, 2, 600),
    (2, 3, 900),
    (1, 5, 1200),
]

print(f"{'k':>2} {'n':>2} | {'|V|':>4} {'d':>3} {'p':>4} | "
      f"{'LB_W':>5} {'UB':>5} | {'rn':>5} {'M':>4} | {'time':>6} {'status':>16}")
print("-" * 78)
for (k, n, tl) in CASES:
    G, _, _ = build_ssd_ladder(k, n)
    nV, p, d = params(k, n)
    dist = dict(nx.all_pairs_shortest_path_length(G))
    ub, viol = upper_bound_greedy(G, d, dist)
    rn, st, el, trusted = exact_rn(G, d, ub, dist, tl)
    M = (p * (d + 1) - rn) if rn is not None else None
    tag = "TRUSTED OPTIMAL" if trusted else "incumbent(UB)"
    print(f"{k:>2} {n:>2} | {nV:>4} {d:>3} {p:>4} | "
          f"{lower_bound_W(k, n):>5} {ub:>5} | {str(rn):>5} {str(M):>4} | "
          f"{el:>5.0f}s {tag:>16}", flush=True)
print("-" * 78)
