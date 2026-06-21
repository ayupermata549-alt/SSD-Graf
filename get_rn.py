"""Kumpulkan rn eksak (ILP) untuk beberapa (k,n) kecil sbg ground-truth M.
M = p(d+1) - rn. Dijalankan dengan time limit longgar."""
import sys, os; sys.path.insert(0, os.getcwd())
import networkx as nx
from supersubdivision_graf_algorithm import build_ssd_ladder
from radio_bounds import upper_bound_greedy, radio_number_exact
from lower_bound_ladder import params, lower_bound_W

CASES = [(3,2),(2,2),(2,3),(1,5)]  # urut dari termudah (|V| kecil)
TIME = 1500

import radio_bounds as rb
rb.ILP_TIME_LIMIT = TIME

for (k,n) in CASES:
    G,_,_ = build_ssd_ladder(k,n)
    nV,p,d = params(k,n)
    dist = dict(nx.all_pairs_shortest_path_length(G))
    ub,viol = upper_bound_greedy(G,d,dist)
    ex,st = radio_number_exact(G,d,ub,dist)
    M = (p*(d+1)-ex) if ex else None
    print(f"k={k} n={n} |V|={nV} d={d} p={p} | UB={ub} LB_W={lower_bound_W(k,n)} "
          f"| rn={ex} [{st}] | M={M}", flush=True)
