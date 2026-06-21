"""
radio_bounds.py — bukti eksak rn(G) untuk SSD_k(L_n) dan SSD_k(D_{m,n}).

Untuk setiap graf, menghitung empat angka yang dipakai mengapit rn(G):

    |V|, d        : jumlah titik dan diameter (parameter dasar)
    LB_center     : batas BAWAH dari metode gap+center
                        rn(G) >= (|V|-1)(d+1) - 2W + (L(x0)+L(xp))
                    dengan W = sum_v d(v, c),  L(v) = d(v, c),  c = center.
    UB_greedy     : batas ATAS dari pelabelan greedy (span sebuah radio
                    labeling yang valid; sama mesin dgn UI Anda).
    rn_exact      : nilai EKSAK via ILP (PuLP/CBC) — hanya untuk |V| kecil.

Kalau LB_center == UB_greedy == rn_exact, ketiganya saling mengunci dan
rn(G) terbukti eksak untuk kasus itu. Tujuan tabel ini: melihat polanya
sehingga bentuk tertutup rn(G) bisa ditebak lalu dibuktikan.

Jalankan:
    python radio_bounds.py                 # tabel default (kasus kecil)
    python radio_bounds.py L 2 4           # satu graf SSD_2(L_4), pakai ILP
    python radio_bounds.py D 1 3 2         # satu graf SSD_1(D_{3,2})
    python radio_bounds.py L 3 8 --no-ilp  # lewati ILP (graf besar)
"""

import sys
import networkx as nx

from supersubdivision_graf_algorithm import (
    build_ssd_ladder, build_ssd_prism,
    graph_center, greedy_ordering, verify_radio,
)
from lower_bound_ladder import lower_bound_level_G

# ILP eksak hanya dijalankan kalau |V| <= ini (di atas ini terlalu lambat).
ILP_MAX_V = 24
ILP_TIME_LIMIT = 120  # detik per graf


# ----------------------------------------------------------------------
# Batas bawah (gap + center)
# ----------------------------------------------------------------------

def lower_bound_center(G):
    """Batas bawah berbasis level (dekomposisi dari subgraf pusat L0):

        rn(G) >= (|V|-1)(d - k + 1) + delta - 2 * sum_v dist(v, L0)

    dengan k=diam(L0), delta=1 bila |L0|=1 (selain itu 0). Diambil L0 terhubung
    yang menghasilkan batas TERTAJAM (lihat lower_bound_level_G). Bila L0 satu
    titik median, rumus menjadi (|V|-1)(d+1)+1-2W: versi p(d+1)-2W + koreksi
    endpoint. Mengembalikan (LB, d, W_L0, L0_repr) agar kompatibel dgn report().
    """
    d = nx.diameter(G)
    lb, L0 = lower_bound_level_G(G, return_best=True)
    msp = dict(nx.all_pairs_shortest_path_length(G))
    W = sum(min(msp[v][c] for c in L0) for v in G)   # sum_v dist(v, L0)
    return lb, d, W, sorted(L0)[0]


# ----------------------------------------------------------------------
# Batas atas (pelabelan greedy yang valid)
# ----------------------------------------------------------------------

def valid_labeling(G, order, d, dist):
    """Pelabelan radio yang DIJAMIN valid untuk urutan apa pun.

    Tiap label baru menghormati SEMUA titik yang sudah dipasang, bukan hanya
    titik sebelumnya:
        phi(x_{i+1}) = max_{j<=i} [ phi(x_j) + d + 1 - dist(x_j, x_{i+1}) ].
    Karena setiap selisih >= d+1-dist, seluruh kondisi radio terpenuhi.
    """
    labels = {order[0]: 0}
    placed = [order[0]]
    for v in order[1:]:
        lo = 0
        for u in placed:
            lo = max(lo, labels[u] + d + 1 - dist[u][v])
        labels[v] = lo
        placed.append(v)
    return labels


def upper_bound_greedy(G, d, dist):
    """Batas atas valid: pakai greedy ordering + valid_labeling."""
    order = greedy_ordering(G)
    labels = valid_labeling(G, order, d, dist)
    span = max(labels.values())
    violations = verify_radio(G, labels, d)  # harus 0
    return span, len(violations)


# ----------------------------------------------------------------------
# Nilai eksak (ILP)
# ----------------------------------------------------------------------

def radio_number_exact(G, d, ub, dist):
    """rn(G) eksak via ILP. Mengembalikan (nilai, status_string).

    Variabel f_v in [0, ub] integer; span S diminimalkan; untuk tiap pasang
    {u,v}:  |f_u - f_v| >= d+1-dist(u,v), dilinearkan dgn biner y_uv.
    ub HARUS batas atas valid (>= rn) agar ILP tidak palsu-infeasible.
    """
    try:
        import pulp
        import time as _time
    except ImportError:
        return None, "pulp tidak terpasang"

    nodes = list(G.nodes())
    # big-M: kendala "off" berbentuk  f[u]-f[w] >= need - M, dan f[u]-f[w] bisa
    # serendah -ub. Jadi perlu need - M <= -ub  =>  M >= ub + need. need<=d+1.
    M = ub + d + 1

    prob = pulp.LpProblem("radio_number", pulp.LpMinimize)
    f = {v: pulp.LpVariable(f"f_{i}", lowBound=0, upBound=ub, cat="Integer")
         for i, v in enumerate(nodes)}
    S = pulp.LpVariable("S", lowBound=0, upBound=ub, cat="Integer")
    prob += S
    for v in nodes:
        prob += S >= f[v]
    # Catatan: JANGAN paku f[nodes[0]]=0 — titik berlabel 0 belum tentu nodes[0];
    # itu over-constraint dan bikin palsu-infeasible. min(f)=0 muncul sendiri
    # karena S diminimalkan (kalau semua f>0, geser turun mengecilkan S).

    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            u, w = nodes[i], nodes[j]
            need = d + 1 - dist[u][w]
            y = pulp.LpVariable(f"y_{i}_{j}", cat="Binary")
            prob += f[u] - f[w] >= need - M * (1 - y)
            prob += f[w] - f[u] >= need - M * y

    solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=ILP_TIME_LIMIT)
    _t0 = _time.time()
    prob.solve(solver)
    elapsed = _time.time() - _t0
    status = pulp.LpStatus[prob.status]
    val = int(round(pulp.value(S))) if pulp.value(S) is not None else None
    # PENTING: CBC sering kehabisan waktu lalu mengembalikan solusi SEMENTARA
    # yang TETAP dilabeli "Optimal" oleh pulp. Jadi optimalitas hanya bisa
    # dipercaya kalau solusi selesai jauh sebelum batas waktu. Kalau tidak,
    # nilai ini hanyalah batas ATAS (incumbent), bukan rn eksak.
    if status == "Optimal" and elapsed >= 0.9 * ILP_TIME_LIMIT:
        status = f"INCUMBENT(timeout {elapsed:.0f}s, NOT proven)"
    return val, status


# ----------------------------------------------------------------------
# Satu graf -> satu baris hasil
# ----------------------------------------------------------------------

def report(G, name, use_ilp=True):
    lb, d, W, c = lower_bound_center(G)
    dist = dict(nx.all_pairs_shortest_path_length(G))
    ub, viol = upper_bound_greedy(G, d, dist)
    nV = G.number_of_nodes()

    ex, st = None, "-"
    if use_ilp and nV <= ILP_MAX_V:
        ex, st = radio_number_exact(G, d, ub, dist)
    elif use_ilp:
        st = f"skip(|V|>{ILP_MAX_V})"

    tight = (ex is not None and ex == lb == ub)
    flag = "  <== EKSAK & terbukti (LB=UB=ILP)" if tight else ""
    ex_str = "-" if ex is None else str(ex)
    print(f"{name:14s} |V|={nV:4d} d={d:3d} W={W:5d} "
          f"| LB={lb:6d}  UB={ub:6d}{'' if viol==0 else '(INVALID)'}  "
          f"rn={ex_str:>6s} [{st}]{flag}")


def header():
    print(f"{'graf':14s} {'':4s}{'':6s}{'':8s} "
          f"| {'LB_center':>9s} {'UB_greedy':>9s} {'rn_exact':>10s}")
    print("-" * 92)


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

def run_single(argv):
    use_ilp = "--no-ilp" not in argv
    argv = [a for a in argv if a != "--no-ilp"]
    head = argv[0].upper()
    header()
    if head == "L":
        k, n = int(argv[1]), int(argv[2])
        G, _, _ = build_ssd_ladder(k, n)
        report(G, f"L k={k} n={n}", use_ilp)
    elif head == "D":
        k, m, n = int(argv[1]), int(argv[2]), int(argv[3])
        G, _, _ = build_ssd_prism(k, m, n)
        report(G, f"D k={k} m={m},n={n}", use_ilp)
    else:
        print("usage: python radio_bounds.py [L k n | D k m n] [--no-ilp]")


def run_table():
    print("Bandingkan batas bawah (LB), batas atas (UB), dan nilai eksak (rn).")
    print("Bila LB = UB = rn pada satu baris, rn(G) untuk kasus itu sudah eksak.\n")
    header()
    print("=== SSD_k(L_n)  ladder ===")
    for k in (1, 2, 3):
        for n in (2, 3, 4):
            G, _, _ = build_ssd_ladder(k, n)
            report(G, f"L k={k} n={n}")
    print("\n=== SSD_k(D_m,n)  prism ===")
    for (k, m, n) in [(1, 3, 2), (1, 3, 3), (1, 4, 2), (2, 3, 2)]:
        G, _, _ = build_ssd_prism(k, m, n)
        report(G, f"D k={k} m={m},n={n}")
    print("\nCatatan: LB_center mentah sering < rn (belum dipertajam paritas/"
          "endpoint).\nUB_greedy hanya satu heuristik — rn_exact (ILP) "
          "adalah patokan kebenarannya.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_single(sys.argv[1:])
    else:
        run_table()
