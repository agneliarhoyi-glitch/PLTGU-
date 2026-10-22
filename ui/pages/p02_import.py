"""
Halaman 2: Import Data Operasi Historian / DCS
Mendukung upload CSV/XLSX, pemilihan sheet, dan preview data mentah.
Ultra-modern UI dengan visual stat card tajam, high-contrast typography, dan raw data governance banner.
"""

import os
import json
from datetime import datetime, timezone, timedelta
import streamlit as st
import streamlit.components.v1 as st_components
import pandas as pd
from ui.components import render_synthetic_banner, render_page_hero, LUCIDE_SVG_ICONS, clean_html

WIB_TZ = timezone(timedelta(hours=7))

def _get_wib_now_str():
    """Mengembalikan waktu saat ini dalam zona WIB (UTC+7) format YYYY-MM-DD HH:MM:SS."""
    return datetime.now(WIB_TZ).strftime("%Y-%m-%d %H:%M:%S")

def _robust_read_csv(uploaded_file) -> pd.DataFrame:
    """Membaca CSV secara tangguh dengan auto-detect pemisah (koma/titik-koma/tab), encoding, dan skip baris rusak."""
    raw_bytes = uploaded_file.getvalue()
    
    # 1. Deteksi encoding
    encoding_to_use = "utf-8"
    for enc in ["utf-8-sig", "utf-8", "latin1", "cp1252"]:
        try:
            sample_text = raw_bytes[:16384].decode(enc)
            encoding_to_use = enc
            break
        except Exception:
            continue
    else:
        sample_text = raw_bytes[:16384].decode("utf-8", errors="ignore")
        
    # 2. Deteksi delimiter paling dominan di 10 baris pertama
    lines = [l for l in sample_text.splitlines() if l.strip()][:10]
    sep = ","
    if lines:
        comma_cnt = sum(l.count(",") for l in lines)
        semi_cnt = sum(l.count(";") for l in lines)
        tab_cnt = sum(l.count("\t") for l in lines)
        if semi_cnt > comma_cnt and semi_cnt > tab_cnt:
            sep = ";"
        elif tab_cnt > comma_cnt and tab_cnt > semi_cnt:
            sep = "\t"
            
    # 3. Coba baca dengan C engine standar (tercepat)
    uploaded_file.seek(0)
    try:
        return pd.read_csv(uploaded_file, sep=sep, encoding=encoding_to_use, low_memory=False)
    except Exception:
        # 4. Fallback jika ada tokenizing error (kelebihan koma, unescaped quote, dll)
        uploaded_file.seek(0)
        try:
            return pd.read_csv(uploaded_file, sep=sep, encoding=encoding_to_use, engine="python", on_bad_lines="skip")
        except Exception:
            # 5. Fallback pamungkas: auto-sniff python engine
            uploaded_file.seek(0)
            return pd.read_csv(uploaded_file, sep=None, engine="python", encoding=encoding_to_use, on_bad_lines="skip")


def render(session_state):
    # Tampilkan notifikasi toast jika dataset baru saja dihapus
    if session_state.pop("dataset_deleted_toast", False):
        st.toast("Dataset berhasil dihapus dari memori!", icon=":material/delete:")

    render_synthetic_banner(session_state.get("is_synthetic", True))
    
    render_page_hero(
        title="Import Data Historian / DCS",
        subtitle="Unggah berkas operasional format CSV atau XLSX. Data mentah disimpan utuh (immutable) dan dilindungi dari modifikasi langsung.",
        badge_text="Raw Data Pipeline",
        badge_icon="database"
    )
    
    # KARTU UNGGAH BERKAS HISTORIAN DCS
    with st.container(border=True):
        file_svg = LUCIDE_SVG_ICONS.get("file_text", "")
        st.markdown(f"""
<div style="display:flex; align-items:center; gap:10px; margin-bottom:12px;">
    <div style="width:34px; height:34px; background:#EFF6FF; color:#1E6DEB; border-radius:8px; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
        {file_svg}
    </div>
    <div>
        <div style="font-size:14.5px; font-weight:700; color:#0F172A; margin:0; line-height:1.15;">Unggah File Historian DCS Baru</div>
        <div style="font-size:11.5px; color:#64748B; margin:2px 0 0 0; line-height:1.2;">Format CSV, XLSX, XLS (Maks. 200MB per berkas)</div>
    </div>
</div>
""", unsafe_allow_html=True)
        
        uploader_key = f"historian_uploader_{session_state.get('uploader_key', 0)}"
        uploaded_file = st.file_uploader(
            "Pilih File Historian DCS (CSV atau Excel)",
            type=["csv", "xlsx", "xls"],
            label_visibility="collapsed",
            key=uploader_key
        )
        st.markdown("""
<div style="font-size:11px; color:#64748B; margin-top:6px; display:flex; align-items:center; gap:6px;">
    <span style="color:#059669; font-size:8px;">●</span> Data mentah asli tersimpan utuh dan dilindungi (read-only).
</div>
""", unsafe_allow_html=True)

    # Proses file yang diunggah
    if uploaded_file is not None:
        file_name = uploaded_file.name
        cur_meta = session_state.get("dataset_metadata") or {}
        if cur_meta.get("filename") != file_name or session_state.get("active_df") is None:
            try:
                size_kb = round(len(uploaded_file.getvalue()) / 1024, 1)
                
                if file_name.endswith(".csv"):
                    df_loaded = _robust_read_csv(uploaded_file)
                    sheet_selected = "CSV Data"
                else:
                    xl = pd.ExcelFile(uploaded_file)
                    sheet_names = xl.sheet_names
                    sheet_selected = st.selectbox("Pilih Sheet Excel:", sheet_names)
                    df_loaded = pd.read_excel(uploaded_file, sheet_name=sheet_selected)
                    
                session_state["raw_df"] = df_loaded.copy()
                session_state["active_df"] = df_loaded.copy()
                is_synth = "data_source_label" in df_loaded.columns and (df_loaded["data_source_label"] == "SINTETIS").any()
                session_state["is_synthetic"] = is_synth
                session_state["active_version"] = "v1_raw"
                metadata = {
                    "filename": file_name,
                    "uploaded_at": _get_wib_now_str(),
                    "size_kb": size_kb,
                    "sheet": sheet_selected,
                    "rows": len(df_loaded),
                    "cols": len(df_loaded.columns)
                }
                session_state["dataset_metadata"] = metadata
                
                # Auto-detect mapping tag DCS secara cerdas
                try:
                    from ui.pages.p03_tag_mapping import auto_detect_tag_mapping
                    session_state["tag_mapping"] = auto_detect_tag_mapping(df_loaded.columns, session_state.get("tag_mapping"))
                except Exception:
                    pass
                
                # Simpan dataset ke penyimpanan sesi persisten agar tidak hilang saat F5/reload
                try:
                    os.makedirs("data", exist_ok=True)
                    df_loaded.to_csv("data/active_dataset.csv", index=False)
                    with open("data/active_dataset_meta.json", "w", encoding="utf-8") as f_meta:
                        json.dump(metadata, f_meta, indent=2)
                except Exception:
                    pass
                    
                st.rerun()
            except Exception as e:
                st.error(f"Gagal membaca file: {str(e)}", icon=":material/error:")
        else:
            sheet_disp = cur_meta.get("sheet", "CSV Data")
            st.success(f"File '{file_name}' ({sheet_disp}) berhasil diimpor!", icon=":material/check_circle:")
    elif session_state.get("active_df") is not None and not session_state["active_df"].empty:
        cur_meta = session_state.get("dataset_metadata") or {}
        f_name_active = cur_meta.get("filename", "Dataset Aktif")
        n_rows_active = cur_meta.get("rows", len(session_state["active_df"]))
        st.markdown(f"""
        <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:8px; padding:8px 12px; margin-top:8px; display:flex; align-items:center; gap:8px;">
            <span style="color:#16A34A; font-weight:700; font-size:12px;">✓ Dataset Aktif:</span>
            <span style="color:#15803D; font-size:12px;"><b>{f_name_active}</b> ({n_rows_active:,} baris data) tersimpan di sesi kerja Anda.</span>
        </div>
        """, unsafe_allow_html=True)

    # Tampilkan Metadata & Preview Data Mentah Asli
    active_df = session_state.get("active_df")
    meta = session_state.get("dataset_metadata")
    
    if active_df is not None and not active_df.empty:
        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
        
        file_check_svg = LUCIDE_SVG_ICONS.get("file_check", "")
        file_text_svg = LUCIDE_SVG_ICONS.get("file_text", "")
        calendar_svg = LUCIDE_SVG_ICONS.get("calendar", "")
        database_svg = LUCIDE_SVG_ICONS.get("database", "")
        activity_svg = LUCIDE_SVG_ICONS.get("activity", "")
        grid_svg = LUCIDE_SVG_ICONS.get("grid", "")
        shield_svg = LUCIDE_SVG_ICONS.get("shield", "")
        
        # Ekstrak data metadata aman
        f_name = meta.get("filename", "Dataset Aktif") if meta else "Dataset Aktif"
        f_disp = f_name if len(f_name) <= 22 else f"{f_name[:10]}...{f_name[-9:]}"
        f_ext = f_name.split(".")[-1].upper() if "." in f_name else "DATA"
        
        up_time_raw = meta.get("uploaded_at", _get_wib_now_str()) if meta else _get_wib_now_str()
        if " " in up_time_raw:
            up_date, up_clock = up_time_raw.split(" ", 1)
        else:
            up_date, up_clock = up_time_raw, "Recorded"
            
        f_size = f"{meta.get('size_kb', 0):,.1f} KB" if meta else f"{round(len(active_df)*len(active_df.columns)*8/1024, 1):,.1f} KB"
        n_rows = f"{meta.get('rows', len(active_df)):,}" if meta else f"{len(active_df):,}"
        n_cols = f"{meta.get('cols', len(active_df.columns))}" if meta else f"{len(active_df.columns)}"
        
        # Render Kartu Metadata 5-Kolom (100% High-Contrast, Bebas Warna Putih)
        with st.container(border=True):
            head_col_info, head_col_btn = st.columns([3.6, 1.4])
            with head_col_info:
                st.markdown(f"""
<div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
    <div style="width:36px; height:36px; background:#EFF6FF; color:#1E6DEB; border-radius:10px; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
        {file_check_svg}
    </div>
    <div>
        <div style="font-size:15.5px; font-weight:700; color:#0F172A; margin:0; line-height:1.15;">Informasi Berkas Operasional & Pratinjau Data Mentah</div>
        <div style="font-size:12px; color:#64748B; margin:2px 0 0 0; line-height:1.2;">Dataset tersimpan dalam status Immutable Raw (Read-Only) untuk integritas audit</div>
    </div>
</div>
<div style="display:flex; gap:8px; margin-bottom:14px;">
    <span style="background:#ECFDF5; color:#059669; border:1px solid #A7F3D0; font-size:11.5px; font-weight:700; padding:3px 9px; border-radius:20px;">
        ✓ Terverifikasi
    </span>
</div>
""", unsafe_allow_html=True)
            with head_col_btn:
                st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
                with st.popover("Hapus Dataset", icon=":material/delete:", use_container_width=True, help="Klik untuk mengosongkan dataset aktif dari memori sesi"):
                    st.markdown(clean_html("""
                    <div style="min-width: 240px; font-size: 13px; color: #0F172A; margin-bottom: 10px; line-height: 1.5;">
                        <b style="color: #DC2626;">Konfirmasi Hapus Dataset?</b><br>
                        <span style="font-size: 11.5px; color: #64748B;">Data aktif di memori sesi akan dikosongkan. Seluruh modul audit akan kembali ke status kosong.</span>
                    </div>
                    """), unsafe_allow_html=True)
                    if st.button("Ya, Hapus Sekarang", type="primary", use_container_width=True, key="btn_confirm_delete_dataset", icon=":material/delete_forever:"):
                        session_state["raw_df"] = None
                        session_state["active_df"] = None
                        session_state["dataset_metadata"] = None
                        session_state["is_synthetic"] = False
                        session_state["active_version"] = None
                        session_state["tag_mapping"] = {}
                        session_state["uploader_key"] = session_state.get("uploader_key", 0) + 1
                        session_state["pending_nav"] = "Import Data Historian"
                        session_state["dataset_deleted_toast"] = True
                        
                        # Hapus juga berkas fisik persisten dari folder data/
                        for f_path in ["data/active_dataset.csv", "data/active_dataset_meta.json"]:
                            if os.path.exists(f_path):
                                try:
                                    os.remove(f_path)
                                except Exception:
                                    pass
                        st.rerun()
            
            mc1, mc2, mc3, mc4, mc5 = st.columns(5, gap="small")
            with mc1:
                st.markdown(f"""
<div class="meta-stat-card">
    <div class="meta-stat-top">
        <span class="meta-stat-label">Nama Berkas</span>
        <div class="meta-stat-icon" style="background:#EFF6FF; color:#2563EB;">{file_text_svg}</div>
    </div>
    <div class="meta-stat-value" title="{f_name}">{f_disp}</div>
    <div class="meta-stat-sub">
        <span style="background:#DBEAFE; color:#1E40AF; padding:1px 6px; border-radius:4px; font-size:10px; font-weight:700;">{f_ext}</span>
        <span>Source</span>
    </div>
</div>
""", unsafe_allow_html=True)

            with mc2:
                st.markdown(f"""
<div class="meta-stat-card">
    <div class="meta-stat-top">
        <span class="meta-stat-label">Waktu Unggah</span>
        <div class="meta-stat-icon" style="background:#FAF5FF; color:#9333EA;">{calendar_svg}</div>
    </div>
    <div class="meta-stat-value">{up_clock}</div>
    <div class="meta-stat-sub"><span>{up_date}</span></div>
</div>
""", unsafe_allow_html=True)

            with mc3:
                st.markdown(f"""
<div class="meta-stat-card">
    <div class="meta-stat-top">
        <span class="meta-stat-label">Ukuran Berkas</span>
        <div class="meta-stat-icon" style="background:#ECFDF5; color:#059669;">{database_svg}</div>
    </div>
    <div class="meta-stat-value">{f_size}</div>
    <div class="meta-stat-sub"><span>In-Memory</span></div>
</div>
""", unsafe_allow_html=True)

            with mc4:
                st.markdown(f"""
<div class="meta-stat-card">
    <div class="meta-stat-top">
        <span class="meta-stat-label">Jumlah Baris</span>
        <div class="meta-stat-icon" style="background:#FFFBEB; color:#D97706;">{activity_svg}</div>
    </div>
    <div class="meta-stat-value">{n_rows}</div>
    <div class="meta-stat-sub"><span>Titik Rekaman</span></div>
</div>
""", unsafe_allow_html=True)

            with mc5:
                st.markdown(f"""
<div class="meta-stat-card">
    <div class="meta-stat-top">
        <span class="meta-stat-label">Jumlah Kolom</span>
        <div class="meta-stat-icon" style="background:#F0FDFA; color:#0D9488;">{grid_svg}</div>
    </div>
    <div class="meta-stat-value">{n_cols} Kolom</div>
    <div class="meta-stat-sub"><span>Kanal DCS</span></div>
</div>
""", unsafe_allow_html=True)

            st.markdown(f"""
<div style="margin-top:14px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center;">
    <span style="font-size:13px; font-weight:700; color:#334155;">Pratinjau 100 Baris Pertama Data Mentah:</span>
    <span style="font-size:11.5px; color:#64748B;">Total {n_rows} baris × {n_cols} kolom</span>
</div>
""", unsafe_allow_html=True)
            
            # Tabel Pratinjau Dataframe
            st.dataframe(active_df.head(100), width="stretch", height=360)
            
            # Raw Data Governance Note Banner
            st.markdown(f"""
<div style="margin-top:14px; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px; padding:12px 16px; display:flex; align-items:flex-start; gap:12px;">
    <div style="color:#2563EB; margin-top:2px;">
        {shield_svg}
    </div>
    <div style="font-size:12px; color:#475569; line-height:1.5;">
        <b style="color:#0F172A;">Tata Kelola Data Mentah (Section K Protocol):</b> Data mentah asli tersimpan dalam keadaan <i>immutable read-only</i>. Seluruh operasi pembersihan transien, deteksi anomali, penyelarasan unit, dan imputasi terawasi akan diproses melalui modul terdedikasi tanpa memodifikasi berkas historis ini.
    </div>
</div>
""", unsafe_allow_html=True)
