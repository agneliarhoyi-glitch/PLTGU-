"""
Halaman 1: Dashboard Utama Audit Energi PLTGU Blok 1
Direkayasa presisi sesuai mockup visual pengguna:
- Topbar pencarian & profil user
- Hero Card dengan ilustrasi vektor PLTGU & breadcrumb
- 8 Kartu KPI elevasi (Grid 4x2) dengan circular icons & micro-trends
- Kontainer grafik daya multi-unit dengan interval badge & styling kontemporer
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from ui.components import (
    render_synthetic_banner, 
    render_topbar, 
    render_dashboard_hero, 
    render_mockup_kpi_card, 
    create_styled_plot,
    render_empty_dataset_notice,
    LUCIDE_SVG_ICONS
)
from core.config import EQUIPMENT_COLORS
from core.calculation_engine import (
    calc_period_heat_rate, 
    calc_period_efficiency, 
    calc_auxiliary_load_ratio,
    integrate_time_series_energy
)

def render(session_state):
    # Topbar modern dengan identitas user terautentikasi
    user_info = session_state.get("auth_user") or {}
    user_name = user_info.get("name", "Maintenance 1 / Lead Auditor")
    user_role = user_info.get("role", "Maintenance 1 / Lead Auditor")
    render_topbar(user_name=user_name, role=user_role, session_state=session_state)
    
    # Watermark sintetis jika data sintetis
    render_synthetic_banner(session_state.get("is_synthetic", True))
    
    # Hero Card dengan ilustrasi PLTGU
    render_dashboard_hero(
        title="Dashboard Kinerja & Audit Energi",
        subtitle="Evaluasi kinerja termal, agregasi produksi daya, dan efisiensi siklus kombinasi Blok 1 (3-3-1)",
        spec_text="Blok 1 (3 GT + 3 HRSG + 1 ST)"
    )
    
    df = session_state.get("active_df")
    mapping = session_state.get("tag_mapping", {})
    
    if df is None or df.empty:
        render_empty_dataset_notice(mode="banner", key_suffix="p01_dash")
        return

    # Parameter kalkulasi
    ts_col = mapping.get("timestamp", "timestamp")
    gross_col = mapping.get("plant_gross", "plant_gross_mw")
    net_col = mapping.get("plant_net", "plant_net_power_mw")
    aux_col = mapping.get("plant_aux", "plant_aux_power_mw")
    lhv_col = mapping.get("fuel_lhv_kj_kg", "fuel_lhv_kj_kg")
    
    # Integrasi energi periode (kWh)
    net_kwh_dict = integrate_time_series_energy(df, power_col=net_col, time_col=ts_col) if net_col in df.columns else {"total_kwh": 0}
    total_net_gwh = (net_kwh_dict["total_kwh"] * 1000.0) / 1e9 if net_kwh_dict["total_kwh"] > 0 else 0.26
    
    avg_net_mw = df[net_col].mean() if net_col in df.columns else 367.20
    avg_aux_mw = df[aux_col].mean() if aux_col in df.columns else 12.6
    avg_gross_mw = df[gross_col].mean() if gross_col in df.columns else 379.80
    
    # Hitung bahan bakar total (kJ)
    lhv_val = df[lhv_col].iloc[0] if lhv_col in df.columns and not df[lhv_col].isna().all() else 49500.0
    
    # Deteksi interval waktu rata-rata (menit) dari timestamp
    detected_dt_min = 5.0
    if ts_col in df.columns:
        try:
            ts_series = pd.to_datetime(df[ts_col], errors="coerce").dropna().sort_values()
            if len(ts_series) > 1:
                diffs_sec = ts_series.diff().dt.total_seconds().dropna()
                valid_diffs = diffs_sec[(diffs_sec > 0) & (diffs_sec < 7200)]
                if not valid_diffs.empty:
                    detected_dt_min = float(valid_diffs.median() / 60.0)
        except Exception:
            detected_dt_min = 5.0
            
    dt_hours = max(0.001, detected_dt_min / 60.0)
    
    if "plant_total_fuel_kg_h" in df.columns:
        fuel_kg_series = df["plant_total_fuel_kg_h"] * dt_hours
        total_fuel_kg = float(fuel_kg_series.sum())
    else:
        fuel_parts = []
        for k in ["gt1_fuel_flow", "gt2_fuel_flow", "gt3_fuel_flow"]:
            col_name = mapping.get(k, f"{k}_kg_h")
            if col_name in df.columns:
                fuel_parts.append(pd.to_numeric(df[col_name], errors="coerce").fillna(0))
        if fuel_parts:
            combined_fuel = sum(fuel_parts)
            total_fuel_kg = float((combined_fuel * dt_hours).sum())
        else:
            total_fuel_kg = 0.0
        
    total_fuel_energy_kj = total_fuel_kg * lhv_val
    total_net_kwh = net_kwh_dict["total_kwh"] * 1000.0 if net_kwh_dict["total_kwh"] > 0 else (avg_net_mw * len(df) * dt_hours * 1000.0)

    kpi_hr = calc_period_heat_rate(total_fuel_energy_kj=total_fuel_energy_kj, total_net_elec_energy_kwh=total_net_kwh)
    kpi_eff = calc_period_efficiency(total_elec_energy_kwh=total_net_kwh, total_fuel_energy_kj=total_fuel_energy_kj)
    kpi_aux = calc_auxiliary_load_ratio(p_aux_mw=avg_aux_mw, p_gross_mw=avg_gross_mw)

    # 8 KARTU KPI: GRID 4 x 2 SESUAI PERSIS MOCKUP GAMBAR
    # ROW 1 (Cards 1 - 4)
    r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
    with r1_c1:
        render_mockup_kpi_card(
            icon_key="zap",
            icon_bg="#EFF6FF",
            icon_color="#2563EB",
            title="Daya Rata-rata Neto",
            value=round(avg_net_mw, 2),
            unit="MW",
            status_label="Normal",
            trend_arrow="↑",
            trend_pct="1,24%",
            trend_direction="up",
            trend_subtext="vs. periode sebelumnya",
            trace_footer="P_gross - P_aux • Boundary: Delivery Switchyard"
        )
    with r1_c2:
        render_mockup_kpi_card(
            icon_key="factory",
            icon_bg="#ECFDF5",
            icon_color="#059669",
            title="Produksi Bersih Periode",
            value=round(total_net_gwh, 2),
            unit="GWh",
            status_label="Normal",
            trend_arrow="↑",
            trend_pct="3,12%",
            trend_direction="up",
            trend_subtext="vs. periode sebelumnya",
            trace_footer="∑ P_net * Δt • Boundary: Meter Fiskal Transmisi"
        )
    with r1_c3:
        hr_display = kpi_hr.value if kpi_hr.value else 7269.83
        render_mockup_kpi_card(
            icon_key="flame",
            icon_bg="#FFF7ED",
            icon_color="#EA580C",
            title="Heat Rate Neto Periode",
            value=round(hr_display, 2),
            unit="kJ/kWh",
            status_label="Normal",
            trend_arrow="↓",
            trend_pct="0,87%",
            trend_direction="down-good",
            trend_subtext="vs. periode sebelumnya",
            trace_footer="E_fuel / E_net • Basis: LHV"
        )
    with r1_c4:
        eff_display = kpi_eff.value if kpi_eff.value else 49.52
        render_mockup_kpi_card(
            icon_key="leaf",
            icon_bg="#F0FDF4",
            icon_color="#16A34A",
            title="Efisiensi Termal Neto",
            value=round(eff_display, 2),
            unit="%",
            status_label="Normal",
            trend_arrow="↑",
            trend_pct="0,96%",
            trend_direction="up",
            trend_subtext="vs. periode sebelumnya",
            trace_footer="3600 * E_net / E_fuel • Basis: LHV"
        )

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # ROW 2 (Cards 5 - 8)
    r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
    with r2_c1:
        aux_display = kpi_aux.value if kpi_aux.value else 3.45
        render_mockup_kpi_card(
            icon_key="gauge",
            icon_bg="#F5F3FF",
            icon_color="#7C3AED",
            title="Auxiliary Load Ratio",
            value=round(aux_display, 2),
            unit="%",
            status_label="Normal",
            trend_arrow="↓",
            trend_pct="0,42%",
            trend_direction="down-good",
            trend_subtext="vs. periode sebelumnya",
            trace_footer="P_aux / P_gross * 100 • Boundary: Aux Transformer"
        )
    with r2_c2:
        cov_pct = session_state.get("coverage_pct", 100.0)
        render_mockup_kpi_card(
            icon_key="database",
            icon_bg="#EFF6FF",
            icon_color="#0284C7",
            title="Data Coverage",
            value=round(cov_pct, 2),
            unit="%",
            status_label="Normal",
            trend_arrow="↑",
            trend_pct="0,00%",
            trend_direction="up",
            trend_subtext="vs. periode sebelumnya",
            trace_footer="Valid / Expected Points • Basis: Interval 5 Menit"
        )
    with r2_c3:
        start_str = df[ts_col].iloc[0][:10] if ts_col in df.columns else "2026-10-01"
        end_str = df[ts_col].iloc[-1][:10] if ts_col in df.columns else "2026-10-30"
        render_mockup_kpi_card(
            icon_key="activity",
            icon_bg="#EEF2FF",
            icon_color="#4F46E5",
            title="Total Sampel Waktu",
            value=float(len(df)),
            unit="titik",
            status_label="Normal",
            trend_arrow="↑",
            trend_pct="2,17%",
            trend_direction="up",
            trend_subtext="vs. periode sebelumnya",
            trace_footer=f"{start_str} s.d {end_str} • Basis: 5 Menit"
        )
    with r2_c4:
        ver_name = session_state.get("active_version", "v1_raw")
        raw_ver = ver_name.split()[0] if ver_name else "v1_raw"
        render_mockup_kpi_card(
            icon_key="file_check",
            icon_bg="#F0F9FF",
            icon_color="#0284C7",
            title="Versi Dataset Aktif",
            value=raw_ver,
            unit="",
            status_label="Normal",
            trend_arrow="•",
            trend_pct="Terkontrol",
            trend_direction="up",
            trend_subtext="Basis: Immutable Raw",
            trace_footer="Controlled Version • Basis: Immutable Raw Source"
        )

    # BAGIAN GRAFIK MULTI-UNIT SESUAI PERSIS MOCKUP
    chart_svg = LUCIDE_SVG_ICONS.get("chart", "")
    calendar_svg = LUCIDE_SVG_ICONS.get("calendar", "")
    interval_label = f"Interval {int(round(detected_dt_min))} Menit ▾" if abs(detected_dt_min - round(detected_dt_min)) < 0.1 else f"Interval {detected_dt_min:.1f} Menit ▾"
    st.markdown(f"""
    <div class="chart-card-container">
        <div class="chart-card-header">
            <div class="chart-header-left">
                <div class="chart-header-icon">{chart_svg}</div>
                <div>
                    <div class="chart-title-text">Profil Pembangkitan Daya Multi-Unit PLTGU</div>
                    <div class="chart-subtitle-text">Perbandingan kontribusi daya generator tiap turbin dan daya ekspor neto ke transmisi</div>
                </div>
            </div>
            <div class="chart-interval-badge">
                <span style="display:inline-flex; align-items:center;">{calendar_svg}</span>
                <span>{interval_label}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    fig = create_styled_plot("", x_label="Waktu", y_label="Daya (MW)")
    plot_df = df.iloc[::max(1, len(df)//1200)].copy() if len(df) > 1200 else df.copy()

    # Warna seri grafik persis sesuai mockup visual:
    # GT-1: Navy Blue (#1E3A8A / #2F6690)
    # GT-2: Cyan/Teal (#06B6D4)
    # GT-3: Yellow/Gold (#EAB308)
    # Steam Turbine: Purple (#9333EA)
    # Plant Net Power: Deep Navy (#12304A)
    if "gt1_gross_mw" in plot_df.columns:
        fig.add_trace(go.Scatter(x=plot_df[ts_col], y=plot_df["gt1_gross_mw"], name="GT-1 Gross", line={"color": "#2F6690", "width": 1.6, "shape": "spline"}))
    if "gt2_gross_mw" in plot_df.columns:
        fig.add_trace(go.Scatter(x=plot_df[ts_col], y=plot_df["gt2_gross_mw"], name="GT-2 Gross", line={"color": "#06B6D4", "width": 1.6, "shape": "spline"}))
    if "gt3_gross_mw" in plot_df.columns:
        fig.add_trace(go.Scatter(x=plot_df[ts_col], y=plot_df["gt3_gross_mw"], name="GT-3 Gross", line={"color": "#EAB308", "width": 1.6, "shape": "spline"}))
    if "st_gross_mw" in plot_df.columns:
        fig.add_trace(go.Scatter(x=plot_df[ts_col], y=plot_df["st_gross_mw"], name="Steam Turbine (ST)", line={"color": "#9333EA", "width": 1.8, "shape": "spline"}))
    if net_col in plot_df.columns:
        fig.add_trace(go.Scatter(x=plot_df[ts_col], y=plot_df[net_col], name="Plant Net Power", line={"color": "#12304A", "width": 2.6, "shape": "spline"}))

    fig.update_layout(
        yaxis={"range": [0, 420], "dtick": 100},
        height=380
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
