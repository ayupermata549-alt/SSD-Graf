"""
test_levelbound.py — uji rumus batas bawah berbasis level:

    rn(G) >= (p-1)(d-k+1) + delta - 2 * sum_{i=0}^{h} |L_i| * i

dengan L_0 subgraf pusat, L_i = {v : dist(v,L_0)=i}, k=diam(L_0),
delta=0 bila |L_0|>=2, delta=1 bila |L_0|=1, h=level maksimum,
d=diam(G). Di sini p diuji = |V| (jadi suku pertama (|V|-1)(d-k+1)).

sum |L_i|*i = sum_v dist(v, L_0)  (jumlah jarak ke himpunan pusat).

Dibandingkan ke rn EKSAK/incumbent yg sudah diketahui. Kalau bound > rn,
rumus (sebagaimana diterapkan) SALAH; kalau <= rn, valid (dan kita lihat
ketajamannya). Diuji utk beberapa pilihan L_0.
"""
import sys, os
sys.path.insert(0, os.getcwd())
import networkx as nx
from supersubdivision_graf_algorithm import build_ssd_ladder, graph_center
from lower_bound_ladder import params

# rn yang sudah diketahui (eksak/terbukti = *, sisanya incumbent=batas atas)
KNOWN = {
    (1, 2): 13, (2, 2): 19, (1, 3): 33,            # * terbukti optimal
    (3, 2): 25, (4, 2): 31, (2, 3): 52, (1, 4): 62,
    (3, 3): 71, (2, 4): 101, (1, 5): 102, (1, 6): 154,
}
PROVEN = {(1, 2), (2, 2), (1, 3)}


def level_bound(G, L0):
    nV = G.number_of_nodes()
    d = nx.diameter(G)
    # jarak tiap titik ke himpunan L0
    msp = dict(nx.all_pairs_shortest_path_length(G))
    distL0 = {v: min(msp[v][c] for c in L0) for v in G}
    h = max(distL0.values())
    sum_iLi = sum(distL0.values())          # = sum_i |L_i|*i
    sub = G.subgraph(L0)
    k = nx.diameter(sub) if nx.is_connected(sub) else None
    delta = 1 if len(L0) == 1 else 0
    if k is None:
        return None, d, None, delta, h, sum_iLi
    p = nV                                   # uji p = |V|
    bound = (p - 1) * (d - k + 1) + delta - 2 * sum_iLi
    return bound, d, k, delta, h, sum_iLi


def L0_choices(G):
    out = {}
    c = graph_center(G)
    out["center"] = list(c)
    out["1center"] = [sorted(c)[0]]
    return out


print(f"{'k_ssd':>5} {'n':>2} | {'rn':>4} {'pf':>2} | {'L0':>8} "
      f"{'|L0|':>4} {'diamL0':>6} {'d':>3} {'sumiLi':>6} | {'bound':>6} "
      f"{'<=rn?':>6} {'gap':>5}")
print("-" * 86)
for (ks, n), rn in KNOWN.items():
    G, _, _ = build_ssd_ladder(ks, n)
    for tag, L0 in L0_choices(G).items():
        b, d, kk, delta, h, s = level_bound(G, L0)
        if b is None:
            print(f"{ks:>5} {n:>2} | {rn:>4} {'*' if (ks,n) in PROVEN else '':>2} "
                  f"| {tag:>8} {len(L0):>4} (L0 tak terhubung)")
            continue
        ok = b <= rn
        flag = "" if ok else "  <-- MELEBIHI rn (SALAH)"
        print(f"{ks:>5} {n:>2} | {rn:>4} {'*' if (ks,n) in PROVEN else '':>2} "
              f"| {tag:>8} {len(L0):>4} {kk:>6} {d:>3} {s:>6} | {b:>6} "
              f"{str(ok):>6} {rn-b:>5}{flag}")
    print()
