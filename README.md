# Lab Inventory — Sistem Inventaris Laboratorium

Aplikasi web sederhana untuk mengelola inventaris barang laboratorium. Backend menggunakan Flask dan SQLite3, sedangkan frontend menggunakan HTML, CSS, dan JavaScript murni (tanpa framework frontend).

## Fitur

- Dashboard ringkasan jumlah jenis barang, total stok, kategori, dan barang yang perlu perhatian.
- CRUD barang: tambah, lihat, edit, dan hapus.
- Pencarian berdasarkan kode, nama, atau kategori.
- Filter berdasarkan kondisi barang.
- Validasi input dan pencegahan kode inventaris duplikat.
- Database SQLite dibuat otomatis saat aplikasi dijalankan.
- Tampilan responsif untuk desktop dan perangkat mobile.

## Teknologi

- Python 3.10+
- Flask
- SQLite3 (sudah termasuk dalam Python)
- HTML5, CSS3, Vanilla JavaScript

## Struktur folder

```text
lab-inventory/
├── app.py
├── backend/
│   ├── __init__.py
│   └── database.py
├── database/
│   └── (inventory.db dibuat otomatis)
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── requirements.txt
└── README.md
```

## Instalasi

### 1. Pastikan Python tersedia

```bash
python --version
```

### 2. Buat dan aktifkan virtual environment

Linux / macOS:

```bash
python -m venv venv
source venv/bin/activate
```

Windows:

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Jalankan aplikasi

```bash
python app.py
```

Saat pertama kali dijalankan, aplikasi membuat folder `database/` dan file `inventory.db` secara otomatis.

Buka browser dan akses:

```text
http://127.0.0.1:5000
```

## API endpoint

| Method | Endpoint | Keterangan |
|---|---|---|
| GET | `/api/health` | Cek status API |
| GET | `/api/dashboard` | Ringkasan dashboard |
| GET | `/api/items` | Mengambil seluruh barang |
| GET | `/api/items/<id>` | Mengambil detail barang |
| POST | `/api/items` | Menambahkan barang |
| PUT | `/api/items/<id>` | Memperbarui barang |
| DELETE | `/api/items/<id>` | Menghapus barang |

### Query parameter daftar barang

- `search`: mencari berdasarkan kode, nama, atau kategori.
- `condition`: filter kondisi (`Baik`, `Perlu Perbaikan`, `Rusak`).
- `category`: filter kategori.

Contoh:

```text
/api/items?search=keyboard
/api/items?condition=Baik
```

### Contoh JSON untuk menambahkan barang

```json
{
  "code": "LAB-001",
  "name": "Keyboard",
  "category": "Periferal",
  "quantity": 10,
  "unit": "Unit",
  "location": "Lemari A-1",
  "condition": "Baik",
  "notes": "Inventaris ruang komputer"
}
```

## Catatan pengembangan

- File database lokal berada di `database/inventory.db`.
- Untuk mengosongkan data, hentikan aplikasi lalu hapus file database tersebut. Database akan dibuat ulang saat aplikasi dijalankan.
- Mode `debug=True` ditujukan untuk pengembangan lokal. Jangan gunakan mode debug untuk deployment publik.
- Aplikasi ini belum memiliki autentikasi/login dan belum ditujukan untuk diakses melalui internet secara publik.
