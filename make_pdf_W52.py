"""
make_pdf_W52.py — buat PDF perhitungan W = 52 untuk SSD_1(L_4).
Pakai matplotlib (mathtext) supaya rumus tampil rapi tanpa perlu LaTeX.
Gaya layout mengikuti make_pdf.py.

Jalankan:  python make_pdf_W52.py
Output  :  perhitungan_W52_SSD1_L4.pdf
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# ---- konten: daftar blok (jenis, teks) ----
# jenis: 'h1' judul, 'h1b' subjudul judul, 'h2' subjudul, 'body' teks,
#        'eq' rumus (mathtext), 'space' jarak, 'newpage' halaman baru
DOC = [
    ("h1",  "Perhitungan  W = 52"),
    ("h1b", r"Kasus  $SSD_1(L_4)$  (k = 1, n = 4)"),
    ("space", 0.4),
    ("body", "W = jumlah jarak dari titik pusat (median) c ke semua titik graf,"),
    ("body", "W = sum_v d(v, c).  Angka ini dipakai pada batas bawah radio number"),
    ("body", "rn(G) >= p(d+1) - 2W.  Dokumen ini menurunkan W = 52 langkah demi langkah."),
    ("space", 0.5),

    ("h2", "Parameter dasar graf"),
    ("body", "Untuk SSD_k(L_n) berlaku rumus parameter berikut (di sini k = 1, n = 4):"),
    ("eq",  r"$|V| = 2n + k(3n-2) = 8 + 1\cdot 10 = 18$"),
    ("eq",  r"$p = |V| - 1 = 17, \qquad d = 2n = 8$"),
    ("body", "Median (titik pusat) c = u_q dengan q = ceil(n/2) = ceil(4/2) = 2,  jadi c = u_2."),
    ("space", 0.5),

    ("h2", "Langkah 1 — Hitung S1 dan S2"),
    ("body", "Dua jumlah penolong, dengan q = 2:"),
    ("eq",  r"$S_1 = \sum_{i=1}^{n} |i-q| = |1{-}2|+|2{-}2|+|3{-}2|+|4{-}2|$"),
    ("eq",  r"$S_1 = 1+0+1+2 = 4$"),
    ("eq",  r"$S_2 = \sum_{i=1}^{n-1} \min(|i-q|,\,|i{+}1-q|)$"),
    ("eq",  r"$S_2 = \min(1,0)+\min(0,1)+\min(1,2) = 0+0+1 = 1$"),
    ("space", 0.5),

    ("h2", "Langkah 2 — Rumus umum W"),
    ("body", "W disusun dari kontribusi tiap kelompok titik (titik atas, titik bawah,"),
    ("body", "dan titik subdivisi) terhadap c:"),
    ("eq",  r"$W = 4S_1 + 2n + k\,(2S_1 + 4S_2 + 5n - 4)$"),
    ("eq",  r"$W = 4(4) + 2(4) + 1\,(2{\cdot}4 + 4{\cdot}1 + 5{\cdot}4 - 4)$"),
    ("eq",  r"$W = 16 + 8 + (8 + 4 + 20 - 4) = 16 + 8 + 28 = 52$"),
    ("space", 0.5),

    ("h2", "Langkah 3 — Cek silang dengan bentuk tertutup"),
    ("body", "Untuk n genap, tulis t = n/2 = 2:"),
    ("eq",  r"$W = 4t(t{+}1) + 2k\,t(3t{+}1)$"),
    ("eq",  r"$W = 4(2)(3) + 2(1)(2)(7) = 24 + 28 = 52 \;\checkmark$"),
    ("space", 0.5),

    ("h2", "Rincian kontribusi tiap kelompok titik (c = u_2)"),
    ("body", "Titik atas  u_i  : d(u_i, c) = 2|i-2|        -> total  4 S1 = 16"),
    ("body", "Titik bawah v_i  : d(v_i, c) = 2|i-2| + 2    -> tambahan 2n  =  8"),
    ("body", "Titik subdivisi  : (k = 1 per sisi)          -> k(2S1+4S2+5n-4) = 28"),
    ("eq",  r"$W = 16 + 8 + 28 = 52$"),
    ("space", 0.5),

    ("h2", "Verifikasi terhadap graf sebenarnya"),
    ("body", "Dihitung langsung dari graf (jumlah jarak minimum / median):"),
    ("eq",  r"$W_{\mathrm{graf}} = W_{\mathrm{closed}} = W_{\mathrm{general}} = 52$"),
    ("body", "Ketiganya cocok (verify -> ok = True)."),
    ("space", 0.5),

    ("h2", "Pemakaian: batas bawah radio number"),
    ("eq",  r"$rn \geq p(d{+}1) - 2W = 17{\times}9 - 2{\times}52 = 153 - 104 = 49$"),
    ("body", "Jadi W = 52 memberi batas bawah rn(SSD_1(L_4)) >= 49."),
]

# ---- layout (semua tinggi dalam INCI; halaman A4) ----
PAGE_W, PAGE_H = 8.27, 11.69
MARGIN_TOP, MARGIN_BOT = 0.85, 0.85
LEFT_FRAC = 0.09

STYLE = {
    "h1":  dict(size=20, weight="bold", color="#1a237e", height=0.46, gap=0.00),
    "h1b": dict(size=14, weight="bold", color="#1a237e", height=0.40, gap=0.02),
    "h2":  dict(size=13, weight="bold", color="#00695c", height=0.34, gap=0.34),
    "body":dict(size=10.5, weight="normal", color="#1a1a1a", height=0.215, gap=0.0),
    "eq":  dict(size=13, weight="normal", color="#000000", height=0.40, gap=0.10,
                center=True),
}

pdf = PdfPages("perhitungan_W52_SSD1_L4.pdf")
fig = plt.figure(figsize=(PAGE_W, PAGE_H))
cur = MARGIN_TOP   # jarak dari atas (inci)

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
    if kind == "eq" and (r"\sum" in text):
        h = 0.66
    if cur + h > PAGE_H - MARGIN_BOT:
        new_page()
    x = 0.5 if st.get("center") else LEFT_FRAC
    ha = "center" if st.get("center") else "left"
    fig.text(x, y_frac(), text, ha=ha, va="top",
             fontsize=st["size"], fontweight=st["weight"], color=st["color"])
    cur += h

pdf.savefig(fig)
plt.close(fig)
pdf.close()
print("OK -> perhitungan_W52_SSD1_L4.pdf")
