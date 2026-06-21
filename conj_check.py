"""conj_check.py — cek konjektur rn(k,n) = k(7n-2)(n-1)/2 + (n^2+2n-1)
terhadap nilai eksak/incumbent CP-SAT."""

def rn_conj(k, n):
    assert (k * (7 * n - 2) * (n - 1)) % 2 == 0
    return k * (7 * n - 2) * (n - 1) // 2 + (n * n + 2 * n - 1)

# (k, n, nilai_CPSAT, terbukti_optimal?)
DATA = [
    (1, 2, 13, True),
    (2, 2, 19, True),
    (1, 3, 33, True),
    (3, 2, 25, False),
    (4, 2, 31, False),
    (2, 3, 52, False),
    (1, 4, 62, False),
    (3, 3, 71, False),
    (2, 4, 101, False),
    (1, 5, 102, False),   # incumbent (UB), belum optimal
    (1, 6, 154, False),   # incumbent (UB), belum optimal
]

print(f"{'k':>2} {'n':>2} | {'CP-SAT':>6} {'konj':>5} | {'sama?':>6} "
      f"{'status':>10}")
print("-" * 44)
for (k, n, val, proven) in DATA:
    c = rn_conj(k, n)
    rel = "EXACT" if val == c else ("UB>=konj" if val >= c else "**KONJ SALAH**")
    print(f"{k:>2} {n:>2} | {val:>6} {c:>5} | {str(val==c):>6} "
          f"{('optimal' if proven else 'incumbent'):>10}  {rel}")
