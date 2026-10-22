"""
Halaman 8: Evaluasi Neraca Massa & Neraca Energi (Mass & Energy Conservation)
Pemilihan boundary sistem, verifikasi kelengkapan aliran masuk/keluar, residual massa & energi, serta evaluasi residual relatif.
Ultra-modern UI dengan kartu KPI presisi, indikator status termal, dan penelusuran aliran Section K.
"""

import streamlit as st
import pandas as pd
from ui.components import (
    render_synthetic_banner, 
    render_page_hero, 
    render_mockup_kpi_card, 
    render_section_header,
    render_status_badge,
    render_empty_dataset_notice,
    LUCIDE_SVG_ICONS
)
from core.mass_energy_balance import evaluate_mass_balance, evaluate_energy_balance_hrsg, evaluate_condenser_balance
from core.calculation_engine import calc_cooling_water_duty

def render(session_state):
    render_synthetic_banner(session_state.get("is_synthetic", True))
    
    render_page_hero(
        title="Evaluasi Neraca Massa & Neraca Energi",
        subtitle="Verifikasi hukum kekekalan massa dan energi per batas sistem (boundary) terpilih dengan evaluasi residual relatif.",
        badge_text="Thermodynamic Balance",
        badge_icon="scale"
    )
    
    df = session_state.get("active_df")
    mapping = session_state.get("tag_mapping", {})
    
    if df is None or df.empty:
        render_empty_dataset_notice(mode="card", key_suffix="p08")
        return

    # Pilihan Boundary
    render_section_header(
        title="Definisi Batas Sistem (Boundary Selection)",
        subtitle="Pilih batas termodinamika terisolasi untuk menguji hukum kekekalan massa dan energi",
        icon_key="scale",
        badge_text="Boundary Control"
    )
    
    boundaries = [
        "Siklus Uap Utama (HRSG 1-3 Steam Output vs ST Steam Input)",
        "Neraca Energi HRSG-1 (Gas Buang vs Air/Uap)",
        "Neraca Panas Kondensor (Sisi Uap vs Sisi Cooling Water)"
    ]
    selected_boundary = st.selectbox("Pilih Batas Sistem (Boundary) untuk Dievaluasi:", boundaries, label_visibility="collapsed")
    
    confirm_boundary = st.checkbox("Saya mengonfirmasi bahwa seluruh aliran masuk dan keluar pada boundary ini telah teridentifikasi dan diisolasi.", value=True)
    
    if not confirm_boundary:
        st.info("Harap centang konfirmasi boundary di atas untuk menampilkan hasil perhitungan neraca.", icon=":material/info:")
        return

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

    # 1. EVALUASI NERACA MASSA SIKLUS UAP
    if selected_boundary == boundaries[0]:
        render_section_header(
            title="Neraca Massa: Siklus Uap Utama (Steam Cycle Header)",
            subtitle="Membandingkan agregasi total uap diproduksi 3 HRSG dengan laju alir uap yang masuk ke Steam Turbine",
            icon_key="droplet",
            badge_text="Mass Conservation",
            icon_bg="#EFF6FF",
            icon_color="#2563EB"
        )
        
        h1_s = _val("hrsg1_steam_flow", ["hrsg1_main_steam_flow_kg_s", "hrsg1_steam_flow"], default=35.0)
        h2_s = _val("hrsg2_steam_flow", ["hrsg2_main_steam_flow_kg_s", "hrsg2_steam_flow"], default=35.0)
        h3_s = _val("hrsg3_steam_flow", ["hrsg3_main_steam_flow_kg_s", "hrsg3_steam_flow"], default=35.0)
        st_s = _val("st_inlet_steam_flow", ["st_inlet_steam_flow_kg_s", "st_inlet_flow"], default=(h1_s + h2_s + h3_s))
        
        inlets = {"Main Steam HRSG-1": h1_s, "Main Steam HRSG-2": h2_s, "Main Steam HRSG-3": h3_s}
        outlets = {"Steam Masuk ST": st_s}
        
        res = evaluate_mass_balance("Steam Header to ST Inlet", inlets, outlets, flow_unit="kg/s")
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            render_mockup_kpi_card(icon_key="droplet", icon_bg="#EFF6FF", icon_color="#2563EB", title="Total Aliran Masuk", value=f"{res['total_inlet']:,.1f}", unit="kg/s", status_label="Normal", trend_arrow="•", trend_pct="Inlet", trend_subtext="∑ 3 HRSG", trace_footer="Total produksi uap HRSG 1-3")
        with c2:
            render_mockup_kpi_card(icon_key="gauge", icon_bg="#FAF5FF", icon_color="#9333EA", title="Total Aliran Keluar", value=f"{res['total_outlet']:,.1f}", unit="kg/s", status_label="Normal", trend_arrow="•", trend_pct="Outlet", trend_subtext="ST Inlet", trace_footer="Aliran uap masuk turbin uap")
        with c3:
            render_mockup_kpi_card(icon_key="scale", icon_bg="#F0FDFA", icon_color="#0D9488", title="Residual Absolut", value=f"{res['residual_abs']:,.2f}", unit="kg/s", status_label="Normal" if res["status"]=="VALID" else "Warning", trend_arrow="•", trend_pct="Selisih", trend_subtext="Inlet - Outlet", trace_footer="Residual neraca massa absolut")
        with c4:
            render_mockup_kpi_card(icon_key="activity", icon_bg="#ECFDF5", icon_color="#059669", title="Residual Relatif", value=f"{res['residual_pct']:,.2f}", unit="%", status_label="Normal" if res["status"]=="VALID" else "Warning", trend_arrow="•", trend_pct="Toleransi < 5%", trend_subtext="kriteria lolos", trace_footer="Residual relatif terhadap total inlet")

        # Rincian Aliran Dalam Card Modern
        with st.container(border=True):
            st.markdown("<div style='font-size:14px; font-weight:700; color:#0F172A; margin-bottom:12px;'>Rincian Aliran Massa Boundary:</div>", unsafe_allow_html=True)
            col_in, col_out = st.columns(2, gap="large")
            with col_in:
                st.markdown("<b style='color:#2563EB;'>Aliran Masuk (Inlet Streams):</b>", unsafe_allow_html=True)
                for k, v in inlets.items():
                    st.markdown(f"- {k}: <b>{v:,.2f} kg/s</b>", unsafe_allow_html=True)
            with col_out:
                st.markdown("<b style='color:#9333EA;'>Aliran Keluar (Outlet Streams):</b>", unsafe_allow_html=True)
                for k, v in outlets.items():
                    st.markdown(f"- {k}: <b>{v:,.2f} kg/s</b>", unsafe_allow_html=True)

    # 2. EVALUASI NERACA ENERGI HRSG-1
    elif selected_boundary == boundaries[1]:
        render_section_header(
            title="Neraca Energi: HRSG-1 (Gas Buang vs Air/Uap)",
            subtitle="Pelepasan kalor gas buang turbin gas GT-1 dibandingkan dengan penyerapan panas pembentukan steam",
            icon_key="flame",
            badge_text="Energy Conservation",
            icon_bg="#FEF2F2",
            icon_color="#EF4444"
        )
        
        t_in = _val("gt1_exhaust_temp", ["GTDL-19071", "gt1_exhaust_temp_c"], default=540.0)
        t_out = _val("hrsg1_stack_temp", ["hrsg1_stack_temp_c", "hrsg1_stack_temp"], default=115.0)
        flue_flow = 278.0
        s_flow = _val("hrsg1_steam_flow", ["hrsg1_main_steam_flow_kg_s", "hrsg1_steam_flow"], default=35.0)
        fw_flow = _val("hrsg1_fw_flow", ["hrsg1_feedwater_flow_kg_s", "hrsg1_fw_flow"], default=s_flow)
        ms_p = _val("main_steam_p", ["main_steam_pressure_bar", "main_steam_p"], default=65.0)
        ms_t = _val("main_steam_t", ["main_steam_temp_c", "main_steam_t"], default=510.0)
        fw_p = _val("feedwater_p", ["feedwater_pressure_bar"], default=75.0)
        fw_t = _val("feedwater_t", ["feedwater_temp_c"], default=135.0)

        res_hrsg = evaluate_energy_balance_hrsg(
            gas_inlet_t_c=t_in,
            gas_outlet_t_c=t_out,
            flue_gas_flow_kg_s=flue_flow,
            steam_flow_kg_s=s_flow,
            feedwater_flow_kg_s=fw_flow,
            steam_p_bar=ms_p,
            steam_t_c=ms_t,
            fw_p_bar=fw_p,
            fw_t_c=fw_t
        )

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            q_gas_mw = res_hrsg["q_gas_kw"] / 1000.0 if res_hrsg["q_gas_kw"] else 0.0
            render_mockup_kpi_card(icon_key="flame", icon_bg="#FEF2F2", icon_color="#EF4444", title="Duty Kalor Gas Buang", value=f"{q_gas_mw:,.1f}", unit="MWth", status_label="Normal", trend_arrow="•", trend_pct="Q_flue", trend_subtext="gas input", trace_footer="m_gas * Cp * ΔT_gas")
        with c2:
            q_stm_mw = res_hrsg["q_steam_kw"] / 1000.0 if res_hrsg["q_steam_kw"] else 0.0
            render_mockup_kpi_card(icon_key="droplet", icon_bg="#EFF6FF", icon_color="#2563EB", title="Duty Kalor Air/Uap", value=f"{q_stm_mw:,.1f}", unit="MWth", status_label="Normal", trend_arrow="•", trend_pct="Q_steam", trend_subtext="diserap", trace_footer="m_s*h_s - m_fw*h_fw")
        with c3:
            res_mw = res_hrsg["residual_kw"] / 1000.0 if res_hrsg["residual_kw"] else 0.0
            render_mockup_kpi_card(icon_key="scale", icon_bg="#FFFBEB", icon_color="#D97706", title="Residual Kalor (Loss)", value=f"{res_mw:,.1f}", unit="MWth", status_label="Normal" if res_hrsg["status"]=="VALID" else "Warning", trend_arrow="•", trend_pct="Disipasi", trend_subtext="losses", trace_footer="Q_gas - Q_steam (Radiasi & Dinding)")
        with c4:
            render_mockup_kpi_card(icon_key="activity", icon_bg="#ECFDF5", icon_color="#059669", title="Residual Relatif", value=f"{res_hrsg['residual_pct']:,.2f}", unit="%", status_label="Normal" if res_hrsg["status"]=="VALID" else "Warning", trend_arrow="•", trend_pct="Toleransi < 7%", trend_subtext="efisiensi transfer", trace_footer="Residual / Q_gas * 100")

    # 3. EVALUASI NERACA KONDENSOR
    else:
        render_section_header(
            title="Neraca Panas: Surface Condenser",
            subtitle="Pelepasan kalor kondensasi uap buang turbin ke sirkulasi air pendingin (Cooling Water)",
            icon_key="database",
            badge_text="Heat Sink Balance",
            icon_bg="#F0FDFA",
            icon_color="#0D9488"
        )
        
        cw_in = _val("cw_in_t", ["4HRCTE-0002", "cw_inlet_temp_c", "cw_in_t"], default=28.0)
        cw_out = _val("cw_out_t", ["4HRCTE-0003", "cw_outlet_temp_c", "cw_out_t"], default=36.5)
        cw_m = _val("cw_flow", ["cw_flow_kg_s", "cw_flow"], default=8500.0)
        q_cw = calc_cooling_water_duty(cw_m, cw_in, cw_out).value
        
        s_flow = _val("st_inlet_steam_flow", ["st_inlet_steam_flow_kg_s", "st_inlet_flow"], default=105.0)
        p_cond = _val("condenser_p", ["condenser_pressure_bar", "condenser_p"], default=0.075)
        t_hw = _val("hotwell_temp", ["hotwell_temp_c"], default=40.0)
        
        res_cond = evaluate_condenser_balance(q_cw, s_flow, p_cond, t_hw)
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            render_mockup_kpi_card(icon_key="droplet", icon_bg="#F0FDFA", icon_color="#0D9488", title="Duty Pendinginan CW", value=f"{q_cw / 1000.0:,.1f}", unit="MWth", status_label="Normal", trend_arrow="•", trend_pct="Cooling Duty", trend_subtext="CW", trace_footer="m_CW * Cp * ΔT")
        with c2:
            q_c_mw = res_cond["q_cond_steam_kw"] / 1000.0 if res_cond["q_cond_steam_kw"] else 0.0
            render_mockup_kpi_card(icon_key="gauge", icon_bg="#EFF6FF", icon_color="#2563EB", title="Duty Kondensasi Uap", value=f"{q_c_mw:,.1f}", unit="MWth", status_label="Normal", trend_arrow="•", trend_pct="Latent Heat", trend_subtext="steam", trace_footer="m_s * (h_exh - h_cond)")
        with c3:
            res_c_mw = res_cond["residual_kw"] / 1000.0 if res_cond["residual_kw"] else 0.0
            render_mockup_kpi_card(icon_key="scale", icon_bg="#FFFBEB", icon_color="#D97706", title="Residual Kalor Kondensor", value=f"{res_c_mw:,.1f}", unit="MWth", status_label="Normal" if res_cond["status"]=="VALID" else "Warning", trend_arrow="•", trend_pct="Selisih", trend_subtext="neraca", trace_footer="Q_steam - Q_CW")
        with c4:
            render_mockup_kpi_card(icon_key="activity", icon_bg="#ECFDF5", icon_color="#059669", title="Residual Relatif", value=f"{res_cond['residual_pct']:,.2f}", unit="%", status_label="Normal" if res_cond["status"]=="VALID" else "Warning", trend_arrow="•", trend_pct="Toleransi < 8%", trend_subtext="vakum", trace_footer="Residual / Q_steam * 100")
