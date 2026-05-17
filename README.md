# Bot Pencatatan Keuangan Telegram

Bot ini menerima perintah terstruktur dari Telegram dan mencatat pengeluaran/pemasukan ke Google Sheets.

## Perintah

- `/add <jumlah> <kategori> [catatan]`
  - Contoh: `/add 50 makan kopi pagi`

## Environment Variables

- `TELEGRAM_BOT_TOKEN` — token bot Telegram.
- `SPREADSHEET_ID` — ID Google Sheets.
- `GOOGLE_SERVICE_ACCOUNT` — JSON credentials service account, bisa raw JSON atau base64.

## Menggunakan `.env`

1. Salin file contoh:

```bash
cp .env.example .env
```
2. Isi nilai nyata di `.env`.
3. Jangan commit file `.env` ke Git.

## Setup Google Sheets

1. Buat Google service account dengan akses `Google Sheets API`.
2. Download credentials JSON.
3. Share spreadsheet dengan email service account sebagai editor.
4. Set env var `GOOGLE_SERVICE_ACCOUNT` dengan JSON atau base64-encoded JSON.

## Run locally

```bash
cd /home/lastnight/bot_project/finance_bot
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Deploy

Rekomendasi: gunakan Railway karena mudah untuk aplikasi webhook Python.

1. Push repository ini ke GitHub.
2. Masuk ke Railway dan buat project baru.
3. Pilih "Deploy from GitHub" lalu sambungkan repo ini.
4. Railway akan mendeteksi `Procfile` dan menjalankan `uvicorn main:app --host 0.0.0.0 --port=${PORT:-8000}`.
5. Di Railway, tambahkan environment variables:
   - `TELEGRAM_BOT_TOKEN`
   - `SPREADSHEET_ID`
   - `GOOGLE_SERVICE_ACCOUNT`
6. Deploy project.

Setelah deployed, atur webhook Telegram:

```bash
curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook" \
  -d "url=https://<your-railway-url>/webhook"
```

> Catatan: saya sudah menambahkan `Procfile` dan `runtime.txt` untuk Railway, tetapi deploy harus dilakukan dari akun Railway kamu sendiri karena saya tidak memiliki akses ke sana.

## Notes

- Bot hanya untuk satu pengguna.
- Spreadsheet kolom: Tanggal, Jumlah, Kategori, Catatan, Mata Uang.
