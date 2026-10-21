"""
CSS & Ultra-Modern Industrial Design System Styling untuk Website Audit Energi PLTGU
Mereplikasi 100% desain modern sesuai acuan mockup visual:
- Menyembunyikan header Streamlit default (Deploy, hamburger menu)
- Menyembunyikan radio bullets/circles bawaan Streamlit secara total
- Topbar pencarian, notifikasi, dan avatar profil user Rafli
- Sidebar Deep Navy modern dengan logo neon, pill status, dan nav pills aktif
- Hero Card dengan ilustrasi PLTGU dan breadcrumb pill
- 8 Kartu KPI dengan icon bulat berwarna, pill status 'Normal', dan tren persentase
- Kontainer grafik modern dengan filter interval dropdown
"""

import streamlit as st
from core.config import COLOR_PALETTE, STATUS_COLORS

def inject_custom_css():
    """Menyuntikkan CSS modern presisi sesuai mockup visual pengguna."""
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');
    
    :root {{
        --primary: #12304A;
        --primary-dark: #0D2133;
        --secondary: #2F6690;
        --accent: #2A9D8F;
        --canvas: #F8FAFC;
        --surface: #FFFFFF;
        --text: #1E293B;
        --muted: #64748B;
        --border: #E2E8F0;
        --success: #16A34A;
        --success-bg: #DCFCE7;
    }}
    
    /* 1. HILANGKAN ELEMEN DEPLOY & MENU AKSI DI KANAN ATAS (TETAP TAMPILKAN TOMBOL BUKA SIDEBAR) */
    [data-testid="stAppDeployButton"],
    [data-testid="stToolbarActions"],
    [data-testid="stStatusWidget"],
    #MainMenu,
    [data-testid="stMainMenu"],
    footer {{
        display: none !important;
        visibility: hidden !important;
    }}
    
    /* 1.1. HILANGKAN IKON ANCHOR LINK BAWAAN STREAMLIT PADA SEMUA HEADING / JUDUL */
    [data-testid="stHeaderActionElements"],
    [data-testid="stHeaderActionButton"],
    [data-testid="stHeaderActionAnchor"],
    [data-testid="stHeadingWithActionElements"] [data-testid="stHeaderActionElements"],
    [data-testid="stHeadingWithActionElements"]:hover [data-testid="stHeaderActionElements"],
    [data-testid="stHeadingWithActionElements"] button,
    [data-testid="stHeadingWithActionElements"] a,
    .stHeading [data-testid="stHeaderActionElements"],
    .stHeadingContainer a,
    a.heading-anchor,
    a.anchor-link,
    h1 a, h2 a, h3 a, h4 a, h5 a, h6 a,
    h1 a.anchor, h2 a.anchor, h3 a.anchor, h4 a.anchor, h5 a.anchor, h6 a.anchor,
    h1 > a[href*="#"], h2 > a[href*="#"], h3 > a[href*="#"], h4 > a[href*="#"], h5 > a[href*="#"], h6 > a[href*="#"] {{
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
        width: 0 !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    
    header[data-testid="stHeader"] {{
        background: transparent !important;
        pointer-events: none !important;
        height: auto !important;
        z-index: 99999 !important;
    }}
    
    header [data-testid="stToolbar"] {{
        background: transparent !important;
        pointer-events: none !important;
    }}
    
    [data-testid="stExpandSidebarButton"] {{
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: auto !important;
        position: fixed !important;
        top: 12px !important;
        left: 12px !important;
        z-index: 9999999 !important;
        background: #12304A !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        border-radius: 9px !important;
        padding: 6px 10px !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4) !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }}
    [data-testid="stExpandSidebarButton"]:hover {{
        background: #2563EB !important;
        border-color: #60A5FA !important;
        transform: scale(1.06) !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.45) !important;
    }}
    [data-testid="stExpandSidebarButton"] * {{
        color: #FFFFFF !important;
        stroke: #FFFFFF !important;
        fill: #FFFFFF !important;
    }}
    [data-testid="stExpandSidebarButton"] svg {{
        width: 22px !important;
        height: 22px !important;
    }}


    
    /* Typography Global */
    html, body, [class*="css"], .stMarkdown, .stText {{
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif !important;
        color: var(--text);
        letter-spacing: -0.01em;
        -webkit-font-smoothing: antialiased;
    }}
    
    /* Reset Khusus Teks Konten Markdown (Tidak memengaruhi Button, Popover, atau Upload Widget) */
    .stMarkdown > div > h1,
    .stMarkdown > div > h2,
    .stMarkdown > div > h3,
    .stMarkdown > div > h4,
    .stMarkdown > div > h5,
    .stMarkdown > div > h6 {{
        margin-top: 0 !important;
        margin-bottom: 3px !important;
        line-height: 1.18 !important;
        letter-spacing: -0.02em !important;
    }}
    
    .stMarkdown > div > p {{
        margin-top: 0 !important;
        margin-bottom: 4px !important;
        line-height: 1.35 !important;
    }}
    
    /* Kanvas Aplikasi */
    .stApp {{
        background-color: var(--canvas) !important;
    }}
    
    /* Hilangkan padding default Streamlit berlebihan */
    .block-container {{
        padding-top: 0.8rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 98% !important;
    }}
    
    /* Ultra-Modern Alert Banners (st.success, st.error, st.warning, st.info) */
    div[data-testid="stAlert"] {{
        border-radius: 10px !important;
        padding: 9px 16px !important;
        border: 1px solid rgba(15, 23, 42, 0.08) !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03) !important;
        margin-top: 6px !important;
        margin-bottom: 12px !important;
    }}
    div[data-testid="stAlert"] [data-testid="stAlertContent"] {{
        align-items: center !important;
        gap: 10px !important;
    }}
    div[data-testid="stAlert"] [data-testid="stAlertContent"] [data-testid="stAlertIcon"] {{
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    div[data-testid="stAlert"] [data-testid="stAlertContent"] [data-testid="stAlertIcon"] span,
    div[data-testid="stAlert"] [data-testid="stAlertContent"] [data-testid="stAlertIcon"] svg {{
        font-size: 21px !important;
        width: 21px !important;
        height: 21px !important;
    }}
    div[data-testid="stAlert"] p {{
        font-size: 13.5px !important;
        font-weight: 600 !important;
        margin: 0 !important;
        line-height: 1.35 !important;
    }}
    
    /* Topbar Modern */
    .topbar-wrapper {{
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 10px 18px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }}
    .search-box {{
        display: flex;
        align-items: center;
        background: #F8FAFC;
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 8px 14px;
        width: 360px;
        color: var(--muted);
        font-size: 13px;
        gap: 8px;
    }}
    .topbar-right {{
        display: flex;
        align-items: center;
        gap: 16px;
    }}
    .notification-btn {{
        position: relative;
        background: #F1F5F9;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        font-size: 16px;
    }}
    .notif-badge {{
        position: absolute;
        top: 2px;
        right: 2px;
        width: 8px;
        height: 8px;
        background: #EF4444;
        border-radius: 50%;
        border: 2px solid #FFFFFF;
    }}
    .user-profile {{
        display: flex;
        align-items: center;
        gap: 10px;
        cursor: pointer;
        padding: 4px 8px;
        border-radius: 8px;
        transition: background 0.2s ease;
    }}
    .user-profile:hover {{
        background: #F8FAFC;
    }}
    .user-avatar {{
        width: 34px;
        height: 34px;
        border-radius: 50%;
        background: #0F172A;
        color: #FFFFFF;
        font-weight: 700;
        font-size: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    .user-name {{
        font-size: 13.5px;
        font-weight: 700;
        color: var(--text);
    }}
    
    /* Popover Topbar Profil */
    div[data-testid="stPopover"] {{
        display: flex !important;
        align-items: center !important;
        justify-content: flex-end !important;
        width: 100% !important;
    }}
    div[data-testid="stPopover"] > button {{
        background: #FFFFFF !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        padding: 5px 14px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03) !important;
        color: #0F172A !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        height: 38px !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 6px !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        justify-content: space-between !important;
    }}
    div[data-testid="stPopover"] > button:hover {{
        border-color: #38BDF8 !important;
        background: #F8FAFC !important;
        box-shadow: 0 3px 10px rgba(14, 165, 233, 0.15) !important;
    }}
    div[data-testid="stPopover"] > button span[data-testid="stIconMaterial"] {{
        color: #2563EB !important;
        font-size: 19px !important;
        display: inline-flex !important;
        align-items: center !important;
    }}
    div[data-testid="stPopoverBody"] {{
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 14px !important;
        box-shadow: 0 16px 36px rgba(0, 0, 0, 0.14) !important;
        padding: 16px !important;
        min-width: 330px !important;
    }}
    
    /* Topbar Search Selectbox Fungsional dengan Ikon Vektor Lucide SVG */
    div[data-testid="column"]:first-child div[data-testid="stSelectbox"] {{
        margin-top: 0px !important;
    }}
    div[data-testid="column"]:first-child div[data-testid="stSelectbox"] > div > div {{
        background-color: #F8FAFC !important;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%2364748B' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='11' cy='11' r='8'/%3E%3Cline x1='21' y1='21' x2='16.65' y2='16.65'/%3E%3C/svg%3E") !important;
        background-repeat: no-repeat !important;
        background-position: 12px center !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        min-height: 38px !important;
        height: 38px !important;
        padding-left: 36px !important;
        padding-right: 12px !important;
        font-size: 13px !important;
        color: #334155 !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02) !important;
        transition: all 0.2s ease !important;
    }}
    div[data-testid="column"]:first-child div[data-testid="stSelectbox"] > div > div:hover {{
        border-color: #38BDF8 !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 2px 8px rgba(14, 165, 233, 0.12) !important;
    }}
    div[data-testid="column"]:first-child div[data-testid="stSelectbox"] > div > div:focus-within {{
        border-color: #0EA5E9 !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.15) !important;
    }}

    /* Baseweb Dropdown Listbox Modern Styling */
    div[data-baseweb="popover"] ul[role="listbox"] {{
        border-radius: 12px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 16px 36px rgba(15, 23, 42, 0.14) !important;
        padding: 6px !important;
        background: #FFFFFF !important;
    }}
    div[data-baseweb="popover"] ul[role="listbox"] li[role="option"] {{
        border-radius: 8px !important;
        padding: 8px 12px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        color: #1E293B !important;
        transition: all 0.15s ease !important;
    }}
    div[data-baseweb="popover"] ul[role="listbox"] li[role="option"]:hover,
    div[data-baseweb="popover"] ul[role="listbox"] li[role="option"][aria-selected="true"] {{
        background: #EFF6FF !important;
        color: #1D4ED8 !important;
        font-weight: 600 !important;
    }}

    /* Bell Notification Popover Button Lingkaran Modern & Sleek */
    div[data-testid="column"]:nth-child(2) div[data-testid="stPopover"] {{
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
    }}
    div[data-testid="column"]:nth-child(2) div[data-testid="stPopover"] > button {{
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 50% !important;
        width: 38px !important;
        height: 38px !important;
        min-width: 38px !important;
        max-width: 38px !important;
        padding: 0 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        position: relative !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
        transition: all 0.2s ease !important;
    }}
    div[data-testid="column"]:nth-child(2) div[data-testid="stPopover"] > button:hover {{
        border-color: #38BDF8 !important;
        background: #F8FAFC !important;
        box-shadow: 0 3px 10px rgba(14, 165, 233, 0.18) !important;
        transform: scale(1.05) !important;
    }}
    /* Sembunyikan panah chevron pada tombol notifikasi bulat */
    div[data-testid="column"]:nth-child(2) div[data-testid="stPopover"] > button svg[data-testid="stIconChevronDown"] {{
        display: none !important;
    }}
    /* Ikon lonceng Material modern */
    div[data-testid="column"]:nth-child(2) div[data-testid="stPopover"] > button span[data-testid="stIconMaterial"] {{
        color: #475569 !important;
        font-size: 20px !important;
        margin: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    div[data-testid="column"]:nth-child(2) div[data-testid="stPopover"] > button:hover span[data-testid="stIconMaterial"] {{
        color: #0284C7 !important;
    }}
    /* Lencana titik merah notifikasi aktif */
    div[data-testid="column"]:nth-child(2) div[data-testid="stPopover"] > button::after {{
        content: '';
        position: absolute;
        top: 6px;
        right: 6px;
        width: 7.5px;
        height: 7.5px;
        background: #EF4444;
        border-radius: 50%;
        border: 1.5px solid #FFFFFF;
        box-shadow: 0 0 6px rgba(239, 68, 68, 0.7);
    }}
    
    /* Sidebar Deep Navy Modern - Lebar proporsional pas sesuai teks menu */
    section[data-testid="stSidebar"][aria-expanded="true"],
    section[data-testid="stSidebar"]:not([aria-expanded="false"]) {{
        background: linear-gradient(180deg, #0d2133 0%, #102a45 50%, #0d1e2e 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.2) !important;
        min-width: 270px !important;
        max-width: 285px !important;
        width: 275px !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: #FFFFFF !important;
    }}
    
    /* Hilangkan space kosong berlebih di bagian atas sidebar secara total & beri padding samping seimbang */
    section[data-testid="stSidebar"] div[data-testid="stSidebarContent"] {{
        background: transparent !important;
        background-color: transparent !important;
        padding-top: 8px !important;
        padding-bottom: 1.5rem !important;
        padding-left: 12px !important;
        padding-right: 12px !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stSidebarUserContent"],
    section[data-testid="stSidebar"] .block-container {{
        padding-top: 0 !important;
        margin-top: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        max-width: 100% !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stLogoSpacer"] {{
        display: none !important;
        height: 0 !important;
        min-height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {{
        height: 32px !important;
        min-height: 32px !important;
        margin-bottom: 0 !important;
        padding: 0 4px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-end !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] {{
        position: static !important;
        margin-left: auto !important;
    }}
    
    /* Category title text */
    .sidebar-category-title {{
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.8px;
        color: #7CA1C7;
        text-transform: uppercase;
        margin: 10px 0 8px 6px;
    }}
    
    /* Menu Navigasi di Sidebar */
    section[data-testid="stSidebar"] div[data-testid="stRadio"] {{
        width: 100% !important;
        box-sizing: border-box !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stRadioGroup"] {{
        width: 100% !important;
        gap: 3px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: stretch !important;
        box-sizing: border-box !important;
    }}
    
    /* Pastikan SEMUA item wrapper (div / label) di radio group merentang 100% */
    section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stRadioGroup"] > div,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stRadioGroup"] > label {{
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        align-self: stretch !important;
        box-sizing: border-box !important;
    }}
    
    /* 1. Sembunyikan HANYA radio circle bawaan Streamlit (div:first-child) */
    section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stRadioOption"] > div > div:first-child,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stRadioOption"] input {{
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        opacity: 0 !important;
        pointer-events: none !important;
        position: absolute !important;
    }}
    
    /* 2. Styling container option sebagai pill navigation dengan lebar 100% rata */
    section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stRadioOption"] {{
        display: flex !important;
        align-items: center !important;
        background: transparent !important;
        border-radius: 10px !important;
        padding: 9px 12px !important;
        margin-bottom: 2px !important;
        border: 1px solid transparent !important;
        transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1) !important;
        cursor: pointer !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stRadioOption"] > div {{
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stRadioOption"] [data-testid="stMarkdownContainer"] {{
        width: 100% !important;
        box-sizing: border-box !important;
    }}
    
    section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stRadioOption"]:hover {{
        background: rgba(255, 255, 255, 0.06) !important;
        transform: translateX(3px) !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stRadioOption"]:hover p,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stRadioOption"]:hover span {{
        color: #FFFFFF !important;
    }}
    
    /* Teks Menu saat tidak aktif: Soft Ice Blue persis mockup */
    section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stRadioOption"] p,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stRadioOption"] span {{
        font-size: 13px !important;
        font-weight: 500 !important;
        margin: 0 !important;
        color: #8EB0D4 !important;
        letter-spacing: 0.2px !important;
        line-height: 1.4 !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }}
    
    /* 3. Styling saat AKTIF / SELECTED: Blue pill dengan left accent dan border halus merentang 100% */
    section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stRadioOption"][data-selected="true"],
    section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stRadioOption"]:has(input:checked) {{
        background: linear-gradient(90deg, rgba(30, 109, 235, 0.75) 0%, rgba(21, 87, 205, 0.65) 100%) !important;
        border: 1px solid rgba(96, 165, 250, 0.5) !important;
        border-left: 3.5px solid #60A5FA !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 14px rgba(30, 109, 235, 0.35) !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }}
    
    /* Teks Menu saat aktif: Crisp white semibold */
    section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stRadioOption"][data-selected="true"] p,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stRadioOption"][data-selected="true"] span,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stRadioOption"]:has(input:checked) p,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stRadioOption"]:has(input:checked) span {{
        color: #FFFFFF !important;
        font-weight: 700 !important;
        letter-spacing: 0.2px !important;
    }}
    
    /* Hero Card Modern (Dengan Ilustrasi Pembangkit) */
    .dashboard-hero-card {{
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02), 0 6px 16px -4px rgba(0,0,0,0.03);
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: relative;
        overflow: hidden;
    }}
    .hero-breadcrumb {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        color: #0D9488;
        font-size: 12.5px;
        font-weight: 700;
        margin-bottom: 6px;
    }}
    .hero-main-title {{
        font-size: 26px;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.02em;
        margin: 0 0 2px 0 !important;
        line-height: 1.15 !important;
    }}
    .hero-main-subtitle {{
        font-size: 13.5px;
        color: #64748B;
        margin: 0 0 10px 0 !important;
        max-width: 650px;
        line-height: 1.3 !important;
    }}
    .hero-spec-pill {{
        background: #FFFBEB;
        border: 1px solid #FDE68A;
        border-radius: 20px;
        padding: 5px 14px;
        font-size: 12px;
        font-weight: 700;
        color: #B45309;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }}
    .hero-illustration-container {{
        width: 300px;
        height: 135px;
        display: flex;
        align-items: center;
        justify-content: flex-end;
    }}
    
    /* Modern KPI Cards (Grid 4 Kolom Sesuai Mockup - Tinggi Seragam 195px) */
    .modern-kpi-card {{
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 16px 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 195px !important;
        min-height: 195px !important;
        max-height: 195px !important;
        box-sizing: border-box !important;
        overflow: hidden !important;
    }}
    .modern-kpi-card:hover {{
        transform: translateY(-2.5px);
        box-shadow: 0 8px 20px -4px rgba(0, 0, 0, 0.06);
        border-color: #CBD5E1;
    }}
    .modern-kpi-card > div:first-child {{
        display: flex;
        flex-direction: column;
        flex: 1;
        justify-content: flex-start;
    }}
    .kpi-header-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }}
    .kpi-icon-circle {{
        width: 36px;
        height: 36px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
    }}
    .kpi-pill-normal {{
        background: #DCFCE7;
        color: #16A34A;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 700;
    }}
    .kpi-label-text {{
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: #475569;
        margin-bottom: 4px;
    }}
    .kpi-number-display {{
        display: flex;
        align-items: baseline;
        gap: 6px;
    }}
    .kpi-number-val {{
        font-size: 26px;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.15;
        letter-spacing: -0.02em;
        font-variant-numeric: tabular-nums !important;
        display: inline-block !important;
        transition: color 0.15s ease !important;
    }}
    .modern-kpi-card:hover .kpi-number-val {{
        color: #2563EB;
    }}
    .kpi-unit-text {{
        font-size: 13px;
        font-weight: 600;
        color: #64748B;
    }}
    .kpi-trend-row {{
        display: flex;
        align-items: center;
        gap: 4px;
        margin-top: 6px;
        font-size: 11.5px;
        font-weight: 600;
    }}
    .trend-up {{
        color: #16A34A;
    }}
    .trend-down-good {{
        color: #16A34A;
    }}
    .trend-subtext {{
        color: #94A3B8;
        font-weight: 400;
        margin-left: 2px;
    }}
    .kpi-trace-footer {{
        margin-top: 10px;
        padding-top: 8px;
        border-top: 1px solid #F1F5F9;
        font-size: 10.5px;
        color: #94A3B8;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    
    /* Modern Chart Container */
    .chart-card-container {{
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 22px 24px;
        margin-top: 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }}
    .chart-card-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
    }}
    .chart-header-left {{
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    .chart-header-icon {{
        width: 38px;
        height: 38px;
        background: #EFF6FF;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        color: #1E6DEB;
    }}
    .chart-title-text {{
        font-size: 15.5px;
        font-weight: 700;
        color: #0F172A;
        margin: 0 !important;
        line-height: 1.15 !important;
    }}
    .chart-subtitle-text {{
        font-size: 12px;
        color: #64748B;
        margin: 2px 0 0 0 !important;
        line-height: 1.25 !important;
    }}
    .chart-interval-badge {{
        background: #F8FAFC;
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 6px 14px;
        font-size: 12px;
        font-weight: 600;
        color: #475569;
        display: flex;
        align-items: center;
        gap: 6px;
    }}
    
    /* Fix global Streamlit Metric text colors */
    div[data-testid="stMetric"] {{
        background: transparent !important;
    }}
    div[data-testid="stMetricLabel"], div[data-testid="stMetricLabel"] * {{
        color: #475569 !important;
        font-size: 12.5px !important;
        font-weight: 600 !important;
    }}
    div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] * {{
        color: #0F172A !important;
        font-size: 20px !important;
        font-weight: 800 !important;
    }}
    div[data-testid="stMetricDelta"], div[data-testid="stMetricDelta"] * {{
        font-size: 12px !important;
    }}
    
    /* Modern Streamlit Container with border & Forms */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: #FFFFFF !important;
        border: 1px solid var(--border) !important;
        border-radius: 14px !important;
        padding: 18px 20px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02) !important;
        margin-bottom: 16px !important;
    }}
    div[data-testid="stForm"] {{
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 18px !important;
        padding: 24px 28px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05) !important;
    }}
    div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button {{
        background: linear-gradient(90deg, #1E6DEB 0%, #0E58D0 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 14.5px !important;
        padding: 12px 20px !important;
        border-radius: 10px !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(30, 109, 235, 0.35) !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
        width: 100% !important;
    }}
    div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button:hover {{
        background: linear-gradient(90deg, #2563EB 0%, #1D4ED8 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.45) !important;
    }}
    div[data-testid="stTextInput"] input {{
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
        font-size: 13.5px !important;
        color: #0F172A !important;
        transition: all 0.15s ease !important;
    }}
    div[data-testid="stTextInput"] input:focus {{
        border-color: #2563EB !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12) !important;
    }}
    div[data-testid="column"] button[kind="secondary"] {{
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 12px 14px !important;
        color: #0F172A !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
        transition: all 0.2s ease !important;
        min-height: 54px !important;
        white-space: pre-line !important;
        line-height: 1.35 !important;
    }}
    div[data-testid="column"] button[kind="secondary"]:hover {{
        border-color: #3B82F6 !important;
        background: #F8FAFC !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.15) !important;
    }}
    div[data-testid="stExpander"] {{
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03) !important;
        overflow: hidden !important;
    }}
    div[data-testid="stExpander"] summary {{
        font-weight: 600 !important;
        color: #1E293B !important;
        font-size: 13px !important;
    }}
    
    /* Modern Streamlit File Uploader styling */
    div[data-testid="stFileUploader"] {{
        background: #FFFFFF !important;
        border: 1.5px dashed #CBD5E1 !important;
        border-radius: 12px !important;
        padding: 10px 14px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02) !important;
    }}
    div[data-testid="stFileUploader"]:hover {{
        border-color: #2563EB !important;
        background: #F8FAFC !important;
    }}
    div[data-testid="stFileUploader"] section {{
        background: transparent !important;
        padding: 4px !important;
    }}
    div[data-testid="stFileUploader"] section * {{
        color: #1E293B !important;
    }}
    div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] {{
        color: #475569 !important;
    }}
    div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] * {{
        color: #475569 !important;
    }}
    div[data-testid="stFileUploader"] button {{
        background: #F1F5F9 !important;
        color: #1E293B !important;
        border: 1px solid #CBD5E1 !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        transition: all 0.15s ease !important;
    }}
    div[data-testid="stFileUploader"] button:hover {{
        background: #1E6DEB !important;
        color: #FFFFFF !important;
        border-color: #1E6DEB !important;
    }}
    
    /* Import Action Cards */
    .import-action-card {{
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 20px 22px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-sizing: border-box;
    }}
    .import-card-header {{
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;
    }}
    .import-card-icon {{
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    .import-card-title {{
        font-size: 16px;
        font-weight: 700;
        color: #0F172A;
        margin: 0;
    }}
    .import-card-desc {{
        font-size: 13px;
        color: #64748B;
        line-height: 1.5;
        margin: 0 0 14px 0;
    }}
    
    /* Metadata KPI Stats Grid */
    .meta-stat-grid {{
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 14px;
        margin-bottom: 18px;
    }}
    .meta-stat-card {{
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 14px 16px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}
    .meta-stat-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        background: #FFFFFF;
        border-color: #CBD5E1;
    }}
    .meta-stat-top {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 8px;
    }}
    .meta-stat-icon {{
        width: 32px;
        height: 32px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    .meta-stat-label {{
        font-size: 11.5px;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .meta-stat-value {{
        font-size: 17px;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.01em;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 4px;
    }}
    .meta-stat-sub {{
        font-size: 11px;
        font-weight: 600;
        color: #94A3B8;
        display: flex;
        align-items: center;
        gap: 4px;
    }}
    
    /* Tag Mapping & Schema Alignment Styles */
    .mapping-toolbar-card {{
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 18px 22px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }}
    .mapping-progress-track {{
        width: 100%;
        height: 7px;
        background: #F1F5F9;
        border-radius: 999px;
        overflow: hidden;
        margin: 8px 0;
    }}
    .mapping-progress-fill {{
        height: 100%;
        background: linear-gradient(90deg, #2563EB 0%, #10B981 100%);
        border-radius: 999px;
        transition: width 0.3s ease;
    }}
    .mapping-row-card {{
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: all 0.2s ease;
    }}
    .mapping-row-card:hover {{
        border-color: #93C5FD;
        box-shadow: 0 2px 8px rgba(37,99,235,0.04);
        background: #FAFCFF;
    }}
    .mapping-tag-code {{
        font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
        font-size: 12px;
        font-weight: 700;
        color: #1D4ED8;
        background: #EFF6FF;
        border: 1px solid #DBEAFE;
        padding: 2px 7px;
        border-radius: 6px;
    }}
    .mapping-unit-badge {{
        font-size: 11px;
        font-weight: 700;
        color: #047857;
        background: #ECFDF5;
        border: 1px solid #A7F3D0;
        padding: 2px 7px;
        border-radius: 6px;
    }}
    
    /* Streamlit Pills Styling */
    div[data-testid="stPills"] button, div[data-testid="stSegmentedControl"] button {{
        font-weight: 600 !important;
        font-size: 13px !important;
        border-radius: 10px !important;
        transition: all 0.2s ease !important;
    }}
    div[data-testid="stPills"] button[aria-selected="true"], div[data-testid="stSegmentedControl"] button[aria-selected="true"] {{
        background: #1E6DEB !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 8px rgba(30,109,235,0.25) !important;
    }}
    
    /* Sidebar User Profile Card */
    .sidebar-user-card {{
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 10px;
        padding: 10px 12px;
        margin: 8px 0 12px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    .sidebar-user-avatar {{
        width: 34px;
        height: 34px;
        background: linear-gradient(135deg, #0EA5E9 0%, #2563EB 100%);
        border-radius: 50%;
        color: #FFFFFF;
        font-weight: 800;
        font-size: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 6px rgba(14, 165, 233, 0.4);
    }}
    .sidebar-user-info {{
        flex: 1;
        overflow: hidden;
    }}
    .sidebar-user-name {{
        font-size: 12.5px;
        font-weight: 700;
        color: #F8FAFC !important;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    .sidebar-user-role {{
        font-size: 10.5px;
        color: #38BDF8 !important;
        font-weight: 600;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

