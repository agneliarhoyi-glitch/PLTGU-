"""
Halaman 3: Tag Mapping & Standarisasi Satuan (Schema Alignment)
Memetakan nama kolom/tag DCS ke variabel kanonikal standar pembangkit PLTGU Blok 1 (3-3-1).
Ultra-modern industrial UI dengan progress bar skema, segmented pills per sub-sistem,
tampilan kartu pemetaan beresolusi tinggi, dan kepatuhan penuh terhadap tata kelola Section K.
"""

import os
import json
import streamlit as st
import pandas as pd
from ui.components import render_synthetic_banner, render_page_hero, render_section_header, render_empty_dataset_notice, LUCIDE_SVG_ICONS

# Daftar variabel kanonikal standar PLTGU Blok 1
CANONICAL_VARIABLES = [
    # Plant & Lingkungan
    ("timestamp", "Timestamp Waktu Operasi", "Datetime", "Plant"),
    ("operating_status", "Status Operasi (NORMAL/STARTUP/TRIP)", "Category", "Plant"),
    ("ambient_temp_c", "Temperatur Udara Ambient", "°C", "Plant"),
    ("ambient_press_bar", "Tekanan Barometrik Ambient", "bar(a)", "Plant"),
    ("plant_gross", "Total Daya Gross PLTGU", "MW", "Plant"),
    ("plant_aux", "Beban Listrik Auxiliary PLTGU", "MW", "Plant"),
    ("plant_net", "Daya Listrik Neto PLTGU", "MW", "Plant"),
    
    # Bahan Bakar
    ("fuel_lhv_kj_kg", "Nilai Kalor Bahan Bakar (LHV)", "kJ/kg", "Fuel"),
    
    # Gas Turbine 1
    ("gt1_power", "Daya Gross GT-1", "MW", "GT-1"),
    ("gt1_fuel_flow", "Laju Alir Bahan Bakar GT-1", "kg/h", "GT-1"),
    ("gt1_comp_p_in", "Tekanan Masuk Kompresor GT-1", "bar(a)", "GT-1"),
    ("gt1_comp_p_out", "Tekanan Keluar Kompresor GT-1", "bar(a)", "GT-1"),
    ("gt1_exhaust_temp", "Temperatur Gas Buang GT-1", "°C", "GT-1"),
    
    # Gas Turbine 2
    ("gt2_power", "Daya Gross GT-2", "MW", "GT-2"),
    ("gt2_fuel_flow", "Laju Alir Bahan Bakar GT-2", "kg/h", "GT-2"),
    ("gt2_comp_p_in", "Tekanan Masuk Kompresor GT-2", "bar(a)", "GT-2"),
    ("gt2_comp_p_out", "Tekanan Keluar Kompresor GT-2", "bar(a)", "GT-2"),
    ("gt2_exhaust_temp", "Temperatur Gas Buang GT-2", "°C", "GT-2"),
    
    # Gas Turbine 3
    ("gt3_power", "Daya Gross GT-3", "MW", "GT-3"),
    ("gt3_fuel_flow", "Laju Alir Bahan Bakar GT-3", "kg/h", "GT-3"),
    ("gt3_comp_p_in", "Tekanan Masuk Kompresor GT-3", "bar(a)", "GT-3"),
    ("gt3_comp_p_out", "Tekanan Keluar Kompresor GT-3", "bar(a)", "GT-3"),
    ("gt3_exhaust_temp", "Temperatur Gas Buang GT-3", "°C", "GT-3"),
    
    # HRSG 1, 2, 3
    ("hrsg1_steam_flow", "Laju Alir Main Steam HRSG-1", "kg/s", "HRSG-1"),
    ("hrsg1_stack_temp", "Temperatur Stack Gas HRSG-1", "°C", "HRSG-1"),
    ("hrsg1_fw_flow", "Laju Alir Feedwater HRSG-1", "kg/s", "HRSG-1"),
    
    ("hrsg2_steam_flow", "Laju Alir Main Steam HRSG-2", "kg/s", "HRSG-2"),
    ("hrsg2_stack_temp", "Temperatur Stack Gas HRSG-2", "°C", "HRSG-2"),
    ("hrsg2_fw_flow", "Laju Alir Feedwater HRSG-2", "kg/s", "HRSG-2"),
    
    ("hrsg3_steam_flow", "Laju Alir Main Steam HRSG-3", "kg/s", "HRSG-3"),
    ("hrsg3_stack_temp", "Temperatur Stack Gas HRSG-3", "°C", "HRSG-3"),
    ("hrsg3_fw_flow", "Laju Alir Feedwater HRSG-3", "kg/s", "HRSG-3"),
    
    # Siklus Uap & Steam Turbine
    ("main_steam_p", "Tekanan Uap Utama HP", "bar(a)", "Steam & ST"),
    ("main_steam_t", "Temperatur Uap Utama HP", "°C", "Steam & ST"),
    ("st_power", "Daya Gross Steam Turbine", "MW", "Steam & ST"),
    
    # Kondensor & Air Pendingin
    ("condenser_p", "Tekanan Kondensor (Vakum)", "bar(a)", "Condenser & CW"),
    ("cw_in_t", "Temperatur Masuk Air Pendingin CW", "°C", "Condenser & CW"),
    ("cw_out_t", "Temperatur Keluar Air Pendingin CW", "°C", "Condenser & CW"),
    ("cw_flow", "Laju Alir Air Pendingin CW", "kg/s", "Condenser & CW")
]

# Alias pencocokan cerdas untuk auto-matching DCS tags
SMART_ALIASES = {
    "timestamp": ["timestamp", "waktu", "datetime", "date_time", "time"],
    "operating_status": ["operating_status", "status_operasi", "unit_status", "mode"],
    "ambient_temp_c": ["ambient_temp_c", "ambient_temp", "t_ambient", "suhu_lingkungan"],
    "ambient_press_bar": ["ambient_press_bar", "ambient_press", "p_ambient", "tekanan_barometrik"],
    "fuel_lhv_kj_kg": ["fuel_lhv_kj_kg", "lhv_kj_kg", "lhv", "fuel_lhv"],
    
    "gt1_power": ["GTDL-19173", "gt1_gross_mw", "gt1_power", "gt1_mw", "gt_1_mw", "gt1_generator_mw", "gt1_load"],
    "gt1_fuel_flow": ["CFGAAI-0004", "GTDL-19161", "gt1_fuel_flow_kg_h", "gt1_fuel_flow_kg_s", "gt1_fuel_flow", "gt1_fuel"],
    "gt1_comp_p_in": ["GTDL-19075", "gt1_comp_p_in_bar", "gt1_comp_p_in", "gt1_p_inlet"],
    "gt1_comp_p_out": ["GTDL-19149", "gt1_comp_p_out_bar", "gt1_comp_p_out", "gt1_p_discharge"],
    "gt1_exhaust_temp": ["GTDL-19071", "gt1_exhaust_temp_c", "gt1_exhaust_temp", "gt1_ttxm"],
    
    "gt2_power": ["GTDL-29173", "gt2_gross_mw", "gt2_power", "gt2_mw", "gt_2_mw", "gt2_generator_mw", "gt2_load"],
    "gt2_fuel_flow": ["CFGAAI-0005", "GTDL-29161", "gt2_fuel_flow_kg_h", "gt2_fuel_flow_kg_s", "gt2_fuel_flow", "gt2_fuel"],
    "gt2_comp_p_in": ["GTDL-29075", "gt2_comp_p_in_bar", "gt2_comp_p_in", "gt2_p_inlet"],
    "gt2_comp_p_out": ["GTDL-29149", "gt2_comp_p_out_bar", "gt2_comp_p_out", "gt2_p_discharge"],
    "gt2_exhaust_temp": ["GTDL-29071", "gt2_exhaust_temp_c", "gt2_exhaust_temp", "gt2_ttxm"],
    
    "gt3_power": ["GTDL-39173", "gt3_gross_mw", "gt3_power", "gt3_mw", "gt_3_mw", "gt3_generator_mw", "gt3_load"],
    "gt3_fuel_flow": ["CFGAAI-0006", "GTDL-39161", "gt3_fuel_flow_kg_h", "gt3_fuel_flow_kg_s", "gt3_fuel_flow", "gt3_fuel"],
    "gt3_comp_p_in": ["GTDL-39075", "gt3_comp_p_in_bar", "gt3_comp_p_in", "gt3_p_inlet"],
    "gt3_comp_p_out": ["GTDL-39149", "gt3_comp_p_out_bar", "gt3_comp_p_out", "gt3_p_discharge"],
    "gt3_exhaust_temp": ["GTDL-39071", "gt3_exhaust_temp_c", "gt3_exhaust_temp", "gt3_ttxm"],
    
    "hrsg1_steam_flow": ["hrsg1_main_steam_flow_kg_s", "hrsg1_steam_flow", "hrsg1_steam"],
    "hrsg1_stack_temp": ["hrsg1_stack_temp_c", "hrsg1_stack_temp", "hrsg1_stack"],
    "hrsg1_fw_flow": ["hrsg1_feedwater_flow_kg_s", "hrsg1_fw_flow", "hrsg1_feedwater"],
    
    "hrsg2_steam_flow": ["hrsg2_main_steam_flow_kg_s", "hrsg2_steam_flow", "hrsg2_steam"],
    "hrsg2_stack_temp": ["hrsg2_stack_temp_c", "hrsg2_stack_temp", "hrsg2_stack"],
    "hrsg2_fw_flow": ["hrsg2_feedwater_flow_kg_s", "hrsg2_fw_flow", "hrsg2_feedwater"],
    
    "hrsg3_steam_flow": ["hrsg3_main_steam_flow_kg_s", "hrsg3_steam_flow", "hrsg3_steam"],
    "hrsg3_stack_temp": ["hrsg3_stack_temp_c", "hrsg3_stack_temp", "hrsg3_stack"],
    "hrsg3_fw_flow": ["hrsg3_feedwater_flow_kg_s", "hrsg3_fw_flow", "hrsg3_feedwater"],
    
    "main_steam_p": ["main_steam_pressure_bar", "main_steam_p", "ms_press_bar"],
    "main_steam_t": ["main_steam_temp_c", "main_steam_t", "ms_temp_c"],
    "st_power": ["STDL-20106", "st_gross_mw", "st_power", "st_mw", "st_generator_mw", "st_load"],
    
    "condenser_p": ["condenser_pressure_bar", "condenser_p", "p_condenser"],
    "cw_in_t": ["4HRCTE-0002", "cw_inlet_temp_c", "cw_in_t", "t_cw_in"],
    "cw_out_t": ["4HRCTE-0003", "cw_outlet_temp_c", "cw_out_t", "t_cw_out"],
    "cw_flow": ["cw_flow_kg_s", "cw_flow", "flow_cw"],
    
    "plant_gross": ["plant_gross_mw", "plant_gross", "total_gross_mw"],
    "plant_aux": ["plant_aux_power_mw", "plant_aux", "aux_power_mw"],
    "plant_net": ["plant_net_power_mw", "plant_net", "total_net_mw"]
}

def auto_detect_tag_mapping(df_columns, existing_mapping=None) -> dict:
    """Mencocokkan nama kolom DataFrame ke variabel kanonikal berdasarkan alias cerdas dan DCS tags."""
    new_map = (existing_mapping or {}).copy()
    col_list = list(df_columns)
    col_lower_map = {str(c).strip().lower(): str(c) for c in col_list}

    for code, _, _, _ in CANONICAL_VARIABLES:
        current_val = new_map.get(code)
        # Jika belum ada atau nilai saat ini tidak valid di kolom dataframe, cari alias
        if not current_val or current_val not in col_list:
            aliases = SMART_ALIASES.get(code, [code])
            for alias in aliases:
                a_clean = alias.strip().lower()
                if a_clean in col_lower_map:
                    new_map[code] = col_lower_map[a_clean]
                    break
    return new_map


def render(session_state):
    render_synthetic_banner(session_state.get("is_synthetic", True))
    
    render_page_hero(
        title="Tag Mapping & Standarisasi Satuan",
        subtitle="Petakan nama kolom/tag DCS ke variabel kanonikal standar pembangkit. Konfigurasi tersimpan dapat dimuat ulang kapan saja.",
        badge_text="Schema Alignment",
        badge_icon="🏷️"
    )
    
    df = session_state.get("active_df")
    if df is None or df.empty:
        render_empty_dataset_notice(mode="card", key_suffix="p03")
        return

    columns_available = ["(Tidak Dipetakan)"] + list(df.columns)
    current_mapping = session_state.get("tag_mapping", {})
    
    # Auto-detect tag secara proaktif jika mapping masih sedikit atau belum lengkap
    detected_mapping = auto_detect_tag_mapping(df.columns, current_mapping)
    if len(detected_mapping) > len(current_mapping):
        current_mapping = detected_mapping
        session_state["tag_mapping"] = current_mapping
    
    # Hitung metrik mapping
    total_canonical = len(CANONICAL_VARIABLES)
    valid_mapped = [c for c, _, _, _ in CANONICAL_VARIABLES if current_mapping.get(c) in df.columns]
    mapped_count = len(valid_mapped)
    unmapped_canonical_count = total_canonical - mapped_count
    pct_complete = (mapped_count / total_canonical) * 100.0 if total_canonical > 0 else 0
    
    # Hitung kolom DCS yang belum terpetakan
    mapped_source_cols = set(current_mapping.values())
    unmapped_cols = [c for c in df.columns if c not in mapped_source_cols]
    
    # 1. TOOLBAR STATUS SKEMA & AKSI CEPAT
    st.markdown(f"""
    <div class="mapping-toolbar-card">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
            <div style="flex:1; min-width:280px;">
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
                    <span style="font-size:15px; font-weight:800; color:#0F172A;">Kelengkapan Skema Variabel:</span>
                    <span style="font-size:13px; font-weight:800; color:#2563EB;">{mapped_count} / {total_canonical} Tag ({pct_complete:.1f}%)</span>
                    <span style="background:{'#ECFDF5' if pct_complete >= 80 else '#FFFBEB'}; color:{'#059669' if pct_complete >= 80 else '#D97706'}; font-size:11px; font-weight:700; padding:2px 8px; border-radius:12px; border:1px solid {'#A7F3D0' if pct_complete >= 80 else '#FDE68A'};">
                        {'✓ Terpetakan Penuh' if pct_complete >= 80 else f'{unmapped_canonical_count} Tag Kosong di Dataset'}
                    </span>
                </div>
                <div class="mapping-progress-track">
                    <div class="mapping-progress-fill" style="width: {pct_complete}%;"></div>
                </div>
                <div style="font-size:12px; color:#64748B; margin-top:4px;">
                    <span>Total {len(df.columns)} Kolom DCS Mentah</span> • 
                    <span style="color:#2563EB; font-weight:600;">{mapped_count} Terhubung</span> • 
                    <span style="color:#D97706; font-weight:600;">{unmapped_canonical_count} Kosong di Dataset</span> • 
                    <span style="color:#0284C7;">{len(unmapped_cols)} Kolom Ekstra Tersedia (Read-Only)</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Baris Tombol Aksi yang Rapi dan Seimbang
    btn_col1, btn_col2, btn_col3 = st.columns([1.2, 1, 1], gap="small")
    
    with btn_col1:
        if st.button("Auto-Match Tag Cerdas", icon=":material/bolt:", width="stretch", type="primary"):
            new_map = auto_detect_tag_mapping(df.columns, current_mapping)
            session_state["tag_mapping"] = new_map
            st.toast(f"✅ Auto-Match Berhasil! {len(new_map)} variabel kanonikal terpetakan.", icon="⚡")
            st.rerun()
            
    with btn_col2:
        mapping_json_str = json.dumps(current_mapping, indent=2)
        st.download_button(
            "Unduh JSON Skema",
            icon=":material/download:",
            data=mapping_json_str,
            file_name="tag_mapping_pltgu_blok1.json",
            mime="application/json",
            width="stretch"
        )
        
    with btn_col3:
        with st.popover("Impor File JSON", icon=":material/upload_file:", width="stretch"):
            st.markdown("<p style='font-size:12.5px; font-weight:600; color:#0F172A; margin-bottom:6px;'>Unggah Konfigurasi Mapping JSON:</p>", unsafe_allow_html=True)
            uploaded_map = st.file_uploader("Unggah File JSON", type=["json"], label_visibility="collapsed")
            if uploaded_map is not None:
                try:
                    loaded = json.load(uploaded_map)
                    imported_dict = loaded.get("tags", loaded)
                    session_state["tag_mapping"] = imported_dict
                    st.success("Konfigurasi skema berhasil diimpor!", icon=":material/check_circle:")
                    st.rerun()
                except Exception as e:
                    st.error(f"Format JSON mapping salah: {e}", icon=":material/error:")

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    
    # 2. NAVIGASI SUB-SISTEM DENGAN SEGMENTED PILLS MODERN
    categories = [
        "Plant", "Fuel", "GT-1", "GT-2", "GT-3", 
        "HRSG-1", "HRSG-2", "HRSG-3", "Steam & ST", "Condenser & CW"
    ]
    
    # Hitung kelengkapan per kategori untuk indikator visual
    cat_badges = {}
    for cat in categories:
        vars_cat = [v for v in CANONICAL_VARIABLES if v[3] == cat]
        m_cat = sum(1 for v in vars_cat if current_mapping.get(v[0]) in df.columns)
        cat_badges[cat] = f"{cat} ({m_cat}/{len(vars_cat)})"
        
    pills_options = list(cat_badges.values())
    
    # Pilih sub-sistem menggunakan st.pills yang estetik
    st.markdown("<div style='font-size:13px; font-weight:700; color:#334155; margin-bottom:6px;'>Pilih Sub-Sistem Pembangkit:</div>", unsafe_allow_html=True)
    selected_pill = st.pills(
        "Kategori Peralatan",
        options=pills_options,
        default=pills_options[0],
        label_visibility="collapsed"
    )
    
    # Ekstrak nama kategori asli dari pill yang dipilih
    selected_cat = "Plant"
    for cat, pill_str in cat_badges.items():
        if pill_str == selected_pill:
            selected_cat = cat
            break
            
    vars_in_cat = [v for v in CANONICAL_VARIABLES if v[3] == selected_cat]
    
    # 3. KONTEN EDITOR PEMETAAN VARIABEL PER SUB-SISTEM
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    
    cat_icons = {
        "Plant": "factory", "Fuel": "flame", "GT-1": "zap", "GT-2": "zap", "GT-3": "zap",
        "HRSG-1": "flame", "HRSG-2": "flame", "HRSG-3": "flame", 
        "Steam & ST": "gauge", "Condenser & CW": "database"
    }
    cat_svg = LUCIDE_SVG_ICONS.get(cat_icons.get(selected_cat, "activity"), "")
    
    render_section_header(
        title=f"Pemetaan Parameter: {selected_cat}",
        subtitle="Petakan sinyal DCS ke variabel standar untuk kalkulasi neraca energi & efisiensi",
        icon_key=cat_icons.get(selected_cat, "activity"),
        badge_text=f"{len(vars_in_cat)} Variabel Standar"
    )
    
    updated_mapping = current_mapping.copy()
    
    with st.form(f"form_mapping_{selected_cat}"):
        for code, label, unit, eq in vars_in_cat:
            cur_mapped_col = current_mapping.get(code, "(Tidak Dipetakan)")
            idx = columns_available.index(cur_mapped_col) if cur_mapped_col in columns_available else 0
            
            is_mapped = (cur_mapped_col in columns_available and cur_mapped_col != "(Tidak Dipetakan)")
            status_html = f'<span style="color:#059669; font-weight:700; font-size:11.5px;">✓ Terhubung: {cur_mapped_col}</span>' if is_mapped else '<span style="color:#D97706; font-weight:700; font-size:11.5px;">⚠️ Belum Dipetakan</span>'
            
            c_label, c_select = st.columns([1.3, 1.7], gap="medium")
            with c_label:
                st.markdown(f"""
                <div style="padding-top:6px;">
                    <div style="font-size:13.5px; font-weight:700; color:#0F172A;">{label}</div>
                    <div style="display:flex; align-items:center; gap:6px; margin-top:4px;">
                        <span class="mapping-tag-code">{code}</span>
                        <span class="mapping-unit-badge">{unit}</span>
                        {status_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            with c_select:
                chosen_col = st.selectbox(
                    f"Pilih Kolom DCS untuk {code}",
                    options=columns_available,
                    index=idx,
                    key=f"map_{code}",
                    label_visibility="collapsed"
                )
                if chosen_col != "(Tidak Dipetakan)":
                    updated_mapping[code] = chosen_col
                elif code in updated_mapping:
                    del updated_mapping[code]
                    
            st.markdown("<div style='height: 1px; background:#F1F5F9; margin: 8px 0 12px 0;'></div>", unsafe_allow_html=True)
            
        c_sub_save, c_sub_space = st.columns([1, 1])
        with c_sub_save:
            submit_btn = st.form_submit_button(f"Simpan Pemetaan {selected_cat}", icon=":material/save:", type="primary", width="stretch")
            if submit_btn:
                session_state["tag_mapping"] = updated_mapping
                st.toast(f"Pemetaan sub-sistem {selected_cat} berhasil disimpan!", icon=":material/check_circle:")
                st.rerun()
    
    # 4. KARTU KOLOM SUMBER YANG BELUM DIPAKAI (READ-ONLY GOVERNANCE)
    with st.expander(f"Kolom Sumber DCS yang Belum Dipetakan ({len(unmapped_cols)} Kolom)", icon=":material/table_chart:", expanded=False):
        st.markdown(f"""
        <div style="font-size:12.5px; color:#475569; margin-bottom:12px;">
            <b>Protokol Tata Kelola (Section K):</b> Kolom mentah DCS yang tidak dipetakan ke variabel standar tetap dipertahankan utuh dalam dataset dan tidak dihapus secara otomatis.
        </div>
        """, unsafe_allow_html=True)
        
        if unmapped_cols:
            col_list_df = pd.DataFrame({
                "Nama Kolom Mentah DCS": unmapped_cols,
                "Tipe Data": [str(df[c].dtype) for c in unmapped_cols],
                "Jumlah Data Non-Null": [int(df[c].notna().sum()) for c in unmapped_cols],
                "Contoh Nilai (Baris 1)": [str(df[c].iloc[0]) if len(df) > 0 else "-" for c in unmapped_cols]
            })
            st.dataframe(col_list_df, width="stretch", height=240)
        else:
            st.success("Seluruh kolom di dataset operasional telah terpetakan ke variabel kanonikal standar pembangkit!", icon=":material/verified:")
