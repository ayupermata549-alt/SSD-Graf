"""
make_pdf_center.py — buat PDF penjelasan TITIK CENTER pada graf
super sub-divisi prisma SSD_k(D_{m,n}). Pakai matplotlib (mathtext) supaya
rumus rapi tanpa LaTeX, dan halaman terakhir berisi gambar yang menyorot
seluruh himpunan titik center.

Jalankan:  python make_pdf_center.py
Output  :  penjelasan_titik_center.pdf
"""
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages
import networkx as nx

from supersubdivision_ui import build_ssd_prism_doc, pretty


# ---------------------------------------------------------------- konten teks
DOC = [
    ("h1",  "Titik Center pada Graf"),
    ("h1b", r"$SSD_k(D_{m,n})$ — Super Sub-Divisi Graf Prisma"),
    ("space", 0.4),
    ("body", "Dokumen ini menjelaskan letak titik center (pusat graf) pada"),
    ("body", "super sub-divisi graf prisma D_{m,n} = C_m x P_n, untuk sembarang"),
    ("body", "k >= 1, m >= 3, n >= 2."),
    ("space", 0.5),

    ("h2", "1. Definisi"),
    ("body", "Titik center = simpul dengan EKSENTRISITAS minimum, dengan"),
    ("eq",  r"$\mathrm{ecc}(v) = \max_{u} d(v,u)$"),
    ("body", "(jarak terjauh dari v). Nilai minimumnya disebut radius. Jadi titik"),
    ("body", "center adalah simpul yang 'paling di tengah'."),
    ("space", 0.5),

    ("h2", "2. Prinsip dasar (sebelum disubdivisi)"),
    ("body", "D_{m,n} = C_m x P_n adalah hasil kali Kartesius. Untuk hasil kali"),
    ("body", "Kartesius, eksentrisitas bersifat aditif, sehingga:"),
    ("eq",  "center(C_m □ P_n)  =  center(C_m) × center(P_n)"),
    ("body", "- C_m self-centered  ->  center = SEMUA posisi siklus j = 1..m"),
    ("body", "- P_n (lintasan n lapis)  ->  center = lapis TENGAH:"),
    ("body", "    n ganjil -> satu lapis  i = (n+1)/2"),
    ("body", "    n genap  -> dua lapis    i = n/2  dan  n/2 + 1"),
    ("space", 0.5),

    ("h2", "3. Efek super-subdivisi SSD_k"),
    ("body", "SSD_k mengganti tiap rusuk dengan K_{2,k}: setiap rusuk asli menjadi"),
    ("body", "PANJANG 2 (lewat simpul subdivisi berderajat 2). Maka jarak antar"),
    ("body", "simpul dasar menjadi dua kali lipat, dan 'titik tengah sejati' dapat"),
    ("body", "jatuh TEPAT pada simpul subdivisi. Inilah yang menggeser center."),
    ("space", 0.5),

    ("h2", "4. Hasil akhir (terbukti lewat perhitungan eksak)"),
    ("body", "n GANJIL  ->  center = siklus TENGAH yang tersubdivisi (lapis i):"),
    ("eq",  r"$C = \{u_{i,j}\}\cup\{w^{t}_{i,j}\},"
            r"\quad i=\frac{n+1}{2},\ \ |C| = m(k+1)$"),
    ("body", "n GENAP   ->  center = subdivisi rusuk-tegak (rung) matching tengah:"),
    ("eq",  r"$C = \{v^{t}_{i,j}\},"
            r"\quad i=\frac{n}{2},\ \ |C| = k\,m$"),
    ("space", 0.3),
    ("body", "Mengapa beda berdasar paritas n:"),
    ("body", "- n ganjil: tengah lintasan tepat DI sebuah lapis, jadi seluruh"),
    ("body", "  siklus tengah (titik dasar u DAN subdivisi-siklusnya w) sama-sama"),
    ("body", "  paling tengah."),
    ("body", "- n genap: tengah lintasan jatuh DI ANTARA dua lapis, yaitu persis"),
    ("body", "  di tengah rung. Simpul subdivisi rung v di sana lebih sentral"),
    ("body", "  daripada simpul dasar, jadi merekalah center-nya."),
    ("space", 0.3),
    ("body", "Pengaruh k: menambah k hanya menambah banyak simpul subdivisi di"),
    ("body", "lokasi center yang SAMA (lihat rumus |C|); letaknya tidak berubah."),
    ("space", 0.5),

    ("h2", "5. Contoh konkret"),
    ("body", "SSD_1(D_3,2)  (n genap):  center = { v^1_{1,1}, v^1_{1,2}, v^1_{1,3} }"),
    ("body", "   yaitu 3 titik tengah rung  (|C| = k*m = 3)."),
    ("body", "SSD_1(D_3,3)  (n ganjil):  center = { u_{2,1}, u_{2,2}, u_{2,3} }"),
    ("body", "   gabung { w^1_{2,1}, w^1_{2,2}, w^1_{2,3} }  -> segitiga tengah"),
    ("body", "   yang tersubdivisi  (|C| = m(k+1) = 6)."),
    ("body", "SSD_2(D_3,3):  |C| = m(k+1) = 3*3 = 9  (3 dasar + 6 subdivisi-siklus)."),
    ("space", 0.5),

    ("h2", "6. Pengecualian"),
    ("body", "SSD_k(D_4,2) menyimpang dari pola: D_4,2 = C_4 x P_2 adalah graf"),
    ("body", "KUBUS Q_3 yang self-centered (radius = diameter), sehingga center-nya"),
    ("body", "jauh lebih besar (mis. SSD_1(D_4,2) punya 20 titik center, bukan"),
    ("body", "k*m = 4). Untuk m ganjil atau n >= 3, pola di bagian 4 berlaku rapi."),
    ("space", 0.5),

    ("h2", "7. Catatan tentang kode"),
    ("body", "- UI menghitung nx.center(G) lalu menandai SATU wakil center (yang"),
    ("body", "  terdekat ke pusat gambar) dengan lingkaran oranye putus-putus."),
    ("body", "- Center bersifat struktural (soal jarak), BUKAN titik yang otomatis"),
    ("body", "  mendapat label 0. Pelabelan radio optimal biasanya tidak dimulai"),
    ("body", "  dari center."),
]

# ---------------------------------------------------------------- layout teks
PAGE_W, PAGE_H = 8.27, 11.69
MARGIN_TOP, MARGIN_BOT = 0.85, 0.85
LEFT_FRAC = 0.09

STYLE = {
    "h1":  dict(size=20, weight="bold", color="#1a237e", height=0.46, gap=0.00),
    "h1b": dict(size=14, weight="bold", color="#1a237e", height=0.40, gap=0.02),
    "h2":  dict(size=13, weight="bold", color="#00695c", height=0.34, gap=0.30),
    "body":dict(size=10.5, weight="normal", color="#1a1a1a", height=0.205, gap=0.0),
    "eq":  dict(size=13, weight="normal", color="#000000", height=0.40, gap=0.10,
                center=True),
}

pdf = PdfPages("penjelasan_titik_center.pdf")
fig = plt.figure(figsize=(PAGE_W, PAGE_H))
cur = MARGIN_TOP


def y_frac():
    return 1.0 - cur / PAGE_H


def new_page():
    global fig, cur
    pdf.savefig(fig)
    plt.close(fig)
    fig = plt.figure(figsize=(PAGE_W, PAGE_H))
    cur = MARGIN_TOP


for kind, text in DOC:
    if kind == "space":
        cur += text * 0.22
        continue
    if kind == "newpage":
        new_page()
        continue
    st = STYLE.get(kind, STYLE["body"])
    cur += st.get("gap", 0.0)
    h = st["height"]
    if cur + h > PAGE_H - MARGIN_BOT:
        new_page()
    x = 0.5 if st.get("center") else LEFT_FRAC
    ha = "center" if st.get("center") else "left"
    fig.text(x, y_frac(), text, ha=ha, va="top",
             fontsize=st["size"], fontweight=st["weight"], color=st["color"])
    cur += h

pdf.savefig(fig)
plt.close(fig)


# ------------------------------------------------ halaman gambar (sorot center)
def draw_center_figure(ax, k, m, n):
    G, pos = build_ssd_prism_doc(k, m, n)
    center = set(nx.center(G))
    for u, v in G.edges:
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        ax.plot([x1, x2], [y1, y2], color="#9aa7b0", lw=1.3, zorder=1)
    for v in G.nodes:
        x, y = pos[v]
        base = v.startswith("p_")
        ax.scatter([x], [y], s=110 if base else 70,
                   c="black" if base else "#e000e0",
                   zorder=3, edgecolors="white", linewidths=0.5)
        if v in center:
            ax.add_patch(mpatches.Circle(
                (x, y), 0.42, facecolor="none", edgecolor="#ff6f00",
                lw=2.2, linestyle="--", zorder=5))
    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    ax.text((min(xs) + max(xs)) / 2, min(ys) - 1.3,
            fr"$SSD_{{{k}}}(D_{{{m},{n}}})$   |center| = {len(center)}",
            ha="center", va="top", fontsize=12)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(min(xs) - 1.1, max(xs) + 1.1)
    ax.set_ylim(min(ys) - 2.3, max(ys) + 1.0)


figp = plt.figure(figsize=(PAGE_W, PAGE_H))
figp.suptitle("Ilustrasi titik center (lingkaran oranye = anggota center)",
              fontsize=13, fontweight="bold", color="#00695c", y=0.96)
ax1 = figp.add_axes([0.05, 0.55, 0.42, 0.36]); draw_center_figure(ax1, 1, 3, 2)
ax2 = figp.add_axes([0.53, 0.55, 0.42, 0.36]); draw_center_figure(ax2, 1, 3, 3)
ax3 = figp.add_axes([0.05, 0.08, 0.42, 0.40]); draw_center_figure(ax3, 2, 3, 3)
ax4 = figp.add_axes([0.53, 0.08, 0.42, 0.40]); draw_center_figure(ax4, 1, 5, 3)
figp.text(0.5, 0.515,
          "n genap (kiri atas): center di rung tengah.   "
          "n ganjil (sisanya): center di siklus tengah yang tersubdivisi.",
          ha="center", fontsize=9.5, color="#444")
pdf.savefig(figp)
plt.close(figp)

pdf.close()
print("OK -> penjelasan_titik_center.pdf")
