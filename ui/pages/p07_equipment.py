"""
Halaman 7: Analisis Kinerja Spesifik Peralatan (Component Thermal Performance)
Tab khusus untuk Gas Turbine (GT1-3), HRSG (1-3), Steam Turbine (ST), dan Condenser / Cooling Water.
Ultra-modern UI dengan kartu KPI presisi, grafik profil daya, dan perumusan IAPWS-IF97.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from ui.components import (
    render_synthetic_banner, 
    render_page_hero, 
    render_mockup_kpi_card, 
    render_section_header,
    create_styled_plot,
    render_empty_dataset_notice,
    LUCIDE_SVG_ICONS
)
from core.config import EQUIPMENT_COLORS
from core.calculation_engine import (
    calc_fuel_heat_input,
    calc_compressor_pressure_ratio,
    calc_cooling_water_duty
)
from core.steam_tables import get_steam_enthalpy, get_water_enthalpy

def render(session_state):
    render_synthetic_banner(session_state.get("is_synthetic", True))
    
    render_page_hero(
        title="Analisis Kinerja Sub-Sistem Peralatan",
        subtitle="Evaluasi termal mendalam per unit: 3 Gas Turbine, 3 HRSG, 1 Steam Turbine, dan Condenser/Cooling Water System.",
        badge_text="Component Performance",
        badge_icon="cpu"
    )
    
    df = session_state.get("active_df")
    mapping = session_state.get("tag_mapping", {})
    
    if df is None or df.empty:
        render_empty_dataset_notice(mode="card", key_suffix="p07")
        return

    ts_col = mapping.get("timestamp", "timestamp")
    plot_df = df.iloc[::max(1, len(df)//1200)].copy() if len(df) > 1200 else df.copy()

    tab_gt, tab_hrsg, tab_st, tab_cond = st.tabs([
        "Gas Turbine (GT 1-3)", 
        "HRSG (1-3)", 
        "Steam Turbine (ST)", 
        "Condenser & Cooling Water"
    ])

    # 1. TAB GAS TURBINE
    with tab_gt:
        render_section_header(
            title="Perbandingan Kinerja Gas Turbine (GT-1, GT-2, GT-3)",
            subtitle="Evaluasi rata-rata daya aktif, rasio kompresi udara (PR), dan temperatur flange gas buang",
            icon_key="zap",
            badge_text="3 x GT Units"
        )
        
        # Sub-kolom metrik 3 GT
        c_gt1, c_gt2, c_gt3 = st.columns(3, gap="medium")
        
        # GT-1
        p_gt1 = df["gt1_gross_mw"].mean() if "gt1_gross_mw" in df.columns else 0.0
        pr_gt1 = df["gt1_comp_pr"].mean() if "gt1_comp_pr" in df.columns else 0.0
        t_gt1 = df["gt1_exhaust_temp_c"].mean() if "gt1_exhaust_temp_c" in df.columns else 0.0
        
        # GT-2
        p_gt2 = df["gt2_gross_mw"].mean() if "gt2_gross_mw" in df.columns else 0.0
        pr_gt2 = df["gt2_comp_pr"].mean() if "gt2_comp_pr" in df.columns else 0.0
        t_gt2 = df["gt2_exhaust_temp_c"].mean() if "gt2_exhaust_temp_c" in df.columns else 0.0
        
        # GT-3
        p_gt3 = df["gt3_gross_mw"].mean() if "gt3_gross_mw" in df.columns else 0.0
        pr_gt3 = df["gt3_comp_pr"].mean() if "gt3_comp_pr" in df.columns else 0.0
        t_gt3 = df["gt3_exhaust_temp_c"].mean() if "gt3_exhaust_temp_c" in df.columns else 0.0

        with c_gt1:
            st.markdown(f"<div style='border-top: 3.5px solid {EQUIPMENT_COLORS['GT-1']}; padding-top:6px; margin-bottom:8px; font-weight:700; color:#0F172A;'>GT-1 (Biru Baja)</div>", unsafe_allow_html=True)
            render_mockup_kpi_card(icon_key="zap", icon_bg="#EFF6FF", icon_color="#2563EB", title="Daya Gross GT-1", value=f"{p_gt1:,.1f}", unit="MW", status_label="Normal", trend_arrow="•", trend_pct="Generator", trend_subtext="aktif", trace_footer="Daya rata-rata periode terpilih")
            st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
            render_mockup_kpi_card(icon_key="gauge", icon_bg="#EFF6FF", icon_color="#2563EB", title="Pressure Ratio GT-1", value=f"{pr_gt1:,.2f}", unit="PR", status_label="Normal", trend_arrow="•", trend_pct="Kompresor", trend_subtext="P_out / P_in", trace_footer="Kompresi aksial tingkat")

        with c_gt2:
            st.markdown(f"<div style='border-top: 3.5px solid {EQUIPMENT_COLORS['GT-2']}; padding-top:6px; margin-bottom:8px; font-weight:700; color:#0F172A;'>GT-2 (Teal)</div>", unsafe_allow_html=True)
            render_mockup_kpi_card(icon_key="zap", icon_bg="#F0FDFA", icon_color="#0D9488", title="Daya Gross GT-2", value=f"{p_gt2:,.1f}", unit="MW", status_label="Normal", trend_arrow="•", trend_pct="Generator", trend_subtext="aktif", trace_footer="Daya rata-rata periode terpilih")
            st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
            render_mockup_kpi_card(icon_key="gauge", icon_bg="#F0FDFA", icon_color="#0D9488", title="Pressure Ratio GT-2", value=f"{pr_gt2:,.2f}", unit="PR", status_label="Normal", trend_arrow="•", trend_pct="Kompresor", trend_subtext="P_out / P_in", trace_footer="Kompresi aksial tingkat")

        with c_gt3:
            st.markdown(f"<div style='border-top: 3.5px solid {EQUIPMENT_COLORS['GT-3']}; padding-top:6px; margin-bottom:8px; font-weight:700; color:#0F172A;'>GT-3 (Kuning Pasir)</div>", unsafe_allow_html=True)
            render_mockup_kpi_card(icon_key="zap", icon_bg="#FFFBEB", icon_color="#D97706", title="Daya Gross GT-3", value=f"{p_gt3:,.1f}", unit="MW", status_label="Normal", trend_arrow="•", trend_pct="Generator", trend_subtext="aktif", trace_footer="Daya rata-rata periode terpilih")
            st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
            render_mockup_kpi_card(icon_key="gauge", icon_bg="#FFFBEB", icon_color="#D97706", title="Pressure Ratio GT-3", value=f"{pr_gt3:,.2f}", unit="PR", status_label="Normal", trend_arrow="•", trend_pct="Kompresor", trend_subtext="P_out / P_in", trace_footer="Kompresi aksial tingkat")

        # Grafik Perbandingan Pressure Ratio Kompresor
        st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
        fig_pr = create_styled_plot("Tren Compressor Pressure Ratio Antar-GT", x_label="Waktu", y_label="Pressure Ratio (P_out,abs / P_in,abs)")
        if "gt1_comp_pr" in plot_df.columns:
            fig_pr.add_trace(go.Scatter(x=plot_df[ts_col], y=plot_df["gt1_comp_pr"], name="GT-1 PR", line={"color": EQUIPMENT_COLORS["GT-1"], "width": 1.5}))
        if "gt2_comp_pr" in plot_df.columns:
            fig_pr.add_trace(go.Scatter(x=plot_df[ts_col], y=plot_df["gt2_comp_pr"], name="GT-2 PR", line={"color": EQUIPMENT_COLORS["GT-2"], "width": 1.5}))
        if "gt3_comp_pr" in plot_df.columns:
            fig_pr.add_trace(go.Scatter(x=plot_df[ts_col], y=plot_df["gt3_comp_pr"], name="GT-3 PR", line={"color": EQUIPMENT_COLORS["GT-3"], "width": 1.5}))
        st.plotly_chart(fig_pr, width="stretch")

    # 2. TAB HRSG
    with tab_hrsg:
        render_section_header(
            title="Kinerja Sisi Gas & Sisi Air/Uap HRSG (1-3)",
            subtitle="Pemisahan analisis termal gas buang dan laju produksi main steam per boiler",
            icon_key="flame",
            badge_text="3 x HRSG Units",
            icon_bg="#FEF2F2",
            icon_color="#EF4444"
        )
        
        c_h1, c_h2, c_h3 = st.columns(3, gap="medium")
        h1_steam = df["hrsg1_main_steam_flow_kg_s"].mean() if "hrsg1_main_steam_flow_kg_s" in df.columns else 0.0
        h1_stack = df["hrsg1_stack_temp_c"].mean() if "hrsg1_stack_temp_c" in df.columns else 0.0
        
        h2_steam = df["hrsg2_main_steam_flow_kg_s"].mean() if "hrsg2_main_steam_flow_kg_s" in df.columns else 0.0
        h2_stack = df["hrsg2_stack_temp_c"].mean() if "hrsg2_stack_temp_c" in df.columns else 0.0
        
        h3_steam = df["hrsg3_main_steam_flow_kg_s"].mean() if "hrsg3_main_steam_flow_kg_s" in df.columns else 0.0
        h3_stack = df["hrsg3_stack_temp_c"].mean() if "hrsg3_stack_temp_c" in df.columns else 0.0

        with c_h1:
            st.markdown(f"<div style='border-top: 3.5px solid {EQUIPMENT_COLORS['HRSG-1']}; padding-top:6px; margin-bottom:8px; font-weight:700; color:#0F172A;'>HRSG-1 (Biru Abu)</div>", unsafe_allow_html=True)
            render_mockup_kpi_card(icon_key="droplet", icon_bg="#EFF6FF", icon_color="#2563EB", title="Main Steam HRSG-1", value=f"{h1_steam:,.1f}", unit="kg/s", status_label="Normal", trend_arrow="•", trend_pct="Steam Flow", trend_subtext="uap utama", trace_footer="Produksi uap HP HRSG-1")
            st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
            render_mockup_kpi_card(icon_key="wind", icon_bg="#F8FAFC", icon_color="#475569", title="Stack Gas Temp", value=f"{h1_stack:,.1f}", unit="°C", status_label="Normal", trend_arrow="•", trend_pct="Cerobong", trend_subtext="stack 1", trace_footer="Temperatur gas buang akhir")

        with c_h2:
            st.markdown(f"<div style='border-top: 3.5px solid {EQUIPMENT_COLORS['HRSG-2']}; padding-top:6px; margin-bottom:8px; font-weight:700; color:#0F172A;'>HRSG-2 (Hijau)</div>", unsafe_allow_html=True)
            render_mockup_kpi_card(icon_key="droplet", icon_bg="#ECFDF5", icon_color="#059669", title="Main Steam HRSG-2", value=f"{h2_steam:,.1f}", unit="kg/s", status_label="Normal", trend_arrow="•", trend_pct="Steam Flow", trend_subtext="uap utama", trace_footer="Produksi uap HP HRSG-2")
            st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
            render_mockup_kpi_card(icon_key="wind", icon_bg="#F8FAFC", icon_color="#475569", title="Stack Gas Temp", value=f"{h2_stack:,.1f}", unit="°C", status_label="Normal", trend_arrow="•", trend_pct="Cerobong", trend_subtext="stack 2", trace_footer="Temperatur gas buang akhir")

        with c_h3:
            st.markdown(f"<div style='border-top: 3.5px solid {EQUIPMENT_COLORS['HRSG-3']}; padding-top:6px; margin-bottom:8px; font-weight:700; color:#0F172A;'>HRSG-3 (Oranye)</div>", unsafe_allow_html=True)
            render_mockup_kpi_card(icon_key="droplet", icon_bg="#FFFBEB", icon_color="#D97706", title="Main Steam HRSG-3", value=f"{h3_steam:,.1f}", unit="kg/s", status_label="Normal", trend_arrow="•", trend_pct="Steam Flow", trend_subtext="uap utama", trace_footer="Produksi uap HP HRSG-3")
            st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
            render_mockup_kpi_card(icon_key="wind", icon_bg="#F8FAFC", icon_color="#475569", title="Stack Gas Temp", value=f"{h3_stack:,.1f}", unit="°C", status_label="Normal", trend_arrow="•", trend_pct="Cerobong", trend_subtext="stack 3", trace_footer="Temperatur gas buang akhir")

        st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
        fig_steam = create_styled_plot("Profil Laju Alir Uap Utama (Main Steam Flow) 3 HRSG", x_label="Waktu", y_label="Laju Alir (kg/s)")
        if "hrsg1_main_steam_flow_kg_s" in plot_df.columns:
            fig_steam.add_trace(go.Scatter(x=plot_df[ts_col], y=plot_df["hrsg1_main_steam_flow_kg_s"], name="HRSG-1 Steam", line={"color": EQUIPMENT_COLORS["HRSG-1"]}))
        if "hrsg2_main_steam_flow_kg_s" in plot_df.columns:
            fig_steam.add_trace(go.Scatter(x=plot_df[ts_col], y=plot_df["hrsg2_main_steam_flow_kg_s"], name="HRSG-2 Steam", line={"color": EQUIPMENT_COLORS["HRSG-2"]}))
        if "hrsg3_main_steam_flow_kg_s" in plot_df.columns:
            fig_steam.add_trace(go.Scatter(x=plot_df[ts_col], y=plot_df["hrsg3_main_steam_flow_kg_s"], name="HRSG-3 Steam", line={"color": EQUIPMENT_COLORS["HRSG-3"]}))
        st.plotly_chart(fig_steam, width="stretch")

    # 3. TAB STEAM TURBINE
    with tab_st:
        render_section_header(
            title="Kinerja Steam Turbine (ST) & Siklus Uap Utama",
            subtitle="Pembangkitan daya ST dari kombinasi agregasi 3 aliran uap HRSG",
            icon_key="gauge",
            badge_text="Steam Cycle",
            icon_bg="#FAF5FF",
            icon_color="#9333EA"
        )
        
        st_mw = df["st_gross_mw"].mean() if "st_gross_mw" in df.columns else 0.0
        st_flow = df["st_inlet_steam_flow_kg_s"].mean() if "st_inlet_steam_flow_kg_s" in df.columns else 0.0
        ms_p = df["main_steam_pressure_bar"].mean() if "main_steam_pressure_bar" in df.columns else 0.0
        ms_t = df["main_steam_temp_c"].mean() if "main_steam_temp_c" in df.columns else 0.0

        c_st1, c_st2, c_st3, c_st4 = st.columns(4)
        with c_st1:
            render_mockup_kpi_card(icon_key="zap", icon_bg="#FAF5FF", icon_color="#9333EA", title="Daya Gross ST", value=f"{st_mw:,.1f}", unit="MW", status_label="Normal", trend_arrow="•", trend_pct="Generator ST", trend_subtext="aktif", trace_footer="Daya gross rata-rata ST")
        with c_st2:
            render_mockup_kpi_card(icon_key="droplet", icon_bg="#EFF6FF", icon_color="#2563EB", title="Total Steam ST", value=f"{st_flow:,.1f}", unit="kg/s", status_label="Normal", trend_arrow="•", trend_pct="Aggregated", trend_subtext="inlet", trace_footer="∑ Steam HRSG 1-3 masuk ST")
        with c_st3:
            render_mockup_kpi_card(icon_key="gauge", icon_bg="#F0FDFA", icon_color="#0D9488", title="Tekanan Uap Utama", value=f"{ms_p:,.1f}", unit="bar(a)", status_label="Normal", trend_arrow="•", trend_pct="HP Header", trend_subtext="tekanan", trace_footer="Header uap tekanan tinggi")
        with c_st4:
            render_mockup_kpi_card(icon_key="flame", icon_bg="#FFFBEB", icon_color="#D97706", title="Temperatur Uap Utama", value=f"{ms_t:,.1f}", unit="°C", status_label="Normal", trend_arrow="•", trend_pct="Superheat", trend_subtext="temperatur", trace_footer="Header uap temperatur tinggi")

        # Entalpi uap IAPWS-IF97
        if ms_p > 0 and ms_t > 0:
            h_inlet = get_steam_enthalpy(ms_p, ms_t)
            sparkles_svg = LUCIDE_SVG_ICONS.get("sparkles", "")
            st.markdown(f"""
            <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:10px; padding:12px 18px; margin-top:16px; display:flex; align-items:center; gap:10px;">
                <div style="color:#16A34A;">{sparkles_svg}</div>
                <div style="font-size:12.5px; color:#15803D;">
                    <b>Formulasi Termodinamika IAPWS-IF97:</b> Entalpi uap utama masuk ST terhitung sebesar <b>{h_inlet:,.1f} kJ/kg</b> pada kondisi operasional {ms_p:.1f} bar(a) dan {ms_t:.1f} °C.
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 4. TAB CONDENSER & CW
    with tab_cond:
        render_section_header(
            title="Kinerja Kondensor & Cooling Water System",
            subtitle="Evaluasi kedalaman vakum kondensor permukaan dan pembuangan panas melalui sirkulasi cooling water",
            icon_key="database",
            badge_text="Heat Sink",
            icon_bg="#F0FDFA",
            icon_color="#0D9488"
        )
        
        p_cond = df["condenser_pressure_bar"].mean() if "condenser_pressure_bar" in df.columns else 0.0
        cw_in = df["cw_inlet_temp_c"].mean() if "cw_inlet_temp_c" in df.columns else 0.0
        cw_out = df["cw_outlet_temp_c"].mean() if "cw_outlet_temp_c" in df.columns else 0.0
        cw_m = df["cw_flow_kg_s"].mean() if "cw_flow_kg_s" in df.columns else 0.0
        
        q_cw_res = calc_cooling_water_duty(m_dot_cw_kg_s=cw_m, t_in_c=cw_in, t_out_c=cw_out)
        delta_cw = (cw_out - cw_in) if (cw_out and cw_in) else 0.0
        
        c_cd1, c_cd2, c_cd3, c_cd4 = st.columns(4)
        with c_cd1:
            render_mockup_kpi_card(icon_key="gauge", icon_bg="#EFF6FF", icon_color="#2563EB", title="Tekanan Kondensor", value=f"{p_cond:,.4f}", unit="bar(a)", status_label="Normal", trend_arrow="•", trend_pct="Vakum", trend_subtext="absolut", trace_footer="Vakum ruang kondensor")
        with c_cd2:
            render_mockup_kpi_card(icon_key="activity", icon_bg="#F0FDFA", icon_color="#0D9488", title="Kenaikan Temp CW (ΔT)", value=f"{delta_cw:,.2f}", unit="°C", status_label="Normal", trend_arrow="•", trend_pct="Delta Temp", trend_subtext="T_out - T_in", trace_footer="Rentang pendinginan CW")
        with c_cd3:
            render_mockup_kpi_card(icon_key="droplet", icon_bg="#ECFDF5", icon_color="#059669", title="Laju Alir CW", value=f"{cw_m:,.0f}", unit="kg/s", status_label="Normal", trend_arrow="•", trend_pct="CW Pump", trend_subtext="sirkulasi", trace_footer="Sirkulasi air pendingin")
        with c_cd4:
            duty_mw = (q_cw_res.value / 1000.0) if q_cw_res and q_cw_res.value else 0.0
            render_mockup_kpi_card(icon_key="flame", icon_bg="#FFFBEB", icon_color="#D97706", title="Heat Duty CW", value=f"{duty_mw:,.1f}", unit="MWth", status_label="Normal", trend_arrow="•", trend_pct="Pelepasan", trend_subtext="panas", trace_footer="m_dot * Cp * ΔT (Air Pendingin)")
