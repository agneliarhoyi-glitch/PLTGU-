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

    def _find_col(canon, fallbacks):
        c = mapping.get(canon)
        if c and c in df.columns:
            return c
        for fb in fallbacks:
            if fb in df.columns:
                return fb
        return None

    ts_col = _find_col("timestamp", ["timestamp", "waktu", "datetime", "date_time", "time"]) or "timestamp"
    net_col = _find_col("plant_net", ["plant_net_power_mw", "plant_net", "total_net_mw", "plant_gross_mw", "st_gross_mw"])
    amb_col = _find_col("ambient_temp_c", ["ambient_temp_c", "ambient_temp", "t_ambient", "4HRCTE-0001", "suhu_lingkungan"])
    fuel_col = _find_col("gt1_fuel_flow", ["plant_total_fuel_kg_h", "gt1_fuel_flow_kg_h", "CFGAAI-0004", "CFGAAI-0005"])

    # Subsampling jika data besar
    sample_df = df.iloc[::max(1, len(df)//1200)].copy() if len(df) > 1200 else df.copy()

    # Fallback estimasi daya neto jika tidak ada kolom neto eksplisit
    if not net_col or net_col not in df.columns:
        gt_cols = [_find_col(f"gt{i}_power", [f"gt{i}_gross_mw", f"GTDL-{i}9173"]) for i in (1, 2, 3)]
        st_c = _find_col("st_power", ["st_gross_mw", "STDL-20106"])
        valid_p = [c for c in gt_cols + [st_c] if c and c in df.columns]
        if valid_p:
            df["_derived_net_mw"] = df[valid_p].apply(pd.to_numeric, errors="coerce").sum(axis=1) * 0.97
            sample_df["_derived_net_mw"] = df["_derived_net_mw"].iloc[sample_df.index]
            net_col = "_derived_net_mw"

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

    with col_g1:
        if net_col and amb_col and net_col in sample_df.columns and amb_col in sample_df.columns:
            fig1 = create_styled_plot("Sensitivitas Daya Neto vs Temperatur Lingkungan", x_label="Temperatur Lingkungan (°C)", y_label="Daya Neto (MW)")
            fig1.add_trace(go.Scatter(
                x=pd.to_numeric(sample_df[amb_col], errors="coerce"), 
                y=pd.to_numeric(sample_df[net_col], errors="coerce"), 
                mode="markers",
                marker={"color": EQUIPMENT_COLORS["Plant Net Power"], "size": 5, "opacity": 0.65},
                name="Titik Operasi Aktual"
            ))
            st.plotly_chart(fig1, width="stretch")
        else:
            st.info("Tag Daya Neto atau Ambient Temp belum dipetakan.", icon=":material/info:")

    with col_g2:
        if net_col and fuel_col and net_col in sample_df.columns and fuel_col in sample_df.columns:
            fig2 = create_styled_plot("Kurva Karakteristik Input-Output (Bahan Bakar vs Daya)", x_label="Daya Neto (MW)", y_label="Total Aliran Bahan Bakar (kg/h)")
            fig2.add_trace(go.Scatter(
                x=pd.to_numeric(sample_df[net_col], errors="coerce"), 
                y=pd.to_numeric(sample_df[fuel_col], errors="coerce"), 
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
        ts_series = pd.to_datetime(df[ts_col], errors="coerce")
        dts = (ts_series.shift(-1) - ts_series).iloc[:-1].dt.total_seconds() / 3600.0
        med_dt = float(dts.median()) if not dts.empty and float(dts.median()) > 0 else (5.0/60.0)
        dts = dts.apply(lambda dt: med_dt if (pd.isna(dt) or dt <= 0 or dt > 2.0) else dt)
        
        stat_rows = []
        target_vars = [
            ("Daya Neto PLTGU", net_col, "MW"),
            ("Daya Gross GT-1", _find_col("gt1_power", ["gt1_gross_mw", "GTDL-19173"]), "MW"),
            ("Daya Gross GT-2", _find_col("gt2_power", ["gt2_gross_mw", "GTDL-29173"]), "MW"),
            ("Daya Gross GT-3", _find_col("gt3_power", ["gt3_gross_mw", "GTDL-39173"]), "MW"),
            ("Daya Gross ST", _find_col("st_power", ["st_gross_mw", "STDL-20106"]), "MW"),
            ("Temperatur Ambient", amb_col, "°C")
        ]
        
        for name, col_name, unit in target_vars:
            if col_name and col_name in df.columns:
                series = pd.to_numeric(df[col_name], errors="coerce").dropna()
                if series.empty:
                    continue
                arithmetic_mean = float(series.mean())
                
                # Time-weighted
                if len(series) > 1 and len(dts) == len(series) - 1:
                    tw_mean = float(np.sum(series.iloc[:-1].values * dts.values) / np.sum(dts.values))
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

    # 4. PENJELAJAH TREN BEBAS MULTI-SENSOR DCS (105 TAG DCS)
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    render_section_header(
        title="Penjelajah Tren Bebas Multi-Sensor (Eksplorasi Seluruh Tag DCS)",
        subtitle="Visualisasikan dan periksa tren waktu riil untuk setiap parameter dari seluruh sensor yang tersedia di dataset",
        icon_key="activity",
        badge_text=f"{len(df.columns)} Tag Tersedia",
        icon_bg="#F0FDF4",
        icon_color="#16A34A"
    )

    numeric_cols = [c for c in df.columns if c != ts_col and pd.api.types.is_numeric_dtype(df[c])]
    if numeric_cols:
        default_tag = "1SGA-RPM" if "1SGA-RPM" in numeric_cols else numeric_cols[0]
        selected_tag = st.selectbox(
            "Pilih Tag Sensor DCS untuk Dianalisis:",
            options=numeric_cols,
            index=numeric_cols.index(default_tag) if default_tag in numeric_cols else 0,
            key="custom_sensor_explorer_select"
        )
        
        if selected_tag:
            tag_series = pd.to_numeric(df[selected_tag], errors="coerce").dropna()
            if not tag_series.empty:
                col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                with col_m1:
                    st.metric("Rata-rata Nilai", f"{tag_series.mean():,.2f}")
                with col_m2:
                    st.metric("Nilai Minimum", f"{tag_series.min():,.2f}")
                with col_m3:
                    st.metric("Nilai Maksimum", f"{tag_series.max():,.2f}")
                with col_m4:
                    st.metric("Standar Deviasi (σ)", f"{tag_series.std():,.2f}")
                
                # Plot series
                fig_sensor = create_styled_plot(f"Tren Operasi Sensor: {selected_tag}", x_label="Waktu", y_label=selected_tag)
                fig_sensor.add_trace(go.Scatter(
                    x=sample_df[ts_col],
                    y=sample_df[selected_tag],
                    name=selected_tag,
                    line={"color": "#2563EB", "width": 1.5}
                ))
                st.plotly_chart(fig_sensor, width="stretch")
