"""
Aplikasi Web Audit Energi dan Kinerja PLTGU Blok 1
Titik Masuk Utama (Main Entrypoint) Streamlit
Sesuai Dokumen Kebutuhan Fungsional Pengembang (16 Halaman)
Desain Presisi Sesuai Mockup Visual Pengguna
"""

import os
import json
from datetime import datetime
import importlib
import streamlit as st
import streamlit.components.v1 as st_components
import pandas as pd
import ui.styles
import ui.components
import ui.pages.p00_login as p00_login
import ui.pages.p01_dashboard as p01_dashboard
import ui.pages.p02_import as p02_import
import ui.pages.p03_tag_mapping as p03_tag_mapping
import ui.pages.p04_data_quality as p04_data_quality
import ui.pages.p05_cleaning_filter as p05_cleaning_filter
import ui.pages.p06_kpi_trends as p06_kpi_trends
import ui.pages.p07_equipment as p07_equipment
import ui.pages.p08_mass_energy as p08_mass_energy
import ui.pages.p09_ai_optimization as p09_ai_optimization
import ui.pages.p10_hysys_prep as p10_hysys_prep
import ui.pages.p11_report_export as p11_report_export
import ui.pages.p12_audit_settings as p12_audit_settings
import core.auth as auth
from core.synthetic_data import save_default_synthetic_dataset

# Dynamic reload to ensure instant updates in running Streamlit server
for mod in [auth, ui.styles, ui.components, p00_login, p01_dashboard, p02_import, 
            p03_tag_mapping, p04_data_quality, p05_cleaning_filter, p06_kpi_trends, 
            p07_equipment, p08_mass_energy, p09_ai_optimization, p10_hysys_prep, 
            p11_report_export, p12_audit_settings]:
    importlib.reload(mod)

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Audit Energi & Kinerja PLTGU",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injeksi CSS Kustom Modern
ui.styles.inject_custom_css()

# Injeksi Script Animasi Angka Bergerak (Interactive Count-Up Ticker)
ui.components.render_number_animation_script()

# Script Otomatis Memastikan Sidebar Terbuka saat Awal Muat
if "sidebar_auto_opened" not in st.session_state:
    st.session_state["sidebar_auto_opened"] = True
    st_components.html("""
    <script>
        function ensureSidebarOpen() {
            try {
                const doc = window.parent.document;
                const sidebar = doc.querySelector('section[data-testid="stSidebar"]');
                const isCollapsed = sidebar ? (sidebar.getAttribute('aria-expanded') === 'false' || sidebar.getAttribute('data-collapsed') === 'true') : true;
                if (isCollapsed) {
                    const btn = doc.querySelector('[data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapsedControl"], [data-testid="collapsedControl"], button[aria-label="Expand sidebar"]');
                    if (btn) btn.click();
                }
            } catch(e) {}
        }
        ensureSidebarOpen();
        setTimeout(ensureSidebarOpen, 150);
    </script>
    """, height=0, width=0)


# Inisialisasi Session State
def init_session():
    if "is_initialized" not in st.session_state:
        # Muat default tag mapping
        map_path = "data/mappings/default_mapping_pltgu.json"
        if os.path.exists(map_path):
            with open(map_path, "r") as f:
                map_data = json.load(f)
                st.session_state["tag_mapping"] = map_data.get("tags", {})
        else:
            st.session_state["tag_mapping"] = {}
            
        # Inisialisasi state dataset default (bersih / kosong)
        # Pengguna dapat mengunggah berkas DCS melalui menu 'Import Data Historian'
        st.session_state["raw_df"] = None
        st.session_state["active_df"] = None
        st.session_state["is_synthetic"] = False
        st.session_state["active_version"] = None
        st.session_state["dataset_metadata"] = None
        st.session_state["change_logs"] = []
        st.session_state["is_initialized"] = True
    
    if "is_authenticated" not in st.session_state or not st.session_state["is_authenticated"]:
        # Periksa apakah ada token sesi di query_params untuk auto-login saat reload (F5 / Ctrl + R)
        session_token = st.query_params.get("session")
        if session_token:
            restored_user = auth.verify_session_token(session_token)
            if restored_user:
                st.session_state["is_authenticated"] = True
                st.session_state["auth_user"] = restored_user.to_dict()
                st.session_state["login_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            else:
                st.session_state["is_authenticated"] = False
                st.session_state["auth_user"] = None
                st.query_params.pop("session", None)
        else:
            st.session_state["is_authenticated"] = False
            st.session_state["auth_user"] = None

    if st.session_state.get("is_authenticated") and st.session_state.get("auth_user"):
        uname = st.session_state["auth_user"].get("username", "")
        if uname and "session" not in st.query_params:
            try:
                st.query_params["session"] = auth.create_session_token(uname)
            except Exception:
                pass

init_session()

# SIDEBAR NAVIGASI ULTRA-MODERN SESUAI MOCKUP GAMBAR
with st.sidebar:
    zap_svg = ui.components.LUCIDE_SVG_ICONS["zap"]
    # Brand Header dengan Icon Kilat Biru Neon Vektor SVG
    st.markdown(f"""
    <div style="padding: 0 2px 10px 2px; margin-top: -10px;">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
            <div style="background: linear-gradient(135deg, #0EA5E9 0%, #2563EB 100%); width: 38px; height: 38px; border-radius: 9px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(14, 165, 233, 0.45); color: #FFFFFF;">
                {zap_svg}
            </div>
            <div>
                <div style="color: #FFFFFF; margin: 0; font-size: 16px; font-weight: 800; letter-spacing: 0.5px; line-height: 1.15;">PLTGU BLOK 1</div>
                <div style="font-size: 11px; color: #94A3B8; font-weight: 500; margin-top: 2px; line-height: 1.15;">Audit Energi & Kinerja Termal</div>
            </div>
        </div>
        <div style="display: inline-flex; align-items: center; gap: 6px; background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.1); padding: 4px 10px; border-radius: 20px; font-size: 10.5px; color: #E2E8F0; margin-top: 4px;">
            <span style="display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: #10B981; box-shadow: 0 0 8px #10B981;"></span>
            <span>Konfigurasi 3-3-1 • 450 MW Class</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not auth.is_authenticated(st.session_state):
        img_b64 = ui.components.get_plant_image_b64()
        shield_svg = ui.components.LUCIDE_SVG_ICONS["shield"]
        zap_svg_sm = ui.components.LUCIDE_SVG_ICONS["zap"]
        
        # Wallpaper Pembangkit Nempel di Background Sidebar (Full-Bleed & Darkened Navy)
        st.markdown(f"""
        <style>
        section[data-testid="stSidebar"],
        section[data-testid="stSidebar"][aria-expanded="true"],
        section[data-testid="stSidebar"]:not([aria-expanded="false"]) {{
            background-image: 
                linear-gradient(180deg, 
                    #0d2133 0%, 
                    #0d2133 220px, 
                    rgba(13, 33, 51, 0.60) 340px, 
                    rgba(10, 25, 38, 0.82) 100%
                ),
                url("data:image/png;base64,{img_b64}") !important;
            background-position: center top, center bottom !important;
            background-size: cover, cover !important;
            background-repeat: no-repeat, no-repeat !important;
            border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        }}
        section[data-testid="stSidebar"] div[data-testid="stSidebarContent"],
        section[data-testid="stSidebar"] div[data-testid="stSidebarUserContent"],
        section[data-testid="stSidebar"] .block-container {{
            background: transparent !important;
            background-color: transparent !important;
        }}
        </style>
        """, unsafe_allow_html=True)
        
        st_components.html(f"""
        <script>
            function applySidebarWallpaper() {{
                try {{
                    const doc = window.parent.document;
                    const sidebar = doc.querySelector('section[data-testid="stSidebar"]');
                    const content = doc.querySelector('section[data-testid="stSidebar"] div[data-testid="stSidebarContent"]');
                    if (content) {{
                        content.style.setProperty('background', 'transparent', 'important');
                        content.style.setProperty('background-color', 'transparent', 'important');
                    }}
                    if (sidebar) {{
                        sidebar.style.setProperty('background-image', 'linear-gradient(180deg, #0d2133 0%, #0d2133 220px, rgba(13, 33, 51, 0.60) 340px, rgba(10, 25, 38, 0.82) 100%), url("data:image/png;base64,{img_b64}")', 'important');
                        sidebar.style.setProperty('background-size', 'cover, cover', 'important');
                        sidebar.style.setProperty('background-position', 'center top, center bottom', 'important');
                        sidebar.style.setProperty('background-repeat', 'no-repeat, no-repeat', 'important');
                    }}
                }} catch(e) {{}}
            }}
            applySidebarWallpaper();
            setTimeout(applySidebarWallpaper, 100);
            setTimeout(applySidebarWallpaper, 300);
        </script>
        """, height=0, width=0)
        
        st.markdown(f"""
        <div style="padding: 12px 14px; background: rgba(15, 23, 42, 0.5); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; font-size: 11.5px; color: #94A3B8; line-height: 1.5; margin: 12px 0 16px 0; display: flex; gap: 10px; align-items: flex-start; backdrop-filter: blur(4px);">
            <span style="color: #60A5FA; display: flex; flex-shrink: 0; margin-top: 2px;">{shield_svg}</span>
            <span>Silakan masukkan kredensial pada formulir login untuk mengakses seluruh modul analitik audit.</span>
        </div>
        <div style="padding: 4px 2px; margin-bottom: 10px;">
            <div style="color: #F8FAFC; font-size: 13px; font-weight: 700; line-height: 1.15;">PLTGU Blok 1</div>
            <div style="color: #94A3B8; font-size: 11px; margin-top: 2px; line-height: 1.15;">Efisiensi • Keandalan • Optimalisasi</div>
        </div>
        
        <div style="height: 180px;"></div>
        
        <div style="padding: 10px 4px; display: flex; align-items: center; gap: 10px;">
            <span style="color: #FFFFFF; font-size: 18px; display: flex;">{zap_svg_sm}</span>
            <div>
                <div style="color: #FFFFFF; font-size: 11.5px; font-weight: 700; line-height: 1.3;">Energi yang efisien</div>
                <div style="color: #CBD5E1; font-size: 10.5px; line-height: 1.2;">untuk masa depan yang berkelanjutan</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Reset background wallpaper sidebar saat sudah login
        st_components.html("""
        <script>
            try {
                const doc = window.parent.document;
                const sidebar = doc.querySelector('section[data-testid="stSidebar"]');
                const content = doc.querySelector('section[data-testid="stSidebar"] div[data-testid="stSidebarContent"]');
                if (sidebar) {
                    sidebar.style.removeProperty('background-image');
                    sidebar.style.removeProperty('background-size');
                    sidebar.style.removeProperty('background-position');
                    sidebar.style.removeProperty('background-repeat');
                }
                if (content) {
                    content.style.removeProperty('background');
                    content.style.removeProperty('background-color');
                }
            } catch(e) {}
        </script>
        """, height=0, width=0)

        # Dapatkan profil user dan daftar modul yang diizinkan (RBAC)
        current_user = auth.get_current_user(st.session_state)
        username = current_user.username if current_user else "operator"
        allowed_menu_options = auth.get_allowed_modules(username)

        # Label Kategori & Badge Jumlah Akses Modul
        is_synth = st.session_state.get("is_synthetic", False)
        has_dataset = st.session_state.get("active_df") is not None
        if not has_dataset:
            mode_text = "BELUM ADA DATASET"
        elif is_synth:
            mode_text = "MOD DATA SINTETIS"
        else:
            mode_text = "MOD DATA AKTUAL"
        st.markdown(f'<div class="sidebar-category-title">{mode_text} • {len(allowed_menu_options)} MODUL</div>', unsafe_allow_html=True)

        if "pending_nav" in st.session_state:
            pending = st.session_state.pop("pending_nav")
            if pending in allowed_menu_options:
                st.session_state["nav_selection"] = pending

        if "nav_selection" not in st.session_state or st.session_state["nav_selection"] not in allowed_menu_options:
            q_nav = st.query_params.get("nav")
            if q_nav and q_nav in allowed_menu_options:
                st.session_state["nav_selection"] = q_nav
            else:
                st.session_state["nav_selection"] = allowed_menu_options[0]

        selected_menu = st.radio(
            "NAVIGASI_MODUL",
            allowed_menu_options,
            key="nav_selection",
            label_visibility="collapsed"
        )
        st.query_params["nav"] = selected_menu
        
        # Footer Sesuai Mockup
        st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="padding: 10px 6px; border-top: 1px solid rgba(255, 255, 255, 0.08);">
            <b style="color: #F8FAFC; font-size: 12px;">PLTGU Blok 1</b><br>
            <span style="color: #64748B; font-size: 11px;">Efisiensi • Keandalan • Optimalisasi</span>
        </div>
        """, unsafe_allow_html=True)

# KONTEN UTAMA & ROUTING
if not auth.is_authenticated(st.session_state):
    p00_login.render(st.session_state)
else:
    current_user = auth.get_current_user(st.session_state)
    username = current_user.username if current_user else "operator"
    
    # Proteksi Akses Modul (RBAC Guard)
    if not auth.is_module_allowed(username, selected_menu):
        ui.components.render_restricted_access(selected_menu, current_user)
    elif selected_menu == "Dashboard Utama":
        p01_dashboard.render(st.session_state)
    elif selected_menu == "Import Data Historian":
        p02_import.render(st.session_state)
    elif selected_menu == "Tag Mapping & Unit":
        p03_tag_mapping.render(st.session_state)
    elif selected_menu == "Validasi Kualitas Data":
        p04_data_quality.render(st.session_state)
    elif selected_menu == "Pembersihan Terkendali":
        p05_cleaning_filter.render(st.session_state)
    elif selected_menu == "Tren KPI & Korelasi":
        p06_kpi_trends.render(st.session_state)
    elif selected_menu == "Analisis Sub-Sistem Unit":
        p07_equipment.render(st.session_state)
    elif selected_menu == "Neraca Massa & Energi":
        p08_mass_energy.render(st.session_state)
    elif selected_menu == "Deteksi Anomali AI":
        p09_ai_optimization.render(st.session_state)
    elif selected_menu == "Persiapan Aspen HYSYS":
        p10_hysys_prep.render(st.session_state)
    elif selected_menu == "Laporan Formal & Ekspor":
        p11_report_export.render(st.session_state)
    elif selected_menu == "Audit Log & Pengaturan":
        p12_audit_settings.render(st.session_state)


