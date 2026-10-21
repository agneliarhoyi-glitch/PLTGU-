"""
Halaman 4: Validasi & Laporan Kualitas Data (Data Quality Audit)
Mendeteksi missing values, invalid timestamp, time gaps, duplikasi key, outlier fisik, dan sensor flatline.
Ultra-modern UI dengan kartu KPI presisi, severity chips, dan filter interaktif sesuai pedoman Section K.
"""

import streamlit as st
import pandas as pd
from ui.components import (
    render_synthetic_banner, 
    render_page_hero, 
    render_mockup_kpi_card, 
    render_status_badge,
    render_empty_dataset_notice,
    LUCIDE_SVG_ICONS
)
from core.data_quality import analyze_data_quality

def render(session_state):
    render_synthetic_banner(session_state.get("is_synthetic", True))
    
    render_page_hero(
        title="Validasi & Laporan Kualitas Data",
        subtitle="Pemeriksaan komprehensif integritas data sensor: missing values, time gap, flatline, duplikasi, dan batas fisik operasi.",
        badge_text="Data Integrity Audit",
        badge_icon="search"
    )
    
    df = session_state.get("active_df")
    mapping = session_state.get("tag_mapping", {})
    
    if df is None or df.empty:
        render_empty_dataset_notice(mode="card", key_suffix="p04")
        return

    ts_col = mapping.get("timestamp", "timestamp")
    
    # Jalankan analisis kualitas data
    with st.spinner("Memeriksa kualitas data sensor..."):
        report = analyze_data_quality(df, timestamp_col=ts_col, expected_interval_min=5.0, tag_mapping=mapping)
        session_state["coverage_pct"] = report.coverage_pct

    # 4 KARTU KPI KUALITAS DATA MODERN
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_mockup_kpi_card(
            icon_key="activity",
            icon_bg="#EFF6FF",
            icon_color="#2563EB",
            title="Data Coverage",
            value=f"{report.coverage_pct:.1f}",
            unit="%",
            status_label="Normal" if report.coverage_pct >= 95 else "Warning",
            trend_arrow="•",
            trend_pct="100% Target",
            trend_direction="up",
            trend_subtext=f"{len(df):,} / {report.expected_intervals:,} titik",
            trace_footer="Interval target 5 menit • Tanpa Imputasi Buatan"
        )
    with c2:
        render_mockup_kpi_card(
            icon_key="database",
            icon_bg="#ECFDF5",
            icon_color="#059669",
            title="Missing Data Ratio",
            value=f"{report.missing_pct:.2f}",
            unit="%",
            status_label="Normal" if report.missing_pct < 1.0 else ("Warning" if report.missing_pct < 10.0 else "Anomaly"),
            trend_arrow="•",
            trend_pct="Terkontrol",
            trend_direction="up",
            trend_subtext="sel kosong terdeteksi",
            trace_footer="Evaluasi seluruh kanal sensor DCS"
        )
    with c3:
        render_mockup_kpi_card(
            icon_key="gauge",
            icon_bg="#FAF5FF",
            icon_color="#9333EA",
            title="Time Gaps Terdeteksi",
            value=f"{report.gap_count}",
            unit="kejadian",
            status_label="Normal" if report.gap_count == 0 else "Warning",
            trend_arrow="•",
            trend_pct="Frekuensi 5-Menit",
            trend_direction="up",
            trend_subtext="konsisten",
            trace_footer="Threshold gap: Δt > 7.5 menit (Non-interpolasi)"
        )
    with c4:
        render_mockup_kpi_card(
            icon_key="file_check",
            icon_bg="#F0FDFA",
            icon_color="#0D9488",
            title="Duplikasi Timestamp",
            value=f"{report.duplicate_count}",
            unit="baris",
            status_label="Normal" if report.duplicate_count == 0 else "Warning",
            trend_arrow="•",
            trend_pct="Unik",
            trend_direction="up",
            trend_subtext="kunci waktu terverifikasi",
            trace_footer="Kunci primer timestamp identik"
        )

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
    
    # DAFTAR TEMUAN MASALAH KUALITAS DATA
    alert_icon = LUCIDE_SVG_ICONS.get("alert_triangle", "")
    shield_icon = LUCIDE_SVG_ICONS.get("shield", "")
    
    issues_list = report.issues if hasattr(report, "issues") and report.issues else []
    
    with st.container(border=True):
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; margin-bottom:16px; padding-bottom:12px; border-bottom:1px solid #F1F5F9;">
            <div style="display:flex; align-items:center; gap:10px;">
                <div style="width:36px; height:36px; background:#FEF3C7; color:#D97706; border-radius:10px; display:flex; align-items:center; justify-content:center;">
                    {alert_icon}
                </div>
                <div>
                    <div style="font-size:15.5px; font-weight:800; color:#0F172A; margin:0; line-height:1.15;">Temuan Audit Kualitas Data & Batas Fisik</div>
                    <div style="font-size:12px; color:#64748B; margin:2px 0 0 0; line-height:1.2;">Identifikasi anomali teknis, pelanggaran batas termal fisik, dan diskontinuitas waktu</div>
                </div>
            </div>
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="background:{'#ECFDF5' if len(issues_list) == 0 else '#FFFBEB'}; color:{'#059669' if len(issues_list) == 0 else '#B45309'}; border:1px solid {'#A7F3D0' if len(issues_list) == 0 else '#FDE68A'}; font-size:12px; font-weight:700; padding:4px 12px; border-radius:16px;">
                    {len(issues_list)} Isu Teridentifikasi
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if not issues_list:
            st.markdown(f"""
            <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:12px; padding:20px; text-align:center; margin:10px 0;">
                <div style="color:#16A34A; display:flex; justify-content:center; margin-bottom:6px;">
                    {shield_icon}
                </div>
                <div style="font-size:15px; font-weight:700; color:#166534; margin:0 0 3px 0; line-height:1.15;">Dataset Operasional Lulus Validasi Kualitas Data!</div>
                <div style="font-size:12.5px; color:#15803D; margin:0; line-height:1.35;">
                    Tidak ditemukan missing values, time gaps, duplikasi timestamp, atau anomali flatline yang kritis. Seluruh tag kanonikal berada dalam batas fisik operasional yang valid dan siap diproses ke tahap audit energi.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            issues_df = pd.DataFrame(issues_list)
            
            # Ekspor & Filter Bar
            c_filter, c_exp = st.columns([2.5, 1], gap="medium")
            with c_filter:
                sev_filter = st.multiselect(
                    "Filter Tingkat Keparahan:",
                    options=["ANOMALY", "WARNING", "INFO"],
                    default=["ANOMALY", "WARNING"]
                )
            with c_exp:
                st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
                csv_data = issues_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "Ekspor Laporan Isu (CSV)",
                    icon=":material/download:",
                    data=csv_data,
                    file_name="laporan_kualitas_data_pltgu.csv",
                    mime="text/csv",
                    width="stretch"
                )
                
            filtered_issues = issues_df[issues_df["severity"].isin(sev_filter)] if "severity" in issues_df.columns else issues_df
            
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            
            # Render Tabel Isu Modern
            for _, row in filtered_issues.iterrows():
                sev = row.get("severity", "INFO")
                desc = row.get("description", "")
                itype = row.get("type", "")
                col_target = row.get("column", "")
                count_val = row.get("count", 0)
                
                border_color = "#EF4444" if sev == "ANOMALY" else ("#F59E0B" if sev == "WARNING" else "#3B82F6")
                badge_bg = "#FEF2F2" if sev == "ANOMALY" else ("#FFFBEB" if sev == "WARNING" else "#EFF6FF")
                badge_text = "#B91C1C" if sev == "ANOMALY" else ("#B45309" if sev == "WARNING" else "#1D4ED8")
                
                col_html = f'<span class="mapping-tag-code" style="margin-left:6px;">{col_target}</span>' if col_target and pd.notna(col_target) else ""
                
                st.markdown(f"""
                <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left: 4px solid {border_color}; border-radius:10px; padding:12px 16px; margin-bottom:10px; box-shadow:0 1px 2px rgba(0,0,0,0.02);">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="font-size:13.5px; font-weight:700; color:#0F172A;">{itype}</span>
                            {col_html}
                        </div>
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="background:{badge_bg}; color:{badge_text}; font-size:11px; font-weight:700; padding:2px 8px; border-radius:6px;">
                                {sev}
                            </span>
                            <span style="font-size:11.5px; color:#64748B; font-weight:600;">
                                {count_val:,} titik
                            </span>
                        </div>
                    </div>
                    <div style="font-size:12.5px; color:#475569; margin-top:6px; line-height:1.4;">
                        {desc}
                    </div>
                </div>
                """, unsafe_allow_html=True)
