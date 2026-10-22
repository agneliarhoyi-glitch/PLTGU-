"""
Halaman 5: Pembersihan Terkendali & Pemilihan Periode (Versioned Controlled Cleaning)
Pemisahan kondisi operasi stabil (steady-state) dari start-up, shutdown, dan trip dengan pratinjau sebelum versi baru disimpan.
Ultra-modern UI dengan ikon SVG vektor tajam, kartu KPI komparasi, dan alur tata kelola versi Section K.
"""

from datetime import datetime
import streamlit as st
import pandas as pd
from ui.components import (
    render_synthetic_banner, 
    render_page_hero, 
    render_mockup_kpi_card, 
    render_section_header,
    render_empty_dataset_notice,
    LUCIDE_SVG_ICONS
)
from core.cleaning import filter_steady_state_periods, filter_by_date_range

def render(session_state):
    render_synthetic_banner(session_state.get("is_synthetic", True))
    
    render_page_hero(
        title="Pembersihan Terkendali & Pemilihan Periode",
        subtitle="Pemisahan kondisi operasi stabil (steady-state) dari start-up, shutdown, dan trip dengan pratinjau sebelum versi baru disimpan.",
        badge_text="Versioned Controlled Cleaning",
        badge_icon="broom"
    )
    
    raw_df = session_state.get("raw_df")
    mapping = session_state.get("tag_mapping", {})
    
    if raw_df is None or raw_df.empty:
        render_empty_dataset_notice(mode="card", key_suffix="p05")
        return

    def _find_power_col():
        c = mapping.get("plant_net")
        if c and c in raw_df.columns:
            return c
        for fb in ["plant_net_power_mw", "plant_net", "plant_gross_mw", "st_gross_mw", "gt1_gross_mw", "GTDL-19173", "STDL-20106"]:
            if fb in raw_df.columns:
                return fb
        return None

    ts_col = mapping.get("timestamp", "timestamp")
    power_col = _find_power_col() or "plant_net_power_mw"
    
    render_section_header(
        title="Konfigurasi Aturan Pembersihan & Filter Kondisi",
        subtitle="Tetapkan batas beban minimum dan laju ramp untuk mengisolasi kondisi transien secara matematis",
        icon_key="sliders",
        badge_text="Aturan Filter Terkendali"
    )
    
    # KONTROL FILTER DALAM CARD MODERN
    with st.container(border=True):
        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown("<div style='font-size:13px; font-weight:700; color:#0F172A; margin-bottom:6px;'>1. Rentang Waktu Analisis Periode:</div>", unsafe_allow_html=True)
            if ts_col in raw_df.columns:
                min_ts = pd.to_datetime(raw_df[ts_col].dropna().min())
                max_ts = pd.to_datetime(raw_df[ts_col].dropna().max())
                date_range = st.date_input(
                    "Pilih Rentang Tanggal:", 
                    value=(min_ts.date(), max_ts.date()), 
                    min_value=min_ts.date(), 
                    max_value=max_ts.date(),
                    label_visibility="collapsed"
                )
            else:
                date_range = None
                
        with col2:
            st.markdown("<div style='font-size:13px; font-weight:700; color:#0F172A; margin-bottom:6px;'>2. Kriteria Kondisi Stabil (Steady-State):</div>", unsafe_allow_html=True)
            min_load = st.slider("Beban Minimum Pembangkit (MW):", min_value=0.0, max_value=400.0, value=50.0, step=10.0, help="Menyaring kondisi shutdown atau operasi idle")
            max_ramp = st.slider("Batas Laju Perubahan Beban (MW/menit):", min_value=0.2, max_value=5.0, value=1.0, step=0.1, help="Menyaring kondisi transien cepat atau trip")

    # Jalankan Filter Preview
    df_preview = raw_df.copy()
    if date_range and len(date_range) == 2:
        df_preview = filter_by_date_range(df_preview, timestamp_col=ts_col, start_date=str(date_range[0]), end_date=str(date_range[1]))
        
    detected_int = 5.0
    if ts_col in df_preview.columns:
        diffs = pd.to_datetime(df_preview[ts_col], errors="coerce").dropna().diff().dt.total_seconds().dropna()
        valid_d = diffs[(diffs > 0) & (diffs < 7200)]
        if not valid_d.empty and valid_d.median() > 0:
            detected_int = float(valid_d.median() / 60.0)

    df_steady, steady_mask = filter_steady_state_periods(
        df_preview, 
        power_col=power_col, 
        min_load_mw=min_load, 
        max_ramp_rate_mw_per_min=max_ramp, 
        interval_min=detected_int
    )

    retention_pct = round(len(df_steady) / len(raw_df) * 100.0, 1) if len(raw_df) > 0 else 0
    excluded_rows = len(raw_df) - len(df_steady)
    cur_version = session_state.get("active_version", "v1_raw")

    render_section_header(
        title="Pratinjau Dampak Pembersihan (Preview Before Apply)",
        subtitle="Evaluasi perbandingan jumlah baris data sebelum disimpan ke versi dataset terkendali baru",
        icon_key="broom",
        badge_text=f"Retensi Data: {retention_pct}%",
        icon_bg="#F0FDF4",
        icon_color="#16A34A"
    )
    
    # 4 KARTU KPI PREVIEW MODERN
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        render_mockup_kpi_card(
            icon_key="database",
            icon_bg="#EFF6FF",
            icon_color="#2563EB",
            title="Total Baris Mentah",
            value=f"{len(raw_df):,}",
            unit="baris",
            status_label="Normal",
            trend_arrow="•",
            trend_pct="100%",
            trend_direction="up",
            trend_subtext="basis data awal",
            trace_footer="Data mentah asli (Immutable)"
        )
    with p2:
        render_mockup_kpi_card(
            icon_key="check_circle",
            icon_bg="#ECFDF5",
            icon_color="#059669",
            title="Baris Steady-State",
            value=f"{len(df_steady):,}",
            unit="baris",
            status_label="Normal",
            trend_arrow="✓",
            trend_pct=f"{retention_pct}%",
            trend_direction="up",
            trend_subtext="data dipertahankan",
            trace_footer="Lolos kriteria stabil & beban"
        )
    with p3:
        render_mockup_kpi_card(
            icon_key="filter",
            icon_bg="#FFFBEB",
            icon_color="#D97706",
            title="Baris Terisolasi",
            value=f"{excluded_rows:,}",
            unit="baris",
            status_label="Normal" if excluded_rows == 0 else "Warning",
            trend_arrow="•",
            trend_pct="Transien",
            trend_direction="up",
            trend_subtext="disaring terpisah",
            trace_footer="Startup, shutdown, & trip"
        )
    with p4:
        raw_v_disp = cur_version.split()[0] if cur_version else "v1_raw"
        render_mockup_kpi_card(
            icon_key="package",
            icon_bg="#FAF5FF",
            icon_color="#9333EA",
            title="Versi Aktif Saat Ini",
            value=raw_v_disp,
            unit="",
            status_label="Normal",
            trend_arrow="•",
            trend_pct="Audit Trail",
            trend_direction="up",
            trend_subtext="terkendali",
            trace_footer="Versi dataset yang sedang aktif"
        )

    # FORM SIMPAN VERSI BARU DALAM CARD MODERN
    render_section_header(
        title="Manajemen & Aktivasi Versi Terkendali Baru",
        subtitle="Simpan subset data stabil ini sebagai versi terdaftar tanpa menimpa data mentah asli",
        icon_key="package",
        badge_text="Version Control",
        icon_bg="#FAF5FF",
        icon_color="#9333EA"
    )
    
    with st.container(border=True):
        c_name, c_btn = st.columns([2, 1], gap="medium")
        with c_name:
            version_input_name = st.text_input("Nama Versi Dataset Baru:", value=f"v2_steady_state_{datetime.now().strftime('%H%M')}")
        with c_btn:
            st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
            if st.button("Terapkan & Buat Versi Baru", icon=":material/save:", width="stretch", type="primary"):
                session_state["active_df"] = df_steady.copy()
                session_state["active_version"] = version_input_name
                
                # Catat ke log perubahan
                if "change_logs" not in session_state:
                    session_state["change_logs"] = []
                session_state["change_logs"].append({
                    "version": version_input_name,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "rows": len(df_steady),
                    "columns": len(df_steady.columns),
                    "action": f"Filter Steady-State (Beban >= {min_load} MW, Ramp <= {max_ramp} MW/min)",
                    "rules": {"min_load_mw": min_load, "max_ramp_mw_min": max_ramp, "date_range": str(date_range)}
                })
                st.toast(f"✅ Versi baru '{version_input_name}' berhasil disimpan dan diaktifkan!", icon="💾")
                st.rerun()

    # Sampel Data Hasil Pembersihan
    with st.expander("Pratinjau Sampel Data Hasil Pembersihan (10 Baris Pertama)", icon=":material/visibility:", expanded=False):
        st.dataframe(df_steady.head(10), width="stretch")
