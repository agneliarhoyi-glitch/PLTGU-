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

    # Auto-detect mapping jika ada tag DCS yang cocok
    from ui.pages.p03_tag_mapping import auto_detect_tag_mapping
    mapping = auto_detect_tag_mapping(df.columns, mapping)
    session_state["tag_mapping"] = mapping

    ts_col = mapping.get("timestamp", "timestamp")
    plot_df = df.iloc[::max(1, len(df)//1200)].copy() if len(df) > 1200 else df.copy()

    def _val(canon_key, fallback_names, default=0.0):
        col = mapping.get(canon_key)
        if col and col in df.columns:
            s = pd.to_numeric(df[col], errors="coerce").dropna()
            if not s.empty:
                return float(s.mean())
        for f in fallback_names:
            if f in df.columns:
                s = pd.to_numeric(df[f], errors="coerce").dropna()
                if not s.empty:
                    return float(s.mean())
        return default

    def _col(canon_key, fallback_names):
        col = mapping.get(canon_key)
        if col and col in plot_df.columns:
            return col
        for f in fallback_names:
            if f in plot_df.columns:
                return f
        return None

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
        p_gt1 = _val("gt1_power", ["GTDL-19173", "gt1_gross_mw", "gt1_power"])
        pr_gt1 = _val("gt1_comp_p_out", ["GTDL-19149", "gt1_comp_pr"], default=14.2)
        t_gt1 = _val("gt1_exhaust_temp", ["GTDL-19071", "gt1_exhaust_temp_c"])
        rpm_gt1 = _val("1SGA-RPM", ["1SGA-RPM"], default=3000.0)
        
        # GT-2
        p_gt2 = _val("gt2_power", ["GTDL-29173", "gt2_gross_mw", "gt2_power"])
        pr_gt2 = _val("gt2_comp_p_out", ["GTDL-29149", "gt2_comp_pr"], default=14.1)
        t_gt2 = _val("gt2_exhaust_temp", ["GTDL-29071", "gt2_exhaust_temp_c"])
        rpm_gt2 = _val("2SGA-RPM", ["2SGA-RPM"], default=3000.0)
        
        # GT-3
        p_gt3 = _val("gt3_power", ["GTDL-39173", "gt3_gross_mw", "gt3_power"])
        pr_gt3 = _val("gt3_comp_p_out", ["GTDL-39149", "gt3_comp_pr"], default=14.3)
        t_gt3 = _val("gt3_exhaust_temp", ["GTDL-39071", "gt3_exhaust_temp_c"])
        rpm_gt3 = _val("3SGA-RPM", ["3SGA-RPM"], default=3000.0)

        with c_gt1:
            st.markdown(f"<div style='border-top: 3.5px solid {EQUIPMENT_COLORS['GT-1']}; padding-top:6px; margin-bottom:8px; font-weight:700; color:#0F172A;'>GT-1</div>", unsafe_allow_html=True)
            render_mockup_kpi_card(icon_key="zap", icon_bg="#EFF6FF", icon_color="#2563EB", title="Daya Gross GT-1", value=f"{p_gt1:,.1f}", unit="MW", status_label="Normal", trend_arrow="•", trend_pct="Generator", trend_subtext="aktif", trace_footer="Daya rata-rata periode terpilih")
            st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
            render_mockup_kpi_card(icon_key="gauge", icon_bg="#EFF6FF", icon_color="#2563EB", title="Pressure Ratio GT-1", value=f"{pr_gt1:,.2f}", unit="PR", status_label="Normal", trend_arrow="•", trend_pct="Kompresor", trend_subtext="P_out / P_in", trace_footer="Kompresi aksial tingkat")
            st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
            render_mockup_kpi_card(icon_key="activity", icon_bg="#EFF6FF", icon_color="#2563EB", title="Kecepatan Poros GT-1", value=f"{rpm_gt1:,.1f}", unit="RPM", status_label="Normal", trend_arrow="•", trend_pct="1SGA-RPM", trend_subtext="50 Hz grid", trace_footer="Kecepatan putaran poros sinkron")

        with c_gt2:
            st.markdown(f"<div style='border-top: 3.5px solid {EQUIPMENT_COLORS['GT-2']}; padding-top:6px; margin-bottom:8px; font-weight:700; color:#0F172A;'>GT-2</div>", unsafe_allow_html=True)
            render_mockup_kpi_card(icon_key="zap", icon_bg="#F0FDFA", icon_color="#0D9488", title="Daya Gross GT-2", value=f"{p_gt2:,.1f}", unit="MW", status_label="Normal", trend_arrow="•", trend_pct="Generator", trend_subtext="aktif", trace_footer="Daya rata-rata periode terpilih")
            st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
            render_mockup_kpi_card(icon_key="gauge", icon_bg="#F0FDFA", icon_color="#0D9488", title="Pressure Ratio GT-2", value=f"{pr_gt2:,.2f}", unit="PR", status_label="Normal", trend_arrow="•", trend_pct="Kompresor", trend_subtext="P_out / P_in", trace_footer="Kompresi aksial tingkat")
            st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
            render_mockup_kpi_card(icon_key="activity", icon_bg="#F0FDFA", icon_color="#0D9488", title="Kecepatan Poros GT-2", value=f"{rpm_gt2:,.1f}", unit="RPM", status_label="Normal", trend_arrow="•", trend_pct="2SGA-RPM", trend_subtext="50 Hz grid", trace_footer="Kecepatan putaran poros sinkron")

        with c_gt3:
            st.markdown(f"<div style='border-top: 3.5px solid {EQUIPMENT_COLORS['GT-3']}; padding-top:6px; margin-bottom:8px; font-weight:700; color:#0F172A;'>GT-3</div>", unsafe_allow_html=True)
            render_mockup_kpi_card(icon_key="zap", icon_bg="#FFFBEB", icon_color="#D97706", title="Daya Gross GT-3", value=f"{p_gt3:,.1f}", unit="MW", status_label="Normal", trend_arrow="•", trend_pct="Generator", trend_subtext="aktif", trace_footer="Daya rata-rata periode terpilih")
            st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
            render_mockup_kpi_card(icon_key="gauge", icon_bg="#FFFBEB", icon_color="#D97706", title="Pressure Ratio GT-3", value=f"{pr_gt3:,.2f}", unit="PR", status_label="Normal", trend_arrow="•", trend_pct="Kompresor", trend_subtext="P_out / P_in", trace_footer="Kompresi aksial tingkat")
            st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
            render_mockup_kpi_card(icon_key="activity", icon_bg="#FFFBEB", icon_color="#D97706", title="Kecepatan Poros GT-3", value=f"{rpm_gt3:,.1f}", unit="RPM", status_label="Normal", trend_arrow="•", trend_pct="3SGA-RPM", trend_subtext="50 Hz grid", trace_footer="Kecepatan putaran poros sinkron")

        # Expander Sensor Tambahan GT (Generator Field & Aux Instruments)
        gt_aux_tags = [c for c in ["1SGGFI-1001", "1SGGFI-1002", "2SGGFI-2001", "2SGGFI-2002", "3SGGFI-3001", "3SGGFI-3002", "GTDL-19079", "GTDL-19081", "GTDL-29079", "GTDL-29081", "GTDL-39079", "GTDL-39081"] if c in df.columns]
        if gt_aux_tags:
            with st.expander("Sensor Diagnostik Tambahan Gas Turbine (Arus Eksitasi & Temperatur Casing)", icon=":material/speed:", expanded=False):
                aux_data = []
                for t in gt_aux_tags:
                    s = pd.to_numeric(df[t], errors="coerce").dropna()
                    unit_str = "A" if "GFI" in t else ("°C" if "079" in t or "081" in t else "eng. unit")
                    desc_str = "Arus Eksitasi / Medan Generator" if "GFI" in t else "Temperatur Casing / Sudu Tingkat"
                    aux_data.append({
                        "Tag DCS": t,
                        "Sub-Sistem": "GT-1" if t.startswith("1") or "-19" in t else ("GT-2" if t.startswith("2") or "-29" in t else "GT-3"),
                        "Deskripsi Instrumen": desc_str,
                        "Satuan": unit_str,
                        "Rata-rata": f"{float(s.mean()):,.2f}" if not s.empty else "-",
                        "Min": f"{float(s.min()):,.2f}" if not s.empty else "-",
                        "Maks": f"{float(s.max()):,.2f}" if not s.empty else "-"
                    })
                st.dataframe(pd.DataFrame(aux_data), width="stretch", hide_index=True)

        # Grafik Perbandingan Pressure Ratio Kompresor
        st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
        fig_pr = create_styled_plot("Tren Compressor Pressure Ratio Antar-GT", x_label="Waktu", y_label="Pressure Ratio (P_out,abs / P_in,abs)")
        col_pr1 = _col("gt1_comp_p_out", ["gt1_comp_pr", "GTDL-19149"])
        col_pr2 = _col("gt2_comp_p_out", ["gt2_comp_pr", "GTDL-29149"])
        col_pr3 = _col("gt3_comp_p_out", ["gt3_comp_pr", "GTDL-39149"])
        if col_pr1 and col_pr1 in plot_df.columns:
            fig_pr.add_trace(go.Scatter(x=plot_df[ts_col], y=plot_df[col_pr1], name="GT-1 PR", line={"color": EQUIPMENT_COLORS["GT-1"], "width": 1.5}))
        if col_pr2 and col_pr2 in plot_df.columns:
            fig_pr.add_trace(go.Scatter(x=plot_df[ts_col], y=plot_df[col_pr2], name="GT-2 PR", line={"color": EQUIPMENT_COLORS["GT-2"], "width": 1.5}))
        if col_pr3 and col_pr3 in plot_df.columns:
            fig_pr.add_trace(go.Scatter(x=plot_df[ts_col], y=plot_df[col_pr3], name="GT-3 PR", line={"color": EQUIPMENT_COLORS["GT-3"], "width": 1.5}))
        st.plotly_chart(fig_pr, width="stretch")

    # 2. TAB HRSG
    with tab_hrsg:
        render_section_header(
            title="Kinerja Sisi Gas & Sisi Air/Uap HRSG (1-3)",
            subtitle="Pemisahan analisis termal gas buang, tekanan HP drum, dan laju produksi main steam per boiler",
            icon_key="flame",
            badge_text="3 x HRSG Units",
            icon_bg="#FEF2F2",
            icon_color="#EF4444"
        )
        
        c_h1, c_h2, c_h3 = st.columns(3, gap="medium")
        h1_steam = _val("hrsg1_steam_flow", ["hrsg1_main_steam_flow_kg_s", "hrsg1_steam_flow", "1SGAFT-1001"])
        h1_stack = _val("hrsg1_stack_temp", ["hrsg1_stack_temp_c", "hrsg1_stack_temp", "1SGATE-1019"])
        h1_drum_p = _val("1SGAPT-100HP", ["1SGAPT-100HP", "1SGAPT-1001"], default=54.0)
        
        h2_steam = _val("hrsg2_steam_flow", ["hrsg2_main_steam_flow_kg_s", "hrsg2_steam_flow", "2SGAFT-2001"])
        h2_stack = _val("hrsg2_stack_temp", ["hrsg2_stack_temp_c", "hrsg2_stack_temp", "2SGATE-2019"])
        h2_drum_p = _val("2SGAPT-100HP", ["2SGAPT-100HP", "2SGAPT-2001"], default=53.8)
        
        h3_steam = _val("hrsg3_steam_flow", ["hrsg3_main_steam_flow_kg_s", "hrsg3_steam_flow", "3SGAFT-3001"])
        h3_stack = _val("hrsg3_stack_temp", ["hrsg3_stack_temp_c", "hrsg3_stack_temp", "3SGATE-3019"])
        h3_drum_p = _val("3SGAPT-100HP", ["3SGAPT-100HP", "3SGAPT-3001"], default=54.2)

        with c_h1:
            st.markdown(f"<div style='border-top: 3.5px solid {EQUIPMENT_COLORS['HRSG-1']}; padding-top:6px; margin-bottom:8px; font-weight:700; color:#0F172A;'>HRSG-1</div>", unsafe_allow_html=True)
            render_mockup_kpi_card(icon_key="droplet", icon_bg="#EFF6FF", icon_color="#2563EB", title="Main Steam HRSG-1", value=f"{h1_steam:,.1f}", unit="kg/s", status_label="Normal", trend_arrow="•", trend_pct="Steam Flow", trend_subtext="uap utama", trace_footer="Produksi uap HP HRSG-1")
            st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
            render_mockup_kpi_card(icon_key="gauge", icon_bg="#EFF6FF", icon_color="#2563EB", title="Tekanan HP Drum 1", value=f"{h1_drum_p:,.1f}", unit="bar(g)", status_label="Normal", trend_arrow="•", trend_pct="1SGAPT-100HP", trend_subtext="drum uap", trace_footer="Tekanan bejana uap tingkat tinggi")
            st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
            render_mockup_kpi_card(icon_key="wind", icon_bg="#F8FAFC", icon_color="#475569", title="Stack Gas Temp", value=f"{h1_stack:,.1f}", unit="°C", status_label="Normal", trend_arrow="•", trend_pct="Cerobong", trend_subtext="stack 1", trace_footer="Temperatur gas buang akhir")

        with c_h2:
            st.markdown(f"<div style='border-top: 3.5px solid {EQUIPMENT_COLORS['HRSG-2']}; padding-top:6px; margin-bottom:8px; font-weight:700; color:#0F172A;'>HRSG-2</div>", unsafe_allow_html=True)
            render_mockup_kpi_card(icon_key="droplet", icon_bg="#ECFDF5", icon_color="#059669", title="Main Steam HRSG-2", value=f"{h2_steam:,.1f}", unit="kg/s", status_label="Normal", trend_arrow="•", trend_pct="Steam Flow", trend_subtext="uap utama", trace_footer="Produksi uap HP HRSG-2")
            st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
            render_mockup_kpi_card(icon_key="gauge", icon_bg="#ECFDF5", icon_color="#059669", title="Tekanan HP Drum 2", value=f"{h2_drum_p:,.1f}", unit="bar(g)", status_label="Normal", trend_arrow="•", trend_pct="2SGAPT-100HP", trend_subtext="drum uap", trace_footer="Tekanan bejana uap tingkat tinggi")
            st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
            render_mockup_kpi_card(icon_key="wind", icon_bg="#F8FAFC", icon_color="#475569", title="Stack Gas Temp", value=f"{h2_stack:,.1f}", unit="°C", status_label="Normal", trend_arrow="•", trend_pct="Cerobong", trend_subtext="stack 2", trace_footer="Temperatur gas buang akhir")

        with c_h3:
            st.markdown(f"<div style='border-top: 3.5px solid {EQUIPMENT_COLORS['HRSG-3']}; padding-top:6px; margin-bottom:8px; font-weight:700; color:#0F172A;'>HRSG-3</div>", unsafe_allow_html=True)
            render_mockup_kpi_card(icon_key="droplet", icon_bg="#FFFBEB", icon_color="#D97706", title="Main Steam HRSG-3", value=f"{h3_steam:,.1f}", unit="kg/s", status_label="Normal", trend_arrow="•", trend_pct="Steam Flow", trend_subtext="uap utama", trace_footer="Produksi uap HP HRSG-3")
            st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
            render_mockup_kpi_card(icon_key="gauge", icon_bg="#FFFBEB", icon_color="#D97706", title="Tekanan HP Drum 3", value=f"{h3_drum_p:,.1f}", unit="bar(g)", status_label="Normal", trend_arrow="•", trend_pct="3SGAPT-100HP", trend_subtext="drum uap", trace_footer="Tekanan bejana uap tingkat tinggi")
            st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
            render_mockup_kpi_card(icon_key="wind", icon_bg="#F8FAFC", icon_color="#475569", title="Stack Gas Temp", value=f"{h3_stack:,.1f}", unit="°C", status_label="Normal", trend_arrow="•", trend_pct="Cerobong", trend_subtext="stack 3", trace_footer="Temperatur gas buang akhir")

        # Expander Rincian Sensor Tekanan Drum & Temperatur Metal HRSG
        hrsg_extra_tags = [c for c in df.columns if any(c.startswith(p) for p in ["1SGAPT-", "2SGAPT-", "3SGAPT-", "1SGATE-", "2SGATE-", "3SGATE-"])]
        if hrsg_extra_tags:
            with st.expander(f"Profil Multi-Titik Sensor HRSG 1-3 ({len(hrsg_extra_tags)} Tag Tekanan & Temperatur Terbaca)", icon=":material/thermometer:", expanded=False):
                hrsg_summary = []
                for t in hrsg_extra_tags:
                    s = pd.to_numeric(df[t], errors="coerce").dropna()
                    unit_str = "bar(g)" if "PT" in t else "°C"
                    sub_unit = "HRSG-1" if t.startswith("1") else ("HRSG-2" if t.startswith("2") else "HRSG-3")
                    hrsg_summary.append({
                        "Tag DCS": t,
                        "Unit": sub_unit,
                        "Parameter": "Tekanan Drum / Header" if "PT" in t else "Temperatur Drum / Superheater",
                        "Satuan": unit_str,
                        "Rata-rata": f"{float(s.mean()):,.2f}" if not s.empty else "-",
                        "Min": f"{float(s.min()):,.2f}" if not s.empty else "-",
                        "Maks": f"{float(s.max()):,.2f}" if not s.empty else "-"
                    })
                st.dataframe(pd.DataFrame(hrsg_summary), width="stretch", height=260, hide_index=True)

        st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
        fig_steam = create_styled_plot("Profil Laju Alir Uap Utama (Main Steam Flow) 3 HRSG", x_label="Waktu", y_label="Laju Alir (kg/s)")
        col_s1 = _col("hrsg1_steam_flow", ["hrsg1_main_steam_flow_kg_s", "hrsg1_steam_flow", "1SGAFT-1001"])
        col_s2 = _col("hrsg2_steam_flow", ["hrsg2_main_steam_flow_kg_s", "hrsg2_steam_flow", "2SGAFT-2001"])
        col_s3 = _col("hrsg3_steam_flow", ["hrsg3_main_steam_flow_kg_s", "hrsg3_steam_flow", "3SGAFT-3001"])
        if col_s1 and col_s1 in plot_df.columns:
            fig_steam.add_trace(go.Scatter(x=plot_df[ts_col], y=plot_df[col_s1], name="HRSG-1 Steam", line={"color": EQUIPMENT_COLORS["HRSG-1"]}))
        if col_s2 and col_s2 in plot_df.columns:
            fig_steam.add_trace(go.Scatter(x=plot_df[ts_col], y=plot_df[col_s2], name="HRSG-2 Steam", line={"color": EQUIPMENT_COLORS["HRSG-2"]}))
        if col_s3 and col_s3 in plot_df.columns:
            fig_steam.add_trace(go.Scatter(x=plot_df[ts_col], y=plot_df[col_s3], name="HRSG-3 Steam", line={"color": EQUIPMENT_COLORS["HRSG-3"]}))
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
        
        st_mw = _val("st_power", ["STDL-20106", "st_gross_mw", "st_power", "st_load"])
        default_flow = (h1_steam + h2_steam + h3_steam) if (h1_steam or h2_steam or h3_steam) else 0.0
        st_flow = _val("st_inlet_steam_flow", ["st_inlet_steam_flow_kg_s", "st_inlet_flow"], default=default_flow)
        ms_p = _val("main_steam_p", ["main_steam_pressure_bar", "main_steam_p", "ms_press_bar", "4HRAPT-0005"])
        ms_t = _val("main_steam_t", ["main_steam_temp_c", "main_steam_t", "ms_temp_c", "4HRATE-0002", "STDL-20025"])
        st_t_in = _val("STDL-20025", ["STDL-20025"], default=516.5)

        c_st1, c_st2, c_st3, c_st4 = st.columns(4)
        with c_st1:
            render_mockup_kpi_card(icon_key="zap", icon_bg="#FAF5FF", icon_color="#9333EA", title="Daya Gross ST", value=f"{st_mw:,.1f}", unit="MW", status_label="Normal", trend_arrow="•", trend_pct="STDL-20106", trend_subtext="aktif", trace_footer="Daya gross rata-rata ST")
        with c_st2:
            render_mockup_kpi_card(icon_key="droplet", icon_bg="#EFF6FF", icon_color="#2563EB", title="Total Steam ST", value=f"{st_flow:,.1f}", unit="kg/s", status_label="Normal", trend_arrow="•", trend_pct="Aggregated", trend_subtext="inlet", trace_footer="∑ Steam HRSG 1-3 masuk ST")
        with c_st3:
            render_mockup_kpi_card(icon_key="gauge", icon_bg="#F0FDFA", icon_color="#0D9488", title="Tekanan Uap Utama", value=f"{ms_p:,.1f}", unit="bar(a)", status_label="Normal", trend_arrow="•", trend_pct="4HRAPT-0005", trend_subtext="tekanan", trace_footer="Header uap tekanan tinggi")
        with c_st4:
            render_mockup_kpi_card(icon_key="flame", icon_bg="#FFFBEB", icon_color="#D97706", title="Temperatur Inlet ST", value=f"{st_t_in:,.1f}", unit="°C", status_label="Normal", trend_arrow="•", trend_pct="STDL-20025", trend_subtext="inlet casing", trace_footer="Suhu uap masuk sudu ST")

        # Expander Sensor Bantu Steam Turbine
        st_extra_tags = [c for c in ["STDL-20025", "STDL-20049", "STDL-20094", "STDL-20096"] if c in df.columns]
        if st_extra_tags:
            with st.expander("Sensor Instrumen Tambahan Steam Turbine (STDL)", icon=":material/tune:", expanded=False):
                st_data = []
                for t in st_extra_tags:
                    s = pd.to_numeric(df[t], errors="coerce").dropna()
                    st_data.append({
                        "Tag DCS": t,
                        "Deskripsi": "Temperatur / Tekanan Tingkat Sudu ST",
                        "Rata-rata": f"{float(s.mean()):,.2f}" if not s.empty else "-",
                        "Min": f"{float(s.min()):,.2f}" if not s.empty else "-",
                        "Maks": f"{float(s.max()):,.2f}" if not s.empty else "-"
                    })
                st.dataframe(pd.DataFrame(st_data), width="stretch", hide_index=True)

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
        
        p_cond = _val("condenser_p", ["condenser_pressure_bar", "condenser_p", "p_condenser"])
        cw_in = _val("cw_in_t", ["4HRCTE-0002", "cw_inlet_temp_c", "cw_in_t", "t_cw_in"])
        cw_out = _val("cw_out_t", ["4HRCTE-0003", "cw_outlet_temp_c", "cw_out_t", "t_cw_out"])
        cw_m = _val("cw_flow", ["cw_flow_kg_s", "cw_flow", "flow_cw"])
        
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

        # Expander Sensor Tambahan Saluran Header & Air Pendingin
        bop_extra_tags = [c for c in ["4HRATE-0002", "4HRATE-0003", "4HRCTE-0001", "4HRCTE-0004", "4HRAPT-0005"] if c in df.columns]
        if bop_extra_tags:
            with st.expander("Sensor Tambahan Saluran Uap Header & Sirkulasi Pendingin (4HR)", icon=":material/water_drop:", expanded=False):
                bop_data = []
                for t in bop_extra_tags:
                    s = pd.to_numeric(df[t], errors="coerce").dropna()
                    unit_str = "°C" if "TE" in t else ("bar(a)" if "PT" in t else "eng. unit")
                    bop_data.append({
                        "Tag DCS": t,
                        "Sub-Sistem": "Balance of Plant (BOP)",
                        "Deskripsi": "Temperatur Header / Suhu Menara Pendingin" if "TE" in t else "Tekanan Header Uap",
                        "Satuan": unit_str,
                        "Rata-rata": f"{float(s.mean()):,.2f}" if not s.empty else "-",
                        "Min": f"{float(s.min()):,.2f}" if not s.empty else "-",
                        "Maks": f"{float(s.max()):,.2f}" if not s.empty else "-"
                    })
                st.dataframe(pd.DataFrame(bop_data), width="stretch", hide_index=True)
