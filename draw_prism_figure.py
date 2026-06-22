"""
draw_prism_figure.py — gambar graf prisma super sub-divisi SSD_k(D_{m,n})
dengan bentuk "rumah/menara" (cabang m == 3) dan PENAMAAN titik sesuai
dokumen umum SSD_k(D_{m,n}):

    V = { u_{i,j}      | 1<=i<=n, 1<=j<=m }            (titik dasar, HITAM)
      U { w^t_{i,j}    | 1<=i<=n,   1<=j<=m, 1<=t<=k } (subdivisi rusuk siklus)
      U { v^t_{i,j}    | 1<=i<=n-1, 1<=j<=m, 1<=t<=k } (subdivisi rusuk tegak)

    E = { u_{i,j} w^t_{i,j},  u_{i,j+1} w^t_{i,j} }     (w^t bagi u_{i,j}-u_{i,j+1})
      U { u_{i,j} v^t_{i,j},  u_{i+1,j} v^t_{i,j} }     (v^t bagi u_{i,j}-u_{i+1,j})

Titik subdivisi (w, v) digambar MAGENTA seperti gambar referensi.
Penamaan memakai pretty() dari supersubdivision_ui (yang sudah memetakan
key internal p_/wc_/wr_ ke u_{i,j}/w^t_{i,j}/v^t_{i,j}).

Jalankan:
    python draw_prism_figure.py                 # default: D_{3,2} dan D_{3,3}
    python draw_prism_figure.py 1 3 2 1 3 3     # k m n  k m n  (pasangan)
Output:
    ssd_prism_figure.png
"""
import sys
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from supersubdivision_ui import build_ssd_prism_doc, pretty


BASE_COLOR = "black"
SUB_COLOR = "#e000e0"      # magenta
EDGE_COLOR = "#555555"
BASE_SIZE = 150
SUB_SIZE = 90
EDGE_LW = 2.0
LABEL_FS = 9


def is_base(name: str) -> bool:
    return name.startswith("p_")


def draw_one(ax, k: int, m: int, n: int):
    """Gambar SSD_k(D_{m,n}) berlabel pada Axes ax."""
    G, pos = build_ssd_prism_doc(k, m, n)

    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    cx = sum(xs) / len(xs)
    cy = sum(ys) / len(ys)

    # rusuk (di belakang)
    for u, v in G.edges:
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        ax.plot([x1, x2], [y1, y2], color=EDGE_COLOR, lw=EDGE_LW,
                zorder=1, solid_capstyle="round")

    # titik + label
    for node in G.nodes:
        x, y = pos[node]
        if is_base(node):
            ax.scatter([x], [y], s=BASE_SIZE, c=BASE_COLOR, zorder=3,
                       edgecolors="black", linewidths=0.5)
        else:
            ax.scatter([x], [y], s=SUB_SIZE, c=SUB_COLOR, zorder=4,
                       edgecolors="white", linewidths=0.6)

        # label diletakkan radial keluar dari pusat agar tak bertumpuk
        dx, dy = x - cx, y - cy
        length = math.hypot(dx, dy) or 1.0
        ox, oy = dx / length * 0.55, dy / length * 0.55
        ha = "left" if ox >= 0 else "right"
        va = "bottom" if oy >= 0 else "top"
        ax.text(x + ox, y + oy, pretty(node),
                ha=ha, va=va, fontsize=LABEL_FS, color="#10324f", zorder=5)

    # keterangan di bawah
    ax.text((min(xs) + max(xs)) / 2.0, min(ys) - 1.5,
            fr"$SSD_{{{k}}}(D_{{{m},{n}}})$",
            ha="center", va="top", fontsize=15)

    ax.set_aspect("equal")
    ax.axis("off")
    pad = 1.6
    ax.set_xlim(min(xs) - pad, max(xs) + pad)
    ax.set_ylim(min(ys) - 2.7, max(ys) + pad)


def parse_pairs(args):
    """args = k m n  k m n  ... -> daftar (k, m, n). Default 2 graf."""
    if not args:
        return [(1, 3, 2), (1, 3, 3)]
    if len(args) % 3 != 0:
        print("usage: python draw_prism_figure.py k m n [k m n ...]")
        sys.exit(2)
    vals = list(map(int, args))
    return [tuple(vals[i:i + 3]) for i in range(0, len(vals), 3)]


def main():
    specs = parse_pairs(sys.argv[1:])
    fig, axes = plt.subplots(1, len(specs), figsize=(6.5 * len(specs), 8.5))
    if len(specs) == 1:
        axes = [axes]
    for ax, (k, m, n) in zip(axes, specs):
        draw_one(ax, k, m, n)

    fig.tight_layout()
    out = "ssd_prism_figure.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    print(f"saved: {out}")


if __name__ == "__main__":
    main()
