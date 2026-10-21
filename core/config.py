"""
Konfigurasi Desain Sistem & Parameter Rekayasa Website Audit Energi PLTGU
Sesuai Lampiran Color Palette & Visual Design System (Halaman 11-12)
"""

# 1. PALET WARNA UTAMA (BRAND & FOUNDATION)
COLOR_PALETTE = {
    "primary": "#12304A",       # Deep Navy: Header, sidebar, judul utama, navigasi aktif
    "secondary": "#2F6690",     # Steel Blue: Tombol utama, tautan, seri grafik utama
    "accent": "#2A9D8F",        # Energy Teal: KPI positif, indikator performa baik
    "canvas": "#F4F7FA",        # Cool Off-White: Latar belakang halaman
    "surface": "#FFFFFF",       # White: Kartu KPI, tabel, panel, formulir
    "text": "#243342",          # Charcoal: Teks utama dan angka KPI
    "muted": "#64748B",         # Slate Gray: Label, keterangan, metadata
    "border": "#D8E1E8",        # Light Steel: Garis tabel, batas kartu, pemisah
}

# 2. STATUS & VALIDASI DATA (WARNA LATAR & TEKS)
STATUS_COLORS = {
    "VALID": {
        "label": "Normal / Valid",
        "bg": "#E6F4F1",
        "text": "#167D70",
        "icon": "✓"
    },
    "WARNING": {
        "label": "Perhatian",
        "bg": "#FFF4D6",
        "text": "#946200",
        "icon": "⚠️"
    },
    "ANOMALY": {
        "label": "Anomali / Gagal Validasi",
        "bg": "#FDECEC",
        "text": "#B42318",
        "icon": "✕"
    },
    "INFO": {
        "label": "Informasi",
        "bg": "#EAF2FB",
        "text": "#245A85",
        "icon": "ℹ"
    },
    "NOT_ENOUGH_DATA": {
        "label": "Belum Tersedia",
        "bg": "#EEF1F4",
        "text": "#586574",
        "icon": "—"
    }
}

# 3. PALET GRAFIK PERALATAN (PLOT SERIES COLORS)
EQUIPMENT_COLORS = {
    "GT-1": "#2F6690",              # Biru baja
    "GT-2": "#2A9D8F",              # Teal
    "GT-3": "#E9C46A",              # Kuning pasir
    "HRSG-1": "#577590",            # Biru abu
    "HRSG-2": "#43AA8B",            # Hijau
    "HRSG-3": "#F4A261",            # Oranye lembut
    "Steam Turbine": "#7B6D8D",     # Ungu abu
    "ST": "#7B6D8D",
    "Condenser / Cooling Water": "#4D908E", # Hijau-biru
    "Condenser": "#4D908E",
    "Plant Net Power": "#12304A",   # Navy
    "Plant Gross Power": "#2F6690",
    "Auxiliary Power": "#946200"
}

# 4. NILAI DESAIN DEFAULT & BOUNDARY LIMITS PLTGU BLOK 1
DEFAULT_CONSTANTS = {
    "water_cp_default": 4.184,     # kJ/(kg*K)
    "air_cp_default": 1.005,       # kJ/(kg*K)
    "flue_gas_cp_default": 1.08,   # kJ/(kg*K) perkiraan gas buang
    "fuel_lhv_default": 49000.0,   # kJ/kg referensi gas alam jika tidak ada di lab
    "sampling_interval_min": 5.0,  # menit
}

# 5. LABELS & DISCLAIMERS WAJIB
SYNTHETIC_DATA_BANNER = "SINTETIS — BUKAN DATA AKTUAL PEMBANGKIT"
AI_DISCLAIMER = "Hasil AI adalah indikasi analitis dan harus diverifikasi oleh engineer; bukan diagnosis pasti atau rekomendasi kontrol otomatis."
HYSYS_DISCLAIMER = "Website menyiapkan input dan kandidat skenario. Model dibangun/dijalankan di Aspen HYSYS oleh engineer."
