# 🍛 Kudakan API

**Kudakan** (Kantin untuk Mahasiswa) adalah RESTful API berbasis FastAPI untuk sistem pemesanan makanan di kantin universitas. Proyek ini mengelola data mahasiswa, kantin, menu makanan, dan pesanan. Gambar arsitektur sistem dapat dilihat di bawah ini:

![Database Structure](https://github.com/nfahrisalim/Assets/blob/main/Kudakan/SQL.jpeg?raw=true)

## 📦 Fitur Utama

- CRUD Mahasiswa
- CRUD Kantin
- CRUD Menu (dengan upload gambar via Supabase)
- CRUD Pesanan dan Detail Pesanan
- Filter berdasarkan ID, Email, dan Status
- Auto-kalkulasi harga menu di Detail Pesanan
- Endpoint pencarian menu
- Endpoint relasional: menu + kantin, pesanan + detail, dsb.

## 🧪 Teknologi

- ⚙️ **FastAPI** – backend framework
- 💾 **PostgreSQL** – database relasional
- ☁️ **Supabase Storage** – penyimpanan gambar
- 🧪 **Pydantic** – validasi skema data
- 🧱 **OpenAPI** – dokumentasi otomatis
- 🔁 **CORS Middleware** – untuk akses frontend

## 🔌 API Endpoint

Semua endpoint dapat diakses melalui prefix `/api/v1/`.

Beberapa contoh endpoint:
- `POST /api/v1/mahasiswa/` – Tambah mahasiswa baru
- `GET /api/v1/kantin/{kantin_id}/with-menus` – Ambil kantin + semua menu
- `POST /api/v1/menu/with-image` – Tambah menu + upload gambar
- `GET /api/v1/pesanan/{id}/with-details` – Detail pesanan + info mahasiswa + kantin

Dokumentasi lengkap tersedia di endpoint:  
👉 `/docs` atau `/redoc`

## ⚙️ Instalasi Lokal

```bash
git clone https://github.com/username/kudakan-api.git
cd kudakan-api
python -m venv env
source env/bin/activate  # atau .\env\Scripts\activate di Windows
pip install -r requirements.txt
uvicorn main:app --reload
