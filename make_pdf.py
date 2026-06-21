"""
make_pdf.py — buat PDF penjelasan batas bawah radio number SSD_k(L_n).
Pakai matplotlib (mathtext) supaya rumus tampil rapi tanpa perlu LaTeX.

Jalankan:  python make_pdf.py
Output  :  penjelasan_batas_bawah.pdf
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# ---- konten: daftar blok (jenis, teks) ----
# jenis: 'h1' judul, 'h2' subjudul, 'body' teks, 'eq' rumus (mathtext),
#        'space' jarak, 'rule' garis
DOC = [
    ("h1",  "Batas Bawah Radio Number"),
    ("h1b", r"$SSD_k(L_n)$ — Graf Super Sub-Divisi Tangga"),
    ("space", 0.4),
    ("body", "Dokumen ini menjelaskan metode batas bawah  rn(G) >= p(d+1) - 2W"),
    ("body", "yang dipakai untuk graf super sub-divisi tangga, langkah demi langkah."),
    ("space", 0.5),

    ("h2", "Latar: apa yang dibuktikan"),
    ("body", "Radio number rn(G) = span TERKECIL dari semua pelabelan radio valid."),
    ("body", "Batas bawah B berarti: tidak ada pelabelan valid dengan span < B,"),
    ("body", "sehingga rn(G) >= B. Satu argumen berlaku untuk SEMUA pelabelan,"),
    ("body", "jadi kita tak perlu memeriksa satu per satu."),
    ("space", 0.5),

    ("h2", "Langkah 1 — Urutkan titik berdasarkan label"),
    ("body", "Ambil pelabelan valid phi apa pun. Urutkan titik dari label terkecil:"),
    ("eq",  r"$\varphi(x_0) < \varphi(x_1) < \varphi(x_2) < \cdots < \varphi(x_p)$"),
    ("body", "dengan p = |V| - 1.  Maka span = phi(x_p) - phi(x_0)."),
    ("space", 0.5),

    ("h2", "Langkah 2 — Kondisi radio membatasi tiap lompatan"),
    ("body", "Aturan radio untuk SETIAP pasangan titik:"),
    ("eq",  r"$|\varphi(u) - \varphi(v)| \geq d + 1 - d(u,v)$"),
    ("body", "Untuk dua titik berurutan x_i dan x_{i+1} (label menaik):"),
    ("eq",  r"$\varphi(x_{i+1}) - \varphi(x_i) \geq d + 1 - d(x_i, x_{i+1})$"),
    ("space", 0.5),

    ("h2", "Langkah 3 — Jumlahkan semua lompatan"),
    ("body", "Span = jumlah seluruh lompatan label:"),
    ("eq",  r"$\mathrm{span} = \sum_{i=0}^{p-1}[\varphi(x_{i+1})-\varphi(x_i)]"
            r" \geq p(d+1) - \sum_{i=0}^{p-1} d(x_i, x_{i+1})$"),
    ("body", "Intuisi: p(d+1) adalah harga maksimal; tiap jarak antar titik"),
    ("body", "berurutan memberi 'diskon'. Untuk batas BAWAH span, kita batasi"),
    ("body", "total jarak itu dari ATAS."),
    ("space", 0.5),

    ("h2", "Langkah 4 — Batasi total jarak lewat titik pusat c"),
    ("body", "Pilih titik acuan c (median). Ketaksamaan segitiga:"),
    ("eq",  r"$d(x_i, x_{i+1}) \leq d(x_i, c) + d(x_{i+1}, c)$"),
    ("body", "Dijumlahkan: tiap titik muncul di dua pasangan (kecuali ujung),"),
    ("eq",  r"$\sum_{i=0}^{p-1} d(x_i,x_{i+1}) \leq 2\sum_{v} d(v,c) = 2W$"),
    ("body", "dengan W = jumlah jarak dari c ke semua titik."),
    ("space", 0.5),

    ("h2", "Langkah 5 — Gabungkan"),
    ("eq",  r"$rn(G) \;\geq\; \mathrm{span} \;\geq\; p(d+1) - 2W$"),
    ("space", 0.6),

    ("h2", "Contoh konkret:  SSD_1(L_4)"),
    ("body", "Parameter graf:  |V| = 18  ->  p = 17 ;   d = 2n = 8  ->  d+1 = 9 ;"),
    ("body", "W = 52  (sudah diturunkan dan diverifikasi)."),
    ("eq",  r"$rn \geq 17 \times 9 - 2 \times 52 = 153 - 104 = 49$"),
    ("body", "Jadi dipastikan rn(SSD_1(L_4)) >= 49."),
    ("space", 0.6),

    ("h2", "Mengapa batas ini valid tetapi belum tajam"),
    ("body", "Ketaksamaan di Langkah 4 hanya KETAT bila c terletak pada jalur"),
    ("body", "terpendek antara x_i dan x_{i+1} (keduanya 'berseberangan' lewat c)."),
    ("body", "Kenyataannya banyak pasangan berurutan berada di sisi yang sama,"),
    ("body", "sehingga jarak aslinya jauh lebih kecil daripada d(x_i,c)+d(x_{i+1},c)."),
    ("body", "Akibatnya total jarak nyata < 2W, sehingga rn sebenarnya LEBIH tinggi."),
    ("body", "Untuk SSD_1(L_4): batas memberi 49, padahal batas atas valid = 62."),
    ("body", "Selisih itulah 'celah' yang harus ditutup agar batas menjadi eksak."),
    ("space", 0.5),

    ("newpage", None),
    ("h2", "Ringkasan rumus pendukung (SSD_k(L_n))"),
    ("eq",  r"$|V| = 2n + k(3n-2), \qquad d = 2n, \qquad p = |V|-1$"),
    ("body", "W bentuk tertutup (median c = u_q, q = ceil(n/2), t = floor(n/2)):"),
    ("eq",  r"$W = 4t(t{+}1) + 2k\,t(3t{+}1) \quad (n=2t)$"),
    ("eq",  r"$W = 4t^2{+}8t{+}2 + k(6t^2{+}8t{+}1) \quad (n=2t{+}1)$"),
]

# ---- layout (semua tinggi dalam INCI; halaman A4) ----
PAGE_W, PAGE_H = 8.27, 11.69
MARGIN_TOP, MARGIN_BOT = 0.85, 0.85
LEFT_FRAC = 0.09

# height = tinggi baris itu; gap = ruang ekstra SEBELUM blok
STYLE = {
    "h1":  dict(size=20, weight="bold", color="#1a237e", height=0.46, gap=0.00),
    "h1b": dict(size=14, weight="bold", color="#1a237e", height=0.40, gap=0.02),
    "h2":  dict(size=13, weight="bold", color="#00695c", height=0.34, gap=0.34),
    "body":dict(size=10.5, weight="normal", color="#1a1a1a", height=0.215, gap=0.0),
    "eq":  dict(size=13, weight="normal", color="#000000", height=0.40, gap=0.10,
                center=True),
}

pdf = PdfPages("penjelasan_batas_bawah.pdf")
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
        cur += text * 0.22   # 'space' value -> inci
        continue
    if kind == "newpage":
        new_page()
        continue
    st = STYLE.get(kind, STYLE["body"])
    cur += st.get("gap", 0.0)
    # rumus dgn penjumlahan (Sigma) lebih tinggi -> beri ruang ekstra
    h = st["height"]
    if kind == "eq" and (r"\sum" in text):
        h = 0.66
    if cur + h > PAGE_H - MARGIN_BOT:
        new_page()
    x = 0.5 if st.get("center") else LEFT_FRAC
    ha = "center" if st.get("center") else "left"
    # teks di-anchor 'top' pd posisi cur
    fig.text(x, y_frac(), text, ha=ha, va="top",
             fontsize=st["size"], fontweight=st["weight"], color=st["color"])
    cur += h

pdf.savefig(fig)
plt.close(fig)
pdf.close()
print("OK -> penjelasan_batas_bawah.pdf")
