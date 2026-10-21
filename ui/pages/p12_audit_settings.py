"""
Halaman 12: Audit Log, Riwayat Versi & Pengaturan Sistem (System Governance)
Menampilkan catatan penelusuran (audit trail) versi dataset, riwayat mapping, versi formula mesin hitung, serta ambang batas operasi.
Ultra-modern UI dengan SVG icons, tabel status rekayasa, dan tata kelola kepatuhan Section K.
"""

from datetime import datetime
import pandas as pd
import streamlit as st
from ui.components import (
    render_synthetic_banner, 
    render_page_hero, 
    render_section_header,
    LUCIDE_SVG_ICONS
)
from core.data_quality import PHYSICAL_BOUNDS
from core.calculation_engine import ENGINE_VERSION

def render(session_state):
    render_synthetic_banner(session_state.get("is_synthetic", True))
    
    render_page_hero(
        title="Audit Log, Riwayat Versi & Pengaturan",
        subtitle="Pencatatan penelusuran (audit trail) versi dataset, riwayat mapping, versi formula mesin hitung, serta ambang batas operasi.",
        badge_text="System Governance",
        badge_icon="settings"
    )
    
    tab_log, tab_ver, tab_bounds = st.tabs([
        "Audit Trail & Log Perubahan", 
        "Versi Mesin & Formula", 
        "Konfigurasi Batas Operasi"
    ])
    
    # 1. TAB AUDIT TRAIL LOG
    with tab_log:
        render_section_header(
            title="Riwayat Pemrosesan Dataset & Log Pembersihan",
            subtitle="Catatan kronologis perubahan versi, kriteria filter, dan pengguna yang melakukan operasi pada dataset",
            icon_key="file_text",
            badge_text="Audit Trail"
        )
        logs = session_state.get("change_logs", [])
        if not logs:
            st.info("Belum ada aktivitas pembersihan atau perubahan versi dataset yang tercatat.", icon=":material/info:")
        else:
            log_df = pd.DataFrame(logs)
            st.dataframe(log_df, width="stretch", height=320)

    # 2. TAB VERSI MESIN & FORMULA
    with tab_ver:
        render_section_header(
            title="Status & Versi Perhitungan Rekayasa Termal",
            subtitle="Verifikasi modul deterministik, pustaka formulasi uap, dan model unsupervised screening",
            icon_key="cpu",
            badge_text="Engine Specs",
            icon_bg="#FAF5FF",
            icon_color="#9333EA"
        )
        engine_info = [
            {"Komponen": "Calculation Engine", "Versi": ENGINE_VERSION, "Status Validasi": "Lulus Acceptance Test", "Referensi": "Briefing Dev Hal 6-10"},
            {"Komponen": "IAPWS-IF97 Steam Formulation", "Versi": "pyXSteam v0.4.10 (MKS)", "Status Validasi": "Tervalidasi", "Referensi": "IAPWS-IF97 Standar"},
            {"Komponen": "AI Anomaly Detection", "Versi": "IsolationForest+PersistenceDebounce-v1.0", "Status Validasi": "Prototipe / Unsupervised", "Referensi": "Briefing Dev Hal 13-16"},
            {"Komponen": "Data Quality Inspector", "Versi": "DQ-Validator-v1.0", "Status Validasi": "Aktif", "Referensi": "Briefing Dev Hal 7"}
        ]
        st.dataframe(pd.DataFrame(engine_info), width="stretch", height=240)

    # 3. TAB BATAS FISIK OPERASI
    with tab_bounds:
        render_section_header(
            title="Batas Fisik Operasi Peralatan PLTGU Blok 1",
            subtitle="Batas termal dan batas keselamatan yang digunakan untuk mendeteksi outlier sensor (sesuai Section K: data tidak dihapus, hanya diberi flag)",
            icon_key="shield",
            badge_text="Physical Boundaries",
            icon_bg="#F0FDFA",
            icon_color="#0D9488"
        )
        
        bounds_data = []
        for param, (low, high) in PHYSICAL_BOUNDS.items():
            bounds_data.append({
                "Parameter Operasi": param,
                "Batas Minimum": low,
                "Batas Maksimum": high,
                "Tindakan Pelanggaran": "Flag Outlier (Tanpa Hapus Otomatis)"
            })
        st.dataframe(pd.DataFrame(bounds_data), width="stretch", height=380)
