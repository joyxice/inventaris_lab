# Lab Inventory — Flask + SQLite3

Aplikasi inventaris laboratorium dengan autentikasi login, dashboard, dan CRUD barang. Frontend menggunakan HTML, CSS, dan JavaScript murni.

## Struktur proyek

```text
lab-inventory/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── backend/
│   ├── __init__.py
│   └── database.py
├── database/
│   └── inventory.db       # dibuat otomatis
└── frontend/
    ├── index.html
    ├── login.html
    ├── css/
    │   ├── style.css
    │   └── login.css
    └── js/
        ├── app.js
        └── login.js
```

## Instalasi dan menjalankan

Python 3.10+ diperlukan.

Linux / macOS:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Windows PowerShell:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Buka `http://127.0.0.1:5000`.

## Akun awal

Saat pertama kali aplikasi dijalankan dan tabel users masih kosong, aplikasi membuat akun admin awal:

- Username: `admin`
- Password: `Admin123!`

Segera ganti kredensial awal sebelum aplikasi digunakan bersama orang lain. Akun awal hanya dibuat jika belum ada pengguna di database.

Untuk menentukan kredensial awal sendiri, atur environment variable sebelum menjalankan aplikasi:

Linux / macOS:

```bash
export ADMIN_USERNAME="nama_admin"
export ADMIN_PASSWORD="password_yang_kuat"
export SECRET_KEY="ganti_dengan_secret_random_yang_panjang"
python app.py
```

Windows PowerShell:

```powershell
$env:ADMIN_USERNAME="nama_admin"
$env:ADMIN_PASSWORD="password_yang_kuat"
$env:SECRET_KEY="ganti_dengan_secret_random_yang_panjang"
python app.py
```

Jika database sudah memiliki akun, mengubah environment variable tidak otomatis mengganti password akun yang sudah ada.

## Perlindungan akses

- `/` mengarahkan pengguna yang belum login ke `/login`.
- Endpoint inventaris dan dashboard membutuhkan session login.
- Password disimpan dalam bentuk hash menggunakan Werkzeug.
- Session cookie menggunakan HttpOnly dan SameSite=Lax.
- Logout menghapus session.
- Endpoint `/api/health` dan `/api/login` tetap dapat diakses tanpa login.

## API utama

| Method | Endpoint | Keterangan |
|---|---|---|
| POST | `/api/login` | Login |
| POST | `/api/logout` | Logout |
| GET | `/api/session` | Memeriksa session |
| GET | `/api/dashboard` | Ringkasan dashboard (login) |
| GET | `/api/items` | Daftar barang (login) |
| GET | `/api/items/<id>` | Detail barang (login) |
| POST | `/api/items` | Tambah barang (login) |
| PUT | `/api/items/<id>` | Edit barang (login) |
| DELETE | `/api/items/<id>` | Hapus barang (login) |

## Catatan keamanan

- `SECRET_KEY` bawaan hanya untuk pengembangan lokal. Atur nilai acak yang kuat sebelum deployment.
- Jangan gunakan `debug=True` pada server produksi.
- Jika menggunakan HTTPS, set `COOKIE_SECURE=1`.
- Contoh ini belum menyediakan halaman untuk mengubah password atau mengelola banyak akun.
- Untuk deployment publik, tambahkan perlindungan CSRF pada request yang mengubah data, rate limiting login, HTTPS, dan konfigurasi server produksi.
