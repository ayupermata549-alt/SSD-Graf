"""
order_anneal.py — cari pelabelan radio bagus via local search atas URUTAN titik.

Fakta kunci: untuk urutan x_0..x_p, valid_labeling memberi span minimum yg
konsisten dgn urutan itu, dan MIN atas semua urutan = rn(G) PERSIS. Jadi
menurunkan span lewat pencarian urutan = batas atas rn yg makin tajam; bila
mencapai nilai formula -> pelabelan valid yg membuktikan rn <= formula.

Murah & single-thread (tak saingan dgn CP-SAT). Deterministik (seed via index,
bukan RNG global) supaya hasil bisa diulang.
"""
import sys, os, math
sys.path.insert(0, os.getcwd())
import networkx as nx
from supersubdivision_graf_algorithm import build_ssd_ladder, greedy_ordering
from lower_bound_ladder import params


def rn_conj(k, n):
    return k * (7 * n - 2) * (n - 1) // 2 + (n * n + 2 * n - 1)


def span_of_order(order, d, dist):
    """valid_labeling span: tiap label menghormati SEMUA titik sebelumnya."""
    labels = {order[0]: 0}
    placed = [order[0]]
    best = 0
    for v in order[1:]:
        lo = 0
        dv = dist[v]
        for u in placed:
            cand = labels[u] + d + 1 - dv[u]
            if cand > lo:
                lo = cand
        labels[v] = lo
        placed.append(v)
        if lo > best:
            best = lo
    return best


# LCG deterministik (hindari Math.random/global RNG utk reprodusibilitas)
class LCG:
    def __init__(self, seed):
        self.s = seed & 0xFFFFFFFF

    def next(self):
        self.s = (1103515245 * self.s + 12345) & 0x7FFFFFFF
        return self.s

    def randint(self, n):
        return self.next() % n

    def rand(self):
        return self.next() / 0x7FFFFFFF


def _move(cur, rng, N):
    """Hasilkan tetangga + fungsi pembalik. 3 jenis: swap, insertion, reverse."""
    t = rng.randint(3)
    if t == 0:  # swap dua posisi
        i, j = rng.randint(N), rng.randint(N)
        cur[i], cur[j] = cur[j], cur[i]
        return lambda: _swap(cur, i, j)
    if t == 1:  # insertion: cabut i, sisipkan di j
        i = rng.randint(N)
        v = cur.pop(i)
        j = rng.randint(N)
        cur.insert(j, v)
        return lambda: (_undo_insert(cur, j, i))
    # reverse segmen [i..j]
    i, j = sorted((rng.randint(N), rng.randint(N)))
    cur[i:j + 1] = cur[i:j + 1][::-1]
    return lambda: cur.__setitem__(slice(i, j + 1), cur[i:j + 1][::-1])


def _swap(cur, i, j):
    cur[i], cur[j] = cur[j], cur[i]


def _undo_insert(cur, j, i):
    v = cur.pop(j)
    cur.insert(i, v)


def anneal(G, d, dist, iters, seed=12345, restarts=8):
    nodes = list(G.nodes())
    N = len(nodes)
    best_order = greedy_ordering(G)
    best_span = span_of_order(best_order, d, dist)
    for r in range(restarts):
        rng = LCG(seed + 7919 * r)
        if r == 0:
            cur = list(best_order)
        else:
            cur = list(best_order)  # mulai dari yg terbaik sejauh ini (re-anneal)
            for _ in range(N):       # acak ringan
                i, j = rng.randint(N), rng.randint(N)
                cur[i], cur[j] = cur[j], cur[i]
        cur_span = span_of_order(cur, d, dist)
        T0, T1 = 8.0, 0.01
        for it in range(iters):
            T = T0 * (T1 / T0) ** (it / max(iters - 1, 1))
            undo = _move(cur, rng, N)
            new_span = span_of_order(cur, d, dist)
            dE = new_span - cur_span
            if dE <= 0 or rng.rand() < math.exp(-dE / T):
                cur_span = new_span
                if cur_span < best_span:
                    best_span = cur_span
                    best_order = list(cur)
            else:
                undo()
    return best_span, best_order


def run(k, n, iters):
    G, _, _ = build_ssd_ladder(k, n)
    nV, p, d = params(k, n)
    dist = dict(nx.all_pairs_shortest_path_length(G))
    span, order = anneal(G, d, dist, iters)
    fc = rn_conj(k, n)
    rel = "= formula" if span == fc else (f"> formula by {span-fc}"
                                          if span > fc else
                                          f"< formula by {fc-span} (!!)")
    print(f"k={k} n={n} |V|={nV} d={d} | best_span={span}  formula={fc}  [{rel}]",
          flush=True)
    return span, order, fc


if __name__ == "__main__":
    ITERS = int(os.environ.get("ANNEAL_ITERS", "40000"))
    if len(sys.argv) > 1:
        pairs = [tuple(map(int, a.split(","))) for a in sys.argv[1:]]
    else:
        pairs = [(1, 2), (2, 2), (1, 3), (2, 3), (1, 4), (1, 5)]
    for (k, n) in pairs:
        run(k, n, ITERS)
