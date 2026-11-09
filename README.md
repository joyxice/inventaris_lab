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
│   └── inventory.db 
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

## API

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