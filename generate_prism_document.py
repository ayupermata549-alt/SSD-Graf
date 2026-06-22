"""
generate_prism_document.py — hasilkan dokumen PDF berisi gambar graf prisma
super sub-divisi SSD_k(D_{m,n}) dengan gaya seperti dokumen referensi:

    * simpul dasar (p_)        -> titik HITAM
    * simpul subdivisi (wc/wr) -> titik MAGENTA
    * k = 1  -> semua rusuk abu-abu (subdivisi tepat di tengah rusuk)
    * k >= 2 -> rusuk subdivisi MAGENTA dan menyebar (kipas) seperti K_{2,k}
    * tanpa label, hanya keterangan SSD_k(D_{m,n}) di bawah tiap graf

Bentuk:
    m = 3        -> menara segitiga datar
    m = 4        -> kubus / tumpukan kubus (proyeksi miring 3-D)
    m >= 5       -> menara poligon datar (mis. prisma segilima)

Jalankan:
    python generate_prism_document.py            # tata letak default (mirip PDF)
Output:
    ssd_prism_document.pdf
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from supersubdivision_ui import build_ssd_prism_doc


BASE_COLOR = "black"
SUB_COLOR = "#e000e0"        # magenta
GRAY = "#555555"
BASE_SIZE = 70
SUB_SIZE = 55


def is_base(name: str) -> bool:
    return name.startswith("p_")


def draw_one(ax, k: int, m: int, n: int):
    G, pos = build_ssd_prism_doc(k, m, n)

    # rusuk: abu-abu untuk k = 1, magenta untuk k >= 2 (rusuk subdivisi)
    edge_color = GRAY if k == 1 else SUB_COLOR
    edge_lw = 1.8 if k == 1 else 1.5
    for u, v in G.edges:
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        ax.plot([x1, x2], [y1, y2], color=edge_color, lw=edge_lw,
                zorder=1, solid_capstyle="round")

    # titik
    bx = [pos[v][0] for v in G.nodes if is_base(v)]
    by = [pos[v][1] for v in G.nodes if is_base(v)]
    sx = [pos[v][0] for v in G.nodes if not is_base(v)]
    sy = [pos[v][1] for v in G.nodes if not is_base(v)]
    ax.scatter(bx, by, s=BASE_SIZE, c=BASE_COLOR, zorder=3,
               edgecolors="black", linewidths=0.4)
    ax.scatter(sx, sy, s=SUB_SIZE, c=SUB_COLOR, zorder=4,
               edgecolors="white", linewidths=0.5)

    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    ax.text((min(xs) + max(xs)) / 2.0, min(ys) - 1.3,
            fr"$SSD_{{{k}}}(D_{{{m},{n}}})$",
            ha="center", va="top", fontsize=13)

    ax.set_aspect("equal")
    ax.axis("off")
    padx = (max(xs) - min(xs)) * 0.10 + 0.8
    ax.set_xlim(min(xs) - padx, max(xs) + padx)
    ax.set_ylim(min(ys) - 2.4, max(ys) + 1.0)


# urutan halaman: tiap halaman 2 graf (kiri, kanan), sama seperti dokumen PDF
PAGES = [
    [(1, 3, 2), (1, 3, 3)],
    [(1, 3, 4), (1, 3, 5)],
    [(1, 4, 2), (1, 4, 3)],
    [(1, 4, 4), (1, 4, 5)],
    [(1, 5, 2), (1, 5, 3)],
    [(1, 5, 4), (1, 5, 5)],
    [(2, 3, 2), (2, 3, 3)],
    [(2, 3, 4), (2, 3, 5)],
]


def main():
    out = "ssd_prism_document.pdf"
    with PdfPages(out) as pdf:
        for page in PAGES:
            fig, axes = plt.subplots(1, 2, figsize=(11.69, 8.27))  # A4 landscape
            for ax, (k, m, n) in zip(axes, page):
                draw_one(ax, k, m, n)
            fig.tight_layout()
            pdf.savefig(fig, facecolor="white")
            plt.close(fig)
    print(f"saved: {out}  ({len(PAGES)} halaman)")


if __name__ == "__main__":
    main()
