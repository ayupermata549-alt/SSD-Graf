"""
max_ham_path.py — hitung M(k,n) = max_{urutan} sum_i d(x_i, x_{i+1})
untuk SSD_k(L_n), yaitu bobot lintasan Hamilton TERBERAT pada metrik jarak.

Kenapa M penting:  rn(G) = p(d+1) - M  (bila urutan pemaksimal M juga
menghasilkan pelabelan yang valid). Jadi menemukan bentuk tertutup M =
menemukan rn eksak untuk SEMUA n.

Metode: ILP MTZ (Miller-Tucker-Zemlin) untuk Hamiltonian path terberat.
Lebih ringan dari ILP radio number, jadi bisa menjangkau n sedikit lebih besar.
"""
import sys, os; sys.path.insert(0, os.getcwd())
import networkx as nx
from supersubdivision_graf_algorithm import build_ssd_ladder
from lower_bound_ladder import params

TIME = 600


def max_ham_path(G, dist, time_limit=TIME):
    import pulp
    nodes = list(G.nodes())
    N = len(nodes)
    idx = {v: i for i, v in enumerate(nodes)}
    prob = pulp.LpProblem("max_ham_path", pulp.LpMaximize)

    x = {}
    for a in nodes:
        for b in nodes:
            if a != b:
                x[a, b] = pulp.LpVariable(f"x_{idx[a]}_{idx[b]}", cat="Binary")
    u = {v: pulp.LpVariable(f"u_{idx[v]}", lowBound=0, upBound=N - 1,
                            cat="Continuous") for v in nodes}

    # bobot = jarak (arah tak penting krn simetris)
    prob += pulp.lpSum(dist[a][b] * x[a, b] for (a, b) in x)

    # tepat N-1 arc terpakai
    prob += pulp.lpSum(x.values()) == N - 1
    for v in nodes:
        prob += pulp.lpSum(x[v, b] for b in nodes if b != v) <= 1   # out <=1
        prob += pulp.lpSum(x[a, v] for a in nodes if a != v) <= 1   # in  <=1
    # tepat 1 start (out=1,in=0) dan 1 end: total out = N-1 sudah memaksa
    # struktur path bila subtour dihilangkan.
    # MTZ subtour elimination
    for a in nodes:
        for b in nodes:
            if a != b:
                prob += u[b] >= u[a] + 1 - N * (1 - x[a, b])

    solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=time_limit)
    prob.solve(solver)
    status = pulp.LpStatus[prob.status]
    val = pulp.value(prob.objective)
    return (int(round(val)) if val is not None else None), status


if __name__ == "__main__":
    cases = sys.argv[1:]
    if cases:
        pairs = [tuple(map(int, c.split(","))) for c in cases]  # "1,5"
    else:
        pairs = [(1, 2), (1, 3), (1, 4), (1, 5)]
    print(f"{'k':>2} {'n':>2} | {'|V|':>4} {'d':>3} {'p':>3} | "
          f"{'M':>5} {'rn=p(d+1)-M':>12} | status")
    print("-" * 60)
    for (k, n) in pairs:
        G, _, _ = build_ssd_ladder(k, n)
        nV, p, d = params(k, n)
        dist = dict(nx.all_pairs_shortest_path_length(G))
        M, st = max_ham_path(G, dist)
        rn = (p * (d + 1) - M) if M is not None else None
        print(f"{k:>2} {n:>2} | {nV:>4} {d:>3} {p:>3} | "
              f"{str(M):>5} {str(rn):>12} | {st}", flush=True)
