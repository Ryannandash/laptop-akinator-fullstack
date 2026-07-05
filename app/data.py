"""
Basis pengetahuan (Knowledge Base) Sistem Pakar Diagnosa Kerusakan Laptop.
Sumber: tabel keputusan gejala x kerusakan (fokus_pada_tabel_keputusan.xlsx)

Nilai bobot (weight) untuk setiap pasangan gejala-kerusakan didapat dari
proporsi jumlah jurnal pendukung, dipakai sebagai CF_pakar (CF expert)
dalam perhitungan Certainty Factor.
"""

DAMAGES = {
    "K01": {"name": "LCD / Layar / Monitor", "icon": "🖥️",
            "solution": "Cek dengan menghubungkan laptop ke monitor eksternal (HDMI/VGA). Jika tampilan normal di monitor eksternal, kemungkinan besar panel LCD atau kabel fleksibel layar yang bermasalah dan perlu diganti."},
    "K02": {"name": "Keyboard / Touchpad", "icon": "⌨️",
            "solution": "Bersihkan sela-sela keyboard dari debu, periksa dan pasang ulang konektor fleksibel keyboard/touchpad ke motherboard. Jika masih bermasalah, komponen perlu diganti."},
    "K03": {"name": "Motherboard / Mainboard", "icon": "🔧",
            "solution": "Periksa komponen seperti kapasitor yang mengembang dan jalur power. Bawa ke service center untuk pengecekan jalur mainboard lebih lanjut karena perbaikan memerlukan alat khusus."},
    "K04": {"name": "RAM / Memory", "icon": "💾",
            "solution": "Lepas RAM, bersihkan pin dengan penghapus karet, lalu pasang kembali. Coba di slot berbeda atau uji satu per satu bila ada lebih dari satu keping RAM. Ganti bila masih bermasalah."},
    "K05": {"name": "Harddisk", "icon": "💿",
            "solution": "Segera backup data penting. Periksa koneksi kabel HDD/SSD ke motherboard, jalankan CHKDSK untuk cek bad sector. Jika terdengar bunyi tidak normal, segera ganti harddisk."},
    "K06": {"name": "Baterai", "icon": "🔋",
            "solution": "Lepas baterai lalu coba nyalakan hanya dengan adaptor. Jika laptop normal tanpa baterai, baterai perlu diganti dengan yang original/kompatibel."},
    "K07": {"name": "Charger / Adaptor", "icon": "🔌",
            "solution": "Coba gunakan adaptor lain dengan spesifikasi voltase & ampere yang sama. Jika laptop normal dengan adaptor lain, adaptor lama perlu diganti."},
    "K08": {"name": "Speaker / Sound", "icon": "🔊",
            "solution": "Perbarui driver audio melalui Device Manager. Periksa kondisi fisik speaker internal. Jika driver sudah benar namun tetap bermasalah, kemungkinan IC sound rusak."},
    "K09": {"name": "VGA", "icon": "🎮",
            "solution": "Perbarui driver VGA/GPU. Bersihkan kipas & pasta thermal jika sering overheat. Kerusakan chip VGA memerlukan penanganan khusus (reballing) oleh teknisi berpengalaman."},
    "K10": {"name": "Port USB", "icon": "🔗",
            "solution": "Periksa & perbarui driver USB controller melalui Device Manager. Periksa kondisi fisik port apakah ada pin bengkok/kotor. Jika masih bermasalah, IC port kemungkinan rusak."},
}

SYMPTOMS = {
    "G01": "Layar tidak menampilkan gambar apapun (blank/black screen)",
    "G02": "Layar berkedip / kadang hidup dan mati",
    "G03": "Layar tampak redup / lebih gelap dari biasanya",
    "G04": "Terdapat garis-garis pada layar (horizontal/vertikal/rolling)",
    "G05": "Hanya sebagian layar yang menampilkan gambar (setengah layar)",
    "G06": "Terdapat bintik-bintik / Dot Pixel pada layar",
    "G07": "Layar pecah/retak/goresan",
    "G08": "Sebagian/semua tombol keyboard tidak berfungsi",
    "G09": "Touchpad/mouse tidak berfungsi",
    "G10": "Karakter yang muncul tidak sesuai (salah huruf/angka)",
    "G11": "Keyboard mengetik sendiri / muncul bunyi 'tut' bergantian",
    "G12": "Tombol function tidak berfungsi",
    "G13": "Laptop mati total",
    "G14": "Tombol power on-off tidak berfungsi",
    "G15": "Laptop tiba-tiba mati / restart sendiri",
    "G16": "Laptop terasa lambat/system freeze/not responding/hang",
    "G17": "Stuck/gagal booting saat dinyalakan",
    "G18": "Indikator LED semua mati / berkedip",
    "G19": "Hardisk tidak terdeteksi di BIOS (hardisk baru)",
    "G20": "Blue screen",
    "G21": "Baterai tidak charging (not charging)",
    "G22": 'Tampil pesan "Warning battery CMOS is low, press F1"',
    "G23": 'Tampil pesan "Unknown disk boot error" / "retry boot disk"',
    "G24": "Operator sistem tidak berfungsi",
    "G25": "Tidak dapat masuk ke windows",
    "G26": "Laptop mengeluarkan suara aneh atau tidak wajar",
    "G27": "Tidak bisa install OS",
    "G28": 'Muncul pesan "warning low battery"',
    "G29": "Indikator baterai silang (X) / Lampu tidak menyala saat dicharge",
    "G30": "Baterai tidak terisi / tidak bisa terisi penuh",
    "G31": "Tidak dapat melakukan re-charging pada baterai laptop",
    "G32": "Laptop dicharger posisi hidup kemudian mati",
    "G33": "Speaker tidak keluar suara sama sekali / audio mati",
    "G34": "Suara Speaker sangat kecil",
    "G35": "Suara Speaker pecah / kresek / ada noise",
    "G36": "Suara putus-putus dan tidak jelas",
    "G37": "Tidak ada aliran listrik yang masuk ke perangkat",
    "G38": "LCD eksternal via VGA tidak menampilkan gambar sama sekali",
    "G39": "Port USB tidak berfungsi / tidak terdeteksi",
    "G40": 'Muncul pesan "Warning USB Not Recognize"',
}

# CF_pakar (bobot pakar) untuk tiap gejala terhadap tiap kerusakan.
# Baris = gejala, kolom = K01..K10. 0 berarti gejala tidak relevan dgn kerusakan itu.
WEIGHTS = {
    "G01": {"K01": 0.8333333333, "K09": 0.6666666667},
    "G02": {"K01": 0.3333333333},
    "G03": {"K01": 0.5, "K09": 0.3333333333},
    "G04": {"K01": 0.8333333333, "K09": 1},
    "G05": {"K01": 0.8333333333},
    "G06": {"K01": 0.3333333333},
    "G07": {"K01": 0.8333333333},
    "G08": {"K02": 1},
    "G09": {"K02": 0.6},
    "G10": {"K02": 0.4},
    "G11": {"K02": 0.4},
    "G12": {"K02": 0.4},
    "G13": {"K02": 0.2},
    "G14": {"K02": 0.4},
    "G15": {"K03": 1, "K04": 0.6666666667, "K07": 1},
    "G16": {"K03": 1, "K05": 1},
    "G17": {"K03": 0.75, "K04": 0.5},
    "G18": {"K03": 0.75, "K04": 0.5},
    "G19": {"K03": 0.5},
    "G20": {"K03": 0.75, "K04": 0.6666666667, "K05": 1, "K09": 0.6666666667},
    "G21": {"K03": 0.5, "K06": 0.6666666667},
    "G22": {"K03": 0.75},
    "G23": {"K03": 0.5, "K05": 0.6666666667},
    "G24": {"K04": 0.1666666667},
    "G25": {"K05": 1},
    "G26": {"K05": 0.6666666667},
    "G27": {"K05": 0.6666666667},
    "G28": {"K06": 0.3333333333},
    "G29": {"K06": 1, "K07": 1},
    "G30": {"K06": 0.6666666667},
    "G31": {"K07": 0.6666666667},
    "G32": {"K07": 0.6666666667},
    "G33": {"K08": 1},
    "G34": {"K08": 0.3333333333},
    "G35": {"K08": 1},
    "G36": {"K08": 0.5},
    "G37": {"K09": 0.6666666667},
    "G38": {"K09": 0.3333333333},
    "G39": {"K10": 1},
    "G40": {"K10": 0.5},
}

# Skala CF pengguna berdasarkan jenis jawaban (dipakai dosen SPK pada umumnya)
ANSWER_CF = {
    "yes": 1.0,
    "probably_yes": 0.6,
    "dont_know": 0.2,
    "probably_not": -0.4,
    "no": -1.0,
}

MAX_QUESTIONS = 12
CONCLUDE_CF_THRESHOLD = 0.6   # CF kandidat teratas dianggap cukup yakin
