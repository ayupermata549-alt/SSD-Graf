"""
lower_bound_ladder.py — bentuk tertutup untuk SSD_k(L_n), diturunkan aljabar
dan diverifikasi terhadap graf sebenarnya.

Yang diturunkan
---------------
1.  Metrik (jarak) SSD_k(L_n) dari jarak ladder L_n.
2.  Diameter        d(k,n) = 2n.
3.  Jumlah titik     |V|   = 2n + k(3n-2),     p = |V| - 1.
4.  Median c = u_q,  q = ceil(n/2)  (titik peminimal jumlah jarak).
5.  W(k,n) = sum_v d(v, c)  -- BENTUK TERTUTUP (lihat W_closed).
6.  LB_W = p(d+1) - 2W      -- batas bawah valid (TAPI belum tajam).

Turunan W
---------
Tulis q = ceil(n/2). Definisikan
    S1 = sum_{i=1..n}   |i-q|
    S2 = sum_{i=1..n-1} min(|i-q|, |i+1-q|)
Dengan jarak:
    d(u_i,c) = 2|i-q|              d(v_i,c) = 2|i-q|+2
    d(wh_i*,c) = 1 + 2 min_i       (sub rel atas, i & i+1 di rel atas)
    d(wb_i*,c) = 3 + 2 min_i       (sub rel bawah; +2 karena rel bawah)
    d(wv_i*,c) = 1 + 2|i-q|        (sub anak-tangga)
maka
    W = 4 S1 + 2n + k(2 S1 + 4 S2 + 5n - 4).
Dengan S1, S2 dalam bentuk tertutup (genap/ganjil) diperoleh W_closed.
"""

import sys
import networkx as nx
from supersubdivision_graf_algorithm import build_ssd_ladder, graph_center


# ----------------------------------------------------------------------
# Bentuk tertutup
# ----------------------------------------------------------------------

def params(k, n):
    """|V|, p, diameter."""
    nV = 2 * n + k * (3 * n - 2)
    return nV, nV - 1, 2 * n


def S1_S2(n):
    """S1 = sum |i-q|,  S2 = sum min(|i-q|,|i+1-q|), dengan q = ceil(n/2)."""
    q = (n + 1) // 2  # ceil(n/2)
    S1 = (q - 1) * q // 2 + (n - q) * (n - q + 1) // 2
    S2 = (q - 2) * (q - 1) // 2 + (n - q - 1) * (n - q) // 2
    return S1, S2


def W_general(k, n):
    """W lewat S1,S2 (berlaku untuk q = ceil(n/2))."""
    S1, S2 = S1_S2(n)
    return 4 * S1 + 2 * n + k * (2 * S1 + 4 * S2 + 5 * n - 4)


def W_closed(k, n):
    """W dalam t = floor(n/2), dipisah paritas n (hasil akhir yang rapi).

        n = 2t   :  W = 4t(t+1) + 2k t(3t+1)
        n = 2t+1 :  W = 4t^2+8t+2 + k(6t^2+8t+1)
    """
    t = n // 2
    if n % 2 == 0:
        return 4 * t * (t + 1) + 2 * k * t * (3 * t + 1)
    else:
        return (4 * t * t + 8 * t + 2) + k * (6 * t * t + 8 * t + 1)


def lower_bound_W(k, n):
    """Batas bawah valid (belum tajam):  rn >= p(d+1) - 2W."""
    nV, p, d = params(k, n)
    return p * (d + 1) - 2 * W_closed(k, n)


# ----------------------------------------------------------------------
# Batas bawah berbasis level (dekomposisi dari subgraf pusat L0)
# ----------------------------------------------------------------------
#
#   rn(G) >= (|V|-1)(d - k + 1) + delta - 2 * sum_{i=0}^{h} |L_i| * i
#
# dengan  L0    = subgraf pusat (HARUS terhubung),
#         L_i   = { v : dist(v, L0) = i },
#         k     = diam(L0),
#         d     = diam(G),
#         delta = 1 bila |L0| = 1, selain itu 0,
#         sum_i |L_i| * i = sum_v dist(v, L0)  (jumlah jarak ke pusat).
#
# Bila L0 = satu titik pusat c: k=0, delta=1, dan rumus menjadi
#   (|V|-1)(d+1) + 1 - 2W  =  [p(d+1) - 2W] + 1  (versi lama + koreksi endpoint).

def _level_bound_for(G, L0):
    """Nilai formula level untuk satu pilihan L0; None bila L0 tak terhubung."""
    sub = G.subgraph(L0)
    if not nx.is_connected(sub):
        return None
    nV = G.number_of_nodes()
    d = nx.diameter(G)
    k0 = nx.diameter(sub)                      # k = diam(L0)
    delta = 1 if len(L0) == 1 else 0
    msp = dict(nx.all_pairs_shortest_path_length(G))
    sum_iLi = sum(min(msp[v][c] for c in L0)   # = sum_i |L_i| * i
                  for v in G)
    return (nV - 1) * (d - k0 + 1) + delta - 2 * sum_iLi


def lower_bound_level_G(G, return_best=False):
    """Batas bawah berbasis level untuk SEBARANG graf G (ladder/prisma/...).

    Setiap L0 terhubung memberi pertidaksamaan VALID, jadi kita ambil yang
    TERTAJAM (maksimum) atas beberapa kandidat L0 terhubung:
        - seluruh himpunan center (bila terhubung),
        - tiap satu titik center,
        - tiap satu titik MEDIAN (jumlah-jarak minimum) -> memaksimalkan rumus,
          karena suku -2*sum_v dist(v,L0) terkecil saat L0 = median.

    return_best=True -> kembalikan (nilai, L0_terpilih); selain itu nilai saja.
    """
    msp = dict(nx.all_pairs_shortest_path_length(G))
    totdist = {v: sum(msp[v].values()) for v in G}
    Wmin = min(totdist.values())
    median = [v for v in G if totdist[v] == Wmin]   # titik peminimal jumlah jarak
    center = graph_center(G)
    candidates = [list(center)] + [[c] for c in center] + [[m] for m in median]
    best_val, best_L0 = None, None
    for L0 in candidates:
        b = _level_bound_for(G, L0)
        if b is not None and (best_val is None or b > best_val):
            best_val, best_L0 = b, L0
    return (best_val, best_L0) if return_best else best_val


def lower_bound_level(k, n):
    """Batas bawah berbasis level untuk SSD_k(L_n) (lihat lower_bound_level_G)."""
    G, _, _ = build_ssd_ladder(k, n)
    return lower_bound_level_G(G)


# ----------------------------------------------------------------------
# Verifikasi terhadap graf nyata
# ----------------------------------------------------------------------

def verify(k, n):
    G, _, _ = build_ssd_ladder(k, n)
    nV, p, d = params(k, n)
    assert G.number_of_nodes() == nV, (G.number_of_nodes(), nV)
    assert nx.diameter(G) == d, (nx.diameter(G), d)
    # W sebenarnya = jumlah jarak minimum (median)
    spall = dict(nx.all_pairs_shortest_path_length(G))
    Wmed = min(sum(spall[v].values()) for v in G)
    ok = (W_general(k, n) == Wmed == W_closed(k, n))
    return nV, p, d, Wmed, W_closed(k, n), W_general(k, n), ok


if __name__ == "__main__":
    print(f"{'k':>2} {'n':>2} | {'|V|':>4} {'p':>3} {'d':>3} "
          f"| {'W_graf':>6} {'cocok':>5} "
          f"| {'LB_W':>6} {'LB_level':>8}")
    print("-" * 64)
    allok = True
    for k in (1, 2, 3, 4):
        for n in range(2, 11):
            nV, p, d, Wg, Wc, Wgen, ok = verify(k, n)
            allok &= ok
            print(f"{k:>2} {n:>2} | {nV:>4} {p:>3} {d:>3} "
                  f"| {Wg:>6} {str(ok):>5} "
                  f"| {lower_bound_W(k, n):>6} {lower_bound_level(k, n):>8}")
    print("-" * 64)
    print("SEMUA bentuk tertutup cocok dgn graf:", allok)
    print("LB_W     = p(d+1) - 2W                     (versi lama)")
    print("LB_level = (|V|-1)(d-k+1) + delta - 2*sum_v dist(v,L0)  (formula level)")
