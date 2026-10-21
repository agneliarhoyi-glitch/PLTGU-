# ⚡ Website Audit Energi dan Kinerja PLTGU Blok 1 (3-3-1)

Sistem evaluasi kinerja termal dan audit energi berbasis data operasi historian DCS untuk PLTGU Blok 1 (3 Gas Turbine, 3 HRSG, 1 Steam Turbine, Condenser & Cooling Water System, serta Auxiliary Load).

---

## 📌 1. Gambaran Umum Proyek
Aplikasi ini dikembangkan untuk mengolah data historis DCS (interval target 5 menit) menjadi metrik audit energi standar industri, neraca massa & energi berdasar formulasi IAPWS-IF97, deteksi anomali operasional (Isolation Forest + Persistence Debouncing), penyiapan kondisi representatif untuk Aspen HYSYS, dan ekspor laporan audit formal multi-sheet.

> ⚠️ **Catatan Transparansi Data:**  
> Seluruh pengujian awal menggunakan data dummy sintetis dengan label **`SINTETIS`** pada antarmuka web, grafik, dan berkas ekspor. Data dummy tidak boleh diklaim sebagai performa aktual plant.

---

## 🛠️ 2. Arsitektur & Struktur Direktori
```
Website Audit Energi dan Kinerja PLTGU/
├── app.py                      # Titik masuk utama aplikasi (Streamlit Multi-Page Routing & Auth Gate)
├── requirements.txt            # Dependensi paket Python
├── README.md                   # Petunjuk instalasi, penggunaan, dan dokumentasi teknis
├── core/                       # Mesin perhitungan inti (Deterministik & AI)
│   ├── auth.py                 # Autentikasi pengguna, SHA-256 + salt hashing, role-based access
│   ├── config.py               # Token warna visual design system & batas fisik operasi
│   ├── models.py               # Dataclass KPIResult, AnomalyFinding, QualityReport
│   ├── calculation_engine.py   # Rumus deterministik (Heat Input, Net Power, Heat Rate, Efisiensi)
│   ├── steam_tables.py         # Formulasi termodinamika uap IAPWS-IF97 (pyXSteam)
│   ├── data_quality.py         # Validator integritas data (Missing, Gaps, Duplikasi, Flatline)
│   ├── cleaning.py             # Controlled cleaning (Steady-state vs transient filtering, audit log)
│   ├── mass_energy_balance.py  # Evaluasi neraca massa & neraca energi tertutup
│   ├── ai_anomaly.py           # Unsupervised Isolation Forest + Persistence Debouncing
│   ├── synthetic_data.py       # Generator data sintetis 1 bulan (~8.640 baris 5-menitan)
│   └── hysys_exporter.py       # Ekstraksi baseline & data gap untuk Aspen HYSYS
├── ui/                         # Lapisan antarmuka pengguna
│   ├── styles.py               # Injeksi CSS Visual Design System resmi
│   ├── components.py           # Kartu KPI, badge status, watermark banner, template chart
│   └── pages/                  # Halaman alur kerja & portal autentikasi
│       ├── p00_login.py        # Portal Login industrial modern & 1-click Quick Access
│       ├── p01_dashboard.py
│       ├── p02_import.py
│       ├── p03_tag_mapping.py
│       ├── p04_data_quality.py
│       ├── p05_cleaning_filter.py
│       ├── p06_kpi_trends.py
│       ├── p07_equipment.py
│       ├── p08_mass_energy.py
│       ├── p09_ai_optimization.py
│       ├── p10_hysys_prep.py
│       ├── p11_report_export.py
│       └── p12_audit_settings.py
├── data/
│   ├── demo/                   # Dataset sintetis (data_pltgu_sintetis_1bulan.csv)
│   └── mappings/               # Template tag mapping DCS (default_mapping_pltgu.json)
└── tests/                      # Pengujian otomatis (Unit Test)
    ├── test_auth.py            # Verifikasi autentikasi, hashing, login/logout, audit trail
    ├── test_calculation_engine.py  # Verifikasi Acceptance Tests Halaman 9-10
    └── test_modules.py         # Pengujian steam tables, data quality, dan AI debouncing
```

---

## 🚀 3. Cara Instalasi & Menjalankan Aplikasi

### Prasyarat
* Python versi 3.10 atau lebih baru (telah diuji pada Python 3.10–3.14).
* Lingkungan Linux / Windows / macOS.

### Langkah-langkah:
1. **Buka Terminal** dan arahkan ke direktori proyek:
   ```bash
   cd "/run/media/rafli/Data/Website Audit Energi dan Kinerja PLTGU"
   ```

2. **Buat & Aktifkan Virtual Environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate    # Di Windows: .venv\Scripts\activate
   ```

3. **Install Dependensi:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Jalankan Unit Test:**
   ```bash
   PYTHONPATH=. pytest tests/ -v
   ```
   *(Seluruh 17 pengujian otomatis harus bernilai `PASSED`)*

5. **Jalankan Aplikasi Web:**
   ```bash
   streamlit run app.py
   ```
   Buka peramban (browser) di alamat: **`http://localhost:8501`**

---

## 🔐 Akun & Kredensial Login Default
Aplikasi dilengkapi dengan portal autentikasi pengguna dan kendali akses berbasis peran (RBAC):

| Peran (Role) | Nama Pengguna | Kata Sandi | Hak Akses Utama |
| :--- | :--- | :--- | :--- |
| **Maintenance 1 / Lead Auditor (Admin)** | `maintenance 1` / `auditor` | `pltgu2026` | Akses Penuh: Konfigurasi sistem, mapping, audit log, ekspor laporan formal |
| **Plant Performance Engineer** | `engineer` | `engineer123` | Analisis Termal, HYSYS prep, deteksi anomali AI, pembersihan data |
| **Control Room Operator** | `operator` | `operator123` | Monitoring Dashboard real-time, tren KPI, inspeksi kualitas data |

---

## 📊 4. Daftar 12 Halaman / Alur Kerja Utama
1. **1. Dashboard:** Ringkasan GWh produksi bersih, rata-rata daya neto, Heat Rate neto, efisiensi termal neto, beban auxiliary %, dan tren profil beban multi-unit.
2. **2. Import Data:** Upload CSV / Excel, pemilihan sheet, dan pemuatan dataset sintetis operasional.
3. **3. Tag Mapping & Unit:** Pemetaan kolom DCS ke variabel standar (GT1-3, HRSG1-3, ST, Condenser, Plant), auto-matching, dan pemantauan kolom mentah yang belum terpakai.
4. **4. Data Quality:** Audit data hilang (*missing*), *gap* waktu sampling, duplikasi kunci timestamp, sensor macet (*flatline*), batas fisik (*outliers*), dan ekspor daftar isu ke CSV.
5. **5. Cleaning & Period Selection:** Filter periode tanggal dan pemisahan kondisi stabil (*steady-state*) dari start-up/trip tanpa merusak data mentah asli (*versioned audit trail*).
6. **6. KPI & Trends:** Visualisasi kurva input-output bahan bakar, sensitivitas temperatur ambient, serta perbandingan rata-rata berbobot waktu (*time-weighted*) vs aritmetika.
7. **7. Equipment Analysis:** Analisis per unit:
   * **GT 1-3:** Gross MW, fuel flow, compressor pressure ratio ($P_{out,abs}/P_{in,abs}$), dan temperatur gas buang.
   * **HRSG 1-3:** Duty uap utama berbasis entalpi IAPWS-IF97, temperatur stack, feedwater flow.
   * **Steam Turbine (ST):** Daya gross, laju uap masuk total, profil entalpi ekspansi.
   * **Condenser & Cooling Water:** Kenaikan temperatur $\Delta T_{CW}$, duty air pendingin $\dot{Q}_{CW} = \dot{m} C_p \Delta T$, dan tekanan vakum absolut.
8. **8. Mass & Energy Balance:** Pemilihan batas sistem (*boundary*), verifikasi aliran masuk & keluar, perhitungan residual absolut, dan residual relatif (%).
9. **9. Optimization Shortlist (AI):** Deteksi anomali operasional dengan *Isolation Forest* & *Persistence Debouncing* (anti-false alarm spike), grafik bukti data (*evidence chart*), serta alur peninjauan engineer (*workflow review*: Belum Ditinjau, Dikonfirmasi, False Positive, Perlu Investigasi).
10. **10. HYSYS Preparation:** Ringkasan parameter operasi baseline representatif untuk simulasi Aspen HYSYS dan penandaan *data gap*.
11. **11. Report & Export:** Ekspor laporan formal lengkap multi-sheet Excel (`.xlsx`) yang konsisten dengan angka di dashboard.
12. **12. Audit Log & Settings:** Riwayat versi pembersihan dataset, audit trail versi formula rekayasa, dan konfigurasi ambang batas fisik.

---

## 📐 5. Acceptance Test Formula Rekayasa (Lulus 100%)
Berdasarkan Lampiran Teknis K (Halaman 9–10):
| Uji Kasus | Input Uji | Target Spesifikasi | Hasil Implementasi |
| :--- | :--- | :--- | :--- |
| **Konversi Fuel Flow** | $1.000\text{ kg/h}$, $\text{LHV } 50.000\text{ kJ/kg}$ | $\dot{Q}_{fuel} = 13.888,89\text{ kW}$ | `13.888,89 kW` (Lulus) |
| **Daya Listrik Neto** | $P_{gross} = 100\text{ MW}$, $P_{aux} = 5\text{ MW}$ | $P_{net} = 95\text{ MW}$ | `95,00 MW` (Lulus) |
| **Heat Rate Periode** | $\dot{Q}_{fuel} = 100.000\text{ kW}$, $P_{net} = 50.000\text{ kW}$ | $\text{HR} = 7.200\text{ kJ/kWh}$ | `7.200,00 kJ/kWh` (Lulus) |
| **Efisiensi Neto** | $\dot{Q}_{fuel} = 100.000\text{ kW}$, $P_{net} = 50.000\text{ kW}$ | $\eta_{net} = 50\%$ | `50,00 %` (Lulus) |
| **Beban Auxiliary** | $P_{aux} = 5\text{ MW}$, $P_{gross} = 100\text{ MW}$ | $\text{Aux} = 5\%$ | `5,00 %` (Lulus) |
| **Penanganan Data Hilang** | LHV tidak tersedia | Status `NOT_ENOUGH_DATA` (bukan 0) | `NOT_ENOUGH_DATA` (Lulus) |
| **Interval Tidak Seragam** | Dua interval durasi berbeda | Integrasi durasi aktual $\Delta t$ | `20.000 kWh` (Lulus) |

---

## 🎨 6. Visual Design System & Token Warna
Mengikuti spesifikasi Halaman 11–12 secara konsisten:
* **Deep Navy (`#12304A`):** Header, sidebar navigasi, judul utama, plant net power.
* **Steel Blue (`#2F6690`):** Tombol aksi utama, tautan, seri GT-1.
* **Energy Teal (`#2A9D8F`):** KPI positif, aksen visual, seri GT-2.
* **Canvas (`#F4F7FA`):** Latar belakang halaman.
* **Surface (`#FFFFFF`):** Kartu metrik, panel data, kontainer tabel.
* **Status Badges:** 
  * Normal/Valid: Latar `#E6F4F1`, Teks `#167D70`
  * Perhatian: Latar `#FFF4D6`, Teks `#946200`
  * Anomali: Latar `#FDECEC`, Teks `#B42318`
  * Informasi: Latar `#EAF2FB`, Teks `#245A85`
  * Belum Tersedia: Latar `#EEF1F4`, Teks `#586574`
* **Seri Peralatan pada Grafik:**
  * GT-1: `#2F6690` | GT-2: `#2A9D8F` | GT-3: `#E9C46A`
  * HRSG-1: `#577590` | HRSG-2: `#43AA8B` | HRSG-3: `#F4A261`
  * ST: `#7B6D8D` | Condenser/CW: `#4D908E` | Plant Net: `#12304A`

---

## 📋 7. Status Fitur, Batasan, & Tahap Berikutnya
* **Fitur yang Telah Selesai:**
  * Seluruh 12 halaman fungsional dan terhubung.
  * Mesin kalkulasi deterministik lulus seluruh acceptance test.
  * Pustaka IAPWS-IF97 terintegrasi untuk entalpi uap dan air.
  * Generator dataset sintetis 1 bulan penuh (8.640 data 5-menitan) lengkap dengan simulasi startup dan compressor fouling untuk pengujian.
  * Deteksi anomali AI (Isolation Forest) dengan *persistence debounce* dan *workflow review* engineer.
  * Ekspor multi-sheet Excel dan ekspor persiapan model Aspen HYSYS.
* **Keterbatasan Saat Ini:**
  * Formulasi kimia bahan bakar mengasumsikan nilai kalor LHV/HHV yang seragam jika komposisi gas per mole fraction belum diinput dari lab.
  * Aspen HYSYS tidak dieksekusi secara otomatis (sesuai batasan resmi dokumen briefing).
* **Rencana Tahap Berikutnya:**
  * Integrasi data aktual CCR PLTGU saat file historis resmi dari DCS diterima.
  * Penyempurnaan kurva koreksi kondisi lingkungan OEM (*Ambient Correction Curves*) untuk GT dan ST.
