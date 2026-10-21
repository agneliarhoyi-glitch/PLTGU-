"""
Halaman 10: Paket Persiapan Simulasi Aspen HYSYS (HYSYS Model Input Package)
Menghasilkan parameter representatif kondisi operasi baseline, mengidentifikasi data gap, dan menyediakan ekspor CSV/Excel.
Ultra-modern UI dengan SVG icons, disclaimer kepatuhan Section K, dan tombol ekspor simetris.
"""

import io
import pandas as pd
import streamlit as st
from ui.components import (
    render_synthetic_banner, 
    render_page_hero, 
    render_section_header,
    render_empty_dataset_notice,
    LUCIDE_SVG_ICONS
)
from core.config import HYSYS_DISCLAIMER
from core.hysys_exporter import generate_hysys_input_package

def render(session_state):
    render_synthetic_banner(session_state.get("is_synthetic", True))
    
    render_page_hero(
        title="Persiapan Simulasi Aspen HYSYS",
        subtitle="Penyusunan kondisi operasi baseline representatif dan identifikasi data gap untuk permodelan proses di Aspen HYSYS.",
        badge_text="HYSYS Model Input",
        badge_icon="package"
    )
    
    # Batasan Aspen HYSYS Wajib (Halaman 4 Poin 8 & Halaman 9 Poin J)
    package_icon = LUCIDE_SVG_ICONS.get("package", "")
    st.markdown(f"""
    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:12px 18px; margin-bottom:18px; display:flex; align-items:center; gap:12px;">
        <div style="color:#2563EB;">{package_icon}</div>
        <div style="font-size:12.5px; color:#475569; line-height:1.5;">
            <b style="color:#0F172A;">Batasan Aspen HYSYS (Section K Protocol):</b> {HYSYS_DISCLAIMER} Aplikasi web ini tidak menjalankan HYSYS secara langsung atau mengklaim integrasi otomatis. Hasil HYSYS merupakan hasil simulasi model dan harus divalidasi engineer sebelum diterapkan.
        </div>
    </div>
    """, unsafe_allow_html=True)

    df = session_state.get("active_df")
    mapping = session_state.get("tag_mapping", {})
    
    if df is None or df.empty:
        render_empty_dataset_notice(mode="card", key_suffix="p10")
        return

    render_section_header(
        title="Pemilihan Skenario Kondisi Baseline",
        subtitle="Pilih periode representatif yang stabil untuk diekstrak menjadi kondisi batas simulasi proses",
        icon_key="sliders",
        badge_text="Skenario Operasi"
    )

    # Pilihan Baseline
    baseline_options = [
        "Kondisi Beban Penuh Rata-rata (Full Load Steady)",
        "Kondisi Siang Hari (Beban Tinggi, Ambient Hangat)",
        "Kondisi Malam Hari (Beban Parsial, Ambient Sejuk)"
    ]
    selected_baseline = st.selectbox("Pilih Skenario Kondisi Baseline untuk Diekstrak:", baseline_options, label_visibility="collapsed")

    # Filter data jika malam / siang
    ts_col = mapping.get("timestamp", "timestamp")
    df_base = df.copy()
    if ts_col in df_base.columns:
        hours = pd.to_datetime(df_base[ts_col]).dt.hour
        if "Siang" in selected_baseline:
            df_base = df_base[(hours >= 11) & (hours <= 15)]
        elif "Malam" in selected_baseline:
            df_base = df_base[(hours >= 0) & (hours <= 5)]

    # Hasilkan paket data HYSYS
    hysys_table = generate_hysys_input_package(df_base, tag_mapping=mapping, baseline_period_label=selected_baseline)

    render_section_header(
        title="Tabel Variabel Representatif untuk Aspen HYSYS",
        subtitle="Tabel terstruktur berisi nilai median, batas validasi, dan identifikasi data gap sesuai kebutuhan lembar spesifikasi",
        icon_key="package",
        badge_text=f"Total: {len(hysys_table)} Parameter",
        icon_bg="#EFF6FF",
        icon_color="#2563EB"
    )

    # Ekspor Buttons
    c_btn1, c_btn2, _ = st.columns([1, 1, 2], gap="small")
    with c_btn1:
        csv_buf = hysys_table.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Ekspor ke CSV",
            icon=":material/download:",
            data=csv_buf,
            file_name=f"hysys_input_{selected_baseline[:12].replace(' ', '_').lower()}.csv",
            mime="text/csv",
            width="stretch"
        )
    with c_btn2:
        output_excel = io.BytesIO()
        with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
            hysys_table.to_excel(writer, index=False, sheet_name="HYSYS_Input")
        excel_data = output_excel.getvalue()
        st.download_button(
            "Ekspor ke Excel (.xlsx)",
            icon=":material/table_view:",
            data=excel_data,
            file_name=f"hysys_input_{selected_baseline[:12].replace(' ', '_').lower()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch"
        )

    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    st.dataframe(hysys_table, width="stretch", height=420)
