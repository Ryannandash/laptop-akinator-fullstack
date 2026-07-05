# Laptop Akinator — Backend + Update Frontend

## Isi paket
1. `laptop-akinator-backend.zip` 
2. `laptop-akinator-frontend-updated.zip` 

## Cara kerja akurasi (Certainty Factor)
- Tiap jawaban (Ya/Mungkin Ya/Tidak Tahu/Mungkin Tidak/Tidak) → CF_user (1, 0.6, 0.2, -0.4, -1).
- Tiap gejala punya bobot pakar (CF_pakar) ke tiap kerusakan, dari tabel Excel kamu.
- CF_evidence = CF_pakar × CF_user, digabung antar gejala pakai rumus kombinasi CF berurutan.
- Kerusakan dengan CF gabungan tertinggi = hasil diagnosis, confidence % = CF × 100 → inilah yang ditampilkan sebagai badge "Akurasi Diagnosis" di ResultScreen (ring progress + warna hijau/kuning/merah).

## Menjalankan backend lokal
```bash
cd laptop-akinator-backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Buka http://localhost:8000/docs untuk lihat semua endpoint (Swagger otomatis dari FastAPI).

## Deploy backend ke Vercel
```bash
cd laptop-akinator-backend
vercel          # login & deploy pertama kali
vercel --prod   # deploy production
```
`vercel.json` sudah diatur supaya semua route `/api/*` masuk ke `api/index.py` (FastAPI).
Set environment variable di dashboard Vercel:
- `JWT_SECRET` — string rahasia untuk sign token (wajib diganti dari default).
- `FRONTEND_ORIGIN` — domain vercel frontend kamu (mis. `https://laptop-akinatorr.vercel.app`), boleh beberapa dipisah koma, default `*`.

⚠️ Catatan penting: penyimpanan user/histori pakai SQLite di `/tmp`, yang di Vercel
bersifat **sementara** (hilang saat cold start / redeploy). Untuk demo & tugas ini cukup,
tapi kalau butuh data permanen lintas deploy, tinggal ganti `DB_PATH`/`database.py` ke
Postgres (Vercel Postgres / Supabase / Neon, semuanya ada free tier).

## Menyambungkan frontend ke backend
Di project frontend, buat file `.env` (boleh copy dari `.env.example`):
```
VITE_API_URL=https://nama-backend-kamu.vercel.app
```
Untuk lokal, biarkan `VITE_API_URL=http://localhost:8000` lalu jalankan `npm run dev` seperti biasa.
Kalau sudah deploy backend, set env var yang sama di **Vercel project frontend** (Settings → Environment Variables) supaya build production ikut memakainya.

## Apa saja yang sudah diimplementasi di backend
- Auth: register, login, me (JWT).
- Diagnosis: symptoms, damages, start, next-question (adaptif), answer (satu-satu seperti di GameScreen), process (kirim semua sekaligus), result, feedback, cancel session.
- Analytics ringkas: `/api/admin/analytics/accuracy` (rasio feedback benar/salah dari user).

Bagian admin panel penuh (CRUD gejala/kerusakan/rule/user, dashboard grafik, notifikasi
broadcast, dsb) di dokumen API kamu belum saya buatkan — itu scope besar untuk backend
admin terpisah. Kalau nanti perlu, strukturnya sudah siap dikembangkan (tinggal tambah
route baru di `app/main.py` + tabel baru di `app/database.py`).

## Yang berubah di frontend
- `src/api/client.js` (baru) — wrapper fetch ke backend.
- `AuthScreen.jsx` — register/login beneran ke `/api/auth/*`, simpan token di localStorage.
- `GameScreen.jsx` — alur tanya-jawab sekarang lewat `/api/diagnosis/:id/answer`, bukan hitung lokal.
- `ResultScreen.jsx` — badge "Akurasi Diagnosis" (ring % + warna) dan daftar kemungkinan kerusakan lain, tombol "Ya/Tidak" kirim feedback ke `/api/diagnosis/:id/feedback`.
- `App.css` — style badge akurasi & chip alternatif kerusakan, sewarna dengan tema ungu/cream yang sudah ada.
