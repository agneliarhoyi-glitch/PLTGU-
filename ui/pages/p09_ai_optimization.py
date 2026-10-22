"""
Halaman 9: Deteksi Anomali AI & Shortlist Optimasi (Machine Learning Screening)
Menggabungkan model Unsupervised Isolation Forest, filter persistensi (debounce), hipotesis rekayasa, dan alur peninjauan engineer.
Ultra-modern UI dengan kartu KPI presisi, alur review interaktif, dan grafik bukti tren kejadian.
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
    render_status_badge, 
    create_styled_plot,
    render_empty_dataset_notice,
    LUCIDE_SVG_ICONS
)
from core.ai_anomaly import AnomalyDetector
from core.config import AI_DISCLAIMER, EQUIPMENT_COLORS

def render(session_state):
    render_synthetic_banner(session_state.get("is_synthetic", True))
    
    render_page_hero(
        title="Deteksi Anomali AI & Shortlist Optimasi",
        subtitle="Penyaringan anomali operasional menggunakan Unsupervised Isolation Forest, filter persistensi (debounce), dan alur peninjauan engineer.",
        badge_text="Machine Learning Screening",
        badge_icon="bot"
    )
    
    # Catatan Transparansi Wajib (Halaman 15 Poin 9)
    bot_icon = LUCIDE_SVG_ICONS.get("bot", "")
    st.markdown(f"""
    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:12px 18px; margin-bottom:18px; display:flex; align-items:center; gap:12px;">
        <div style="color:#2563EB;">{bot_icon}</div>
        <div style="font-size:12.5px; color:#475569; line-height:1.5;">
            <b style="color:#0F172A;">Prinsip Transparansi AI (Section K Protocol):</b> {AI_DISCLAIMER}
        </div>
    </div>
    """, unsafe_allow_html=True)

    df = session_state.get("active_df")
    mapping = session_state.get("tag_mapping", {})
    
    if df is None or df.empty:
        render_empty_dataset_notice(mode="card", key_suffix="p09")
        return

    ts_col = mapping.get("timestamp", "timestamp")
    
    def _resolve_feature_cols(pairs):
        res = []
        for canon, fallbacks in pairs:
            c = mapping.get(canon)
            if c and c in df.columns:
                res.append(c)
                continue
            for fb in fallbacks:
                if fb in df.columns:
                    res.append(fb)
                    break
        return res

    # Inisialisasi temuan di session state jika belum ada
    if "ai_findings" not in session_state or session_state.get("re_run_ai", False):
        with st.spinner("Menjalankan model deteksi anomali pada fitur operasi..."):
            detector = AnomalyDetector(contamination=0.02, persistence_window=3)
            
            # Deteksi pada GT-2 (yang memiliki simulated compressor fouling)
            gt2_features = _resolve_feature_cols([
                ("gt2_power", ["GTDL-29173", "gt2_gross_mw", "gt2_power"]),
                ("gt2_comp_p_out", ["GTDL-29149", "gt2_comp_pr"]),
                ("gt2_exhaust_temp", ["GTDL-29071", "gt2_exhaust_temp_c"]),
                ("gt2_fuel_flow", ["CFGAAI-0005", "GTDL-29161", "gt2_fuel_flow_kg_h", "gt2_fuel_flow_kg_s"])
            ])
            findings_gt2 = detector.detect_anomalies(df, timestamp_col=ts_col, feature_cols=gt2_features, equipment_name="GT-2")
            
            # Deteksi pada GT-1
            gt1_features = _resolve_feature_cols([
                ("gt1_power", ["GTDL-19173", "gt1_gross_mw", "gt1_power"]),
                ("gt1_comp_p_out", ["GTDL-19149", "gt1_comp_pr"]),
                ("gt1_exhaust_temp", ["GTDL-19071", "gt1_exhaust_temp_c"]),
                ("gt1_fuel_flow", ["CFGAAI-0004", "GTDL-19161", "gt1_fuel_flow_kg_h", "gt1_fuel_flow_kg_s"])
            ])
            findings_gt1 = detector.detect_anomalies(df, timestamp_col=ts_col, feature_cols=gt1_features, equipment_name="GT-1")
            
            # Deteksi pada HRSG
            hrsg_features = _resolve_feature_cols([
                ("hrsg1_steam_flow", ["hrsg1_main_steam_flow_kg_s", "hrsg1_steam_flow"]),
                ("hrsg1_stack_temp", ["hrsg1_stack_temp_c", "hrsg1_stack_temp"]),
                ("hrsg2_steam_flow", ["hrsg2_main_steam_flow_kg_s", "hrsg2_steam_flow"]),
                ("hrsg2_stack_temp", ["hrsg2_stack_temp_c", "hrsg2_stack_temp"])
            ])
            findings_hrsg = detector.detect_anomalies(df, timestamp_col=ts_col, feature_cols=hrsg_features, equipment_name="HRSG")
            
            session_state["ai_findings"] = findings_gt2 + findings_gt1 + findings_hrsg
            session_state["re_run_ai"] = False

    findings = session_state.get("ai_findings", [])
    
    render_section_header(
        title="Ringkasan Screening Anomali Machine Learning",
        subtitle="Agregasi temuan anomali persisten dari model Isolation Forest setelah melalui filter debounce",
        icon_key="bot",
        badge_text="Isolation Forest"
    )

    # METRIK RINGKASAN TEMUAN
    total_findings = len(findings)
    unreviewed = sum(1 for f in findings if f.review_status == "Belum Ditinjau")
    confirmed = sum(1 for f in findings if f.review_status == "Dikonfirmasi")
    false_positives = sum(1 for f in findings if f.review_status == "False Positive")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_mockup_kpi_card(icon_key="bot", icon_bg="#EFF6FF", icon_color="#2563EB", title="Total Indikasi Anomali", value=f"{total_findings}", unit="kejadian", status_label="Normal", trend_arrow="•", trend_pct="Screened", trend_subtext="debouced", trace_footer="Isolation Forest + Persistensi 3 sampel")
    with c2:
        render_mockup_kpi_card(icon_key="alert_triangle", icon_bg="#FFFBEB", icon_color="#D97706", title="Belum Ditinjau", value=f"{unreviewed}", unit="kejadian", status_label="Normal" if unreviewed==0 else "Warning", trend_arrow="•", trend_pct="Pending", trend_subtext="antrian", trace_footer="Menunggu konfirmasi engineer")
    with c3:
        render_mockup_kpi_card(icon_key="check_circle", icon_bg="#ECFDF5", icon_color="#059669", title="Dikonfirmasi Valid", value=f"{confirmed}", unit="kejadian", status_label="Normal", trend_arrow="✓", trend_pct="Verified", trend_subtext="lapangan", trace_footer="Tervalidasi sesuai kondisi fisik")
    with c4:
        render_mockup_kpi_card(icon_key="shield", icon_bg="#F8FAFC", icon_color="#64748B", title="False Positive", value=f"{false_positives}", unit="kejadian", status_label="Normal", trend_arrow="•", trend_pct="Cleared", trend_subtext="variasi wajar", trace_footer="Bukan kerusakan operasional")

    render_section_header(
        title="Daftar Temuan & Alur Verifikasi Engineer",
        subtitle="Tinjau hipotesis awal model AI, skor keyakinan, dan tetapkan rekomendasi pemeliharaan",
        icon_key="sparkles",
        badge_text="Engineer Workflow",
        icon_bg="#FAF5FF",
        icon_color="#9333EA"
    )
    
    if not findings:
        st.success("Tidak ada anomali persisten yang terdeteksi pada dataset terpilih.", icon=":material/check_circle:")
        return

    # Filter temuan
    f_eq, f_status = st.columns([1, 1], gap="medium")
    with f_eq:
        eq_filter = st.multiselect("Filter Peralatan:", options=list(set(f.equipment for f in findings)), default=list(set(f.equipment for f in findings)))
    with f_status:
        st_filter = st.multiselect("Filter Status Review:", ["Belum Ditinjau", "Dikonfirmasi", "False Positive", "Perlu Investigasi"], default=["Belum Ditinjau", "Dikonfirmasi", "Perlu Investigasi"])

    filtered_findings = [f for f in findings if f.equipment in eq_filter and f.review_status in st_filter]

    # Iterasi setiap temuan dengan panel peninjauan
    for idx, item in enumerate(filtered_findings):
        sev_color = "#EF4444" if item.confidence_severity == "Anomali Perlu Ditinjau" else ("#F59E0B" if item.confidence_severity == "Perhatian" else "#3B82F6")
        sev_bg = "#FEF2F2" if item.confidence_severity == "Anomali Perlu Ditinjau" else ("#FFFBEB" if item.confidence_severity == "Perhatian" else "#EFF6FF")
        sev_border = "#FCA5A5" if item.confidence_severity == "Anomali Perlu Ditinjau" else ("#FDE68A" if item.confidence_severity == "Perhatian" else "#BFDBFE")
        badge_sev = f'<span style="background:{sev_bg}; color:{sev_color}; border:1px solid {sev_border}; font-size:11.5px; font-weight:700; padding:2px 8px; border-radius:6px; display:inline-flex; align-items:center; gap:5px;"><span style="width:6px; height:6px; border-radius:50%; background:{sev_color};"></span>{item.confidence_severity}</span>'
        
        status_review_colors = {
            "Belum Ditinjau": "#64748B",
            "Dikonfirmasi": "#167D70",
            "False Positive": "#586574",
            "Perlu Investigasi": "#946200"
        }
        rev_color = status_review_colors.get(item.review_status, "#64748B")
        
        with st.expander(f"[{item.id}] {item.equipment} — {item.finding_type} ({item.timestamp_start} s.d {item.timestamp_end})", icon=":material/manage_search:", expanded=(idx == 0)):
            m_col1, m_col2, m_col3 = st.columns([1.5, 1.5, 1])
            with m_col1:
                st.markdown(f"**Tingkat Keparahan:** {badge_sev}", unsafe_allow_html=True)
                st.markdown(f"**Tag Terkait:** `{', '.join(item.tags)}`")
                st.markdown(f"**Durasi Kejadian:** `{item.duration_min:.0f} menit`")
            with m_col2:
                st.markdown(f"**Nilai Aktual (Median):** `{item.actual_value}`")
                st.markdown(f"**Nilai Baseline/Expected:** `{item.expected_value}`")
                st.markdown(f"**Deviasi:** `{(item.deviation_pct or 0.0):+.1f}%`")
            with m_col3:
                st.markdown(f"**Status Saat Ini:** <span style='font-weight:700; color:{rev_color};'>{item.review_status}</span>", unsafe_allow_html=True)
                st.markdown(f"**Confidence Score:** `{item.confidence_score*100:.0f}%`")
                
            brain_svg = LUCIDE_SVG_ICONS.get("brain", "")
            sliders_svg = LUCIDE_SVG_ICONS.get("sliders", "")
            st.markdown(f"""
            <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:8px; padding:10px 14px; margin-top:10px; display:flex; align-items:flex-start; gap:10px;">
                <div style="color:#16A34A; margin-top:2px;">{brain_svg}</div>
                <div style="font-size:12.5px; color:#166534; line-height:1.5;">
                    <b style="color:#14532D;">Hipotesis AI:</b> {item.hypothesis}
                </div>
            </div>
            <div style="background:#EFF6FF; border:1px solid #BFDBFE; border-radius:8px; padding:10px 14px; margin-top:8px; display:flex; align-items:flex-start; gap:10px;">
                <div style="color:#2563EB; margin-top:2px;">{sliders_svg}</div>
                <div style="font-size:12.5px; color:#1E40AF; line-height:1.5;">
                    <b style="color:#1E3A8A;">Rekomendasi Tindak Lanjut:</b> {item.recommended_action}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Workflow Form Review
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            with st.form(f"review_form_{item.id}"):
                c_sel, c_note = st.columns([1, 2])
                with c_sel:
                    new_status = st.selectbox("Keputusan Review:", ["Belum Ditinjau", "Dikonfirmasi", "False Positive", "Perlu Investigasi"], index=["Belum Ditinjau", "Dikonfirmasi", "False Positive", "Perlu Investigasi"].index(item.review_status))
                with c_note:
                    new_note = st.text_input("Catatan Teknis Engineer:", value=item.review_notes, placeholder="Contoh: Dikonfirmasi filter inlet kotor saat inspeksi lapangan.")
                    
                if st.form_submit_button("Perbarui Status Review", icon=":material/check_circle:", type="primary"):
                    item.review_status = new_status
                    item.review_notes = new_note
                    st.toast(f"Status temuan {item.id} diperbarui menjadi '{new_status}'!", icon=":material/check_circle:")
                    st.rerun()

    # GRAFIK BUKTI DATA (EVIDENCE CHART)
    render_section_header(
        title="Bukti Data Tren Kejadian (Evidence Chart)",
        subtitle="Visualisasi perbandingan deret waktu sebelum, saat, dan sesudah anomali untuk verifikasi independen",
        icon_key="chart",
        badge_text="Independent Validation"
    )
    
    if "gt2_comp_pr" in df.columns and "gt1_comp_pr" in df.columns:
        fig_ev = create_styled_plot("Bukti Penurunan Pressure Ratio GT-2 (Kandidat Fouling) vs GT-1 (Normal Baseline)", x_label="Waktu", y_label="Pressure Ratio")
        plot_slice = df.iloc[::max(1, len(df)//1000)].copy() if len(df) > 1000 else df.copy()
        fig_ev.add_trace(go.Scatter(x=plot_slice[ts_col], y=plot_slice["gt1_comp_pr"], name="GT-1 Baseline PR", line={"color": EQUIPMENT_COLORS["GT-1"], "dash": "dot"}))
        fig_ev.add_trace(go.Scatter(x=plot_slice[ts_col], y=plot_slice["gt2_comp_pr"], name="GT-2 PR (Mengalami Penurunan)", line={"color": EQUIPMENT_COLORS["GT-2"], "width": 2}))
        st.plotly_chart(fig_ev, width="stretch")
