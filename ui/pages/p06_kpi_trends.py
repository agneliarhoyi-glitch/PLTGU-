"""
Halaman 6: Tren KPI & Analisis Korelasi (Operational Screening)
Visualisasi performa terhadap ambient, kurva input-output panas, serta perbandingan rata-rata berbobot waktu vs aritmetika.
Ultra-modern UI dengan SVG icons, grafik interaktif beresolusi tinggi, dan kepatuhan Section K.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from ui.components import (
    render_synthetic_banner, 
    render_page_hero, 
    render_section_header,
    create_styled_plot,
    render_empty_dataset_notice,
    LUCIDE_SVG_ICONS
)
from core.config import COLOR_PALETTE, EQUIPMENT_COLORS

def render(session_state):
    render_synthetic_banner(session_state.get("is_synthetic", True))
    
    render_page_hero(
        title="Tren KPI & Analisis Korelasi Operasi",
        subtitle="Analisis sensitivitas temperatur ambient, kurva input-output panas bahan bakar, dan statistik berbobot waktu.",
        badge_text="Operational Screening",
        badge_icon="chart"
    )
    
    df = session_state.get("active_df")
    mapping = session_state.get("tag_mapping", {})
    
    if df is None or df.empty:
        render_empty_dataset_notice(mode="card", key_suffix="p06")
        return

    ts_col = mapping.get("timestamp", "timestamp")
    net_col = mapping.get("plant_net", "plant_net_power_mw")
    amb_col = mapping.get("ambient_temp_c", "ambient_temp_c")
    fuel_col = mapping.get("gt1_fuel_flow", "plant_total_fuel_kg_h")

    # Catatan Engineering Screening
    shield_icon = LUCIDE_SVG_ICONS.get("shield", "")
    st.markdown(f"""
    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:12px 18px; margin-bottom:18px; display:flex; align-items:center; gap:12px;">
        <div style="color:#2563EB;">{shield_icon}</div>
        <div style="font-size:12.5px; color:#475569; line-height:1.5;">
            <b style="color:#0F172A;">Prinsip Rekayasa (Engineering Screening):</b> Korelasi statistik antara ambient, beban, dan fuel flow digunakan untuk <i>screening</i> deviasi operasi harian, bukan bukti sebab-akibat langsung tanpa penyesuaian kurva koreksi OEM.
        </div>
    </div>
    """, unsafe_allow_html=True)

    render_section_header(
        title="Visualisasi Karakteristik & Sensitivitas Operasi",
        subtitle="Analisis korelasi multi-parameter daya neto pembangkit terhadap fluktuasi cuaca ambient dan konsumsi bahan bakar",
        icon_key="chart",
        badge_text="Scatter Analysis"
    )

    # GRAFIK 1 & 2 DALAM 2 KOLOM MODERN
    col_g1, col_g2 = st.columns(2, gap="medium")
    
    # Subsampling jika data besar
    sample_df = df.iloc[::max(1, len(df)//1200)].copy() if len(df) > 1200 else df.copy()

    with col_g1:
        if net_col in sample_df.columns and amb_col in sample_df.columns:
            fig1 = create_styled_plot("Sensitivitas Daya Neto vs Temperatur Lingkungan", x_label="Temperatur Lingkungan (°C)", y_label="Daya Neto (MW)")
            fig1.add_trace(go.Scatter(
                x=sample_df[amb_col], 
                y=sample_df[net_col], 
                mode="markers",
                marker={"color": EQUIPMENT_COLORS["Plant Net Power"], "size": 5, "opacity": 0.65},
                name="Titik Operasi Aktual"
            ))
            st.plotly_chart(fig1, width="stretch")
        else:
            st.info("Tag Daya Neto atau Ambient Temp belum dipetakan.", icon=":material/info:")

    with col_g2:
        if net_col in sample_df.columns and fuel_col in sample_df.columns:
            fig2 = create_styled_plot("Kurva Karakteristik Input-Output (Bahan Bakar vs Daya)", x_label="Daya Neto (MW)", y_label="Total Aliran Bahan Bakar (kg/h)")
            fig2.add_trace(go.Scatter(
                x=sample_df[net_col], 
                y=sample_df[fuel_col], 
                mode="markers",
                marker={"color": EQUIPMENT_COLORS["GT-2"], "size": 5, "opacity": 0.65},
                name="Input Panas Bahan Bakar"
            ))
            st.plotly_chart(fig2, width="stretch")
        else:
            st.info("Tag Daya Neto atau Fuel Flow belum dipetakan.", icon=":material/info:")

    # STATISTIK: RATA-RATA BERBOBOT WAKTU VS ARITMETIKA (Section K / Hal 7 Bagian C)
    render_section_header(
        title="Perbandingan Rata-rata Berbobot Waktu (Time-Weighted) vs Aritmetika",
        subtitle="Mencegah distorsi nilai agregat energi pada data dengan interval yang tidak seragam sesuai standar audit",
        icon_key="scale",
        badge_text="Section K Protocol",
        icon_bg="#FAF5FF",
        icon_color="#9333EA"
    )
    
    if ts_col in df.columns:
        ts_series = pd.to_datetime(df[ts_col])
        dts = (ts_series.shift(-1) - ts_series).iloc[:-1].dt.total_seconds() / 3600.0
        dts = dts.apply(lambda dt: (5.0/60.0) if (dt <= 0 or dt > 2.0) else dt)
        
        stat_rows = []
        target_vars = [
            ("Daya Neto PLTGU", net_col, "MW"),
            ("Daya Gross GT-1", "gt1_gross_mw", "MW"),
            ("Daya Gross GT-2", "gt2_gross_mw", "MW"),
            ("Daya Gross GT-3", "gt3_gross_mw", "MW"),
            ("Daya Gross ST", "st_gross_mw", "MW"),
            ("Temperatur Ambient", amb_col, "°C")
        ]
        
        for name, col_name, unit in target_vars:
            if col_name in df.columns:
                series = pd.to_numeric(df[col_name], errors="coerce").dropna()
                arithmetic_mean = series.mean()
                
                # Time-weighted
                if len(series) > 1 and len(dts) == len(series) - 1:
                    tw_mean = np.sum(series.iloc[:-1].values * dts.values) / np.sum(dts.values)
                else:
                    tw_mean = arithmetic_mean
                    
                diff = tw_mean - arithmetic_mean
                stat_rows.append({
                    "Parameter Operasi": name,
                    "Rata-rata Aritmetika": f"{arithmetic_mean:,.2f}",
                    "Rata-rata Berbobot Waktu (Time-Weighted)": f"{tw_mean:,.2f}",
                    "Selisih Deviasi": f"{diff:+.3f}",
                    "Satuan": unit
                })
                
        if stat_rows:
            st.dataframe(pd.DataFrame(stat_rows), width="stretch")
