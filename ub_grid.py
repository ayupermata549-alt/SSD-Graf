"""
ub_grid.py — batas atas terstruktur (greedy + valid_labeling) untuk grid
(k,n) yang luas, plus LB_W. Murah dihitung; dipakai untuk menebak pola rn.

Greedy-UB di sini sudah TERBUKTI menyamai ILP untuk SSD_1(L_2). Kalau pola
UB rapi dan cocok dgn semua ILP kecil, ia jadi kandidat kuat rumus rn.
"""
import sys, os
sys.path.insert(0, os.getcwd())
import networkx as nx
from supersubdivision_graf_algorithm import build_ssd_ladder
from lower_bound_ladder import params, lower_bound_W
from radio_bounds import upper_bound_greedy

KS = [1, 2, 3, 4]
NS = list(range(2, 13))

print(f"{'k':>2} {'n':>2} | {'|V|':>4} {'d':>3} {'p':>4} | "
      f"{'LB_W':>6} {'UB':>6} | {'UB-LB':>6}")
print("-" * 56)
for k in KS:
    for n in NS:
        G, _, _ = build_ssd_ladder(k, n)
        nV, p, d = params(k, n)
        dist = dict(nx.all_pairs_shortest_path_length(G))
        ub, viol = upper_bound_greedy(G, d, dist)
        lb = lower_bound_W(k, n)
        assert viol == 0
        print(f"{k:>2} {n:>2} | {nV:>4} {d:>3} {p:>4} | "
              f"{lb:>6} {ub:>6} | {ub - lb:>6}", flush=True)
    print()
