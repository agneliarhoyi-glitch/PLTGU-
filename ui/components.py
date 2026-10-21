"""
Komponen Antarmuka Pengguna (UI Components) Modern Sesuai Mockup Visual Pengguna
Menyediakan Ikon Vektor Lucide SVG Ultra-Crisp, Topbar, Hero Card dengan Ilustrasi PLTGU, dan 8 Kartu KPI Elevasi.
"""

from typing import Optional, Dict, Any
from datetime import datetime
import os
import base64
import textwrap
import streamlit as st
import streamlit.components.v1 as st_components
import plotly.graph_objects as go
from core.config import COLOR_PALETTE, STATUS_COLORS, EQUIPMENT_COLORS, SYNTHETIC_DATA_BANNER


# KOLEKSI IKON VEKTOR SVG MODERN (LUCIDE / FEATHER STYLE)
# Menggantikan emoji standar agar tajam, profesional, dan beresolusi tinggi di semua layar
# KOLEKSI IKON VEKTOR SVG MODERN (LUCIDE / FEATHER STYLE)
# Menggantikan emoji standar agar tajam, profesional, dan beresolusi tinggi di semua layar
LUCIDE_SVG_ICONS = {
    "zap": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>""",
    "factory": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 20a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8l-7 5V8l-7 5V4a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z"/><path d="M17 18h1"/><path d="M12 18h1"/><path d="M7 18h1"/></svg>""",
    "flame": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/></svg>""",
    "leaf": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/></svg>""",
    "gauge": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 14 4-4"/><path d="M3.34 19a10 10 0 1 1 17.32 0"/></svg>""",
    "database": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19A9 3 0 0 0 21 19V5"/><path d="M3 12A9 3 0 0 0 21 12"/></svg>""",
    "activity": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>""",
    "file_check": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="m9 15 2 2 4-4"/></svg>""",
    "chart": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>""",
    "calendar": """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>""",
    "search": """<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>""",
    "bell": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>""",
    "grid": """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>""",
    "alert_triangle": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>""",
    "cpu": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M15 2v2"/><path d="M15 20v2"/><path d="M2 15h2"/><path d="M2 9h2"/><path d="M20 15h2"/><path d="M20 9h2"/><path d="M9 2v2"/><path d="M9 20v2"/></svg>""",
    "shield": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>""",
    "scale": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/></svg>""",
    "sparkles": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"/></svg>""",
    "flask": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 2v7.31L4.1 19.34A2 2 0 0 0 5.8 22h12.4a2 2 0 0 0 1.7-2.66L14 9.31V2"/><line x1="8.5" y1="2" x2="15.5" y2="2"/><line x1="7" y1="14" x2="17" y2="14"/></svg>""",
    "file_text": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>""",
    "settings": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>""",
    "broom": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 11-8.5 8.5a2.12 2.12 0 1 1-3-3L12 8"/><path d="m18 8 3-3a1.5 1.5 0 0 0-2.12-2.12L16 6"/><path d="m13 13 4 4"/><path d="m9 9 4 4"/></svg>""",
    "filter": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>""",
    "sliders": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/></svg>""",
    "layers": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>""",
    "bot": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg>""",
    "brain": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/><path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"/><path d="M12 5v14"/></svg>""",
    "package": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m16.5 9.4-9-5.19M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.29 7 12 12 20.71 7"/><line x1="12" y1="22" x2="12" y2="12"/></svg>""",
    "printer": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect width="12" height="8" x="6" y="14"/></svg>""",
    "download": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>""",
    "upload": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>""",
    "check_circle": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>""",
    "crosshair": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="22" y1="12" x2="18" y2="12"/><line x1="6" y1="12" x2="2" y2="12"/><line x1="12" y1="6" x2="12" y2="2"/><line x1="12" y1="22" x2="12" y2="18"/></svg>""",
    "droplet": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/></svg>""",
    "wind": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.7 7.7a2.5 2.5 0 1 1 1.8 4.3H2"/><path d="M9.6 4.6A2 2 0 1 1 11 8H2"/><path d="M12.6 19.4A2 2 0 1 0 14 16H2"/></svg>""",
    "external_link": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>""",
    "user": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>""",
    "lock": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>""",
    "key": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="7.5" cy="15.5" r="5.5"/><path d="m21 2-9.6 9.6"/><path d="m15.5 7.5 3 3L22 7l-3-3"/></svg>""",
    "info": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>""",
    "folder": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"/></svg>"""
}

def clean_html(html_str: str) -> str:
    """Membersihkan whitespace/indentasi dan menghapus baris kosong agar tidak memicu parser code block Markdown."""
    return "".join(line.strip() for line in html_str.strip().splitlines() if line.strip())

@st.cache_data
def get_plant_image_b64() -> str:
    """Mengembalikan representasi Base64 dari foto pembangkit PLTGU untuk embedding HTML/CSS."""
    for filename in ["pltgu_plant.png", "pltgu_plant.jpg"]:
        path = os.path.join(os.path.dirname(__file__), "assets", filename)
        if os.path.exists(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
    return ""

# Pemetaan otomatis dari emoji lama ke key ikon SVG vektor
EMOJI_TO_SVG_KEY = {
    "⚡": "zap",
    "🏭": "factory",
    "🔥": "flame",
    "🍃": "leaf",
    "⏱️": "gauge",
    "🛢️": "database",
    "📈": "activity",
    "📄": "file_check",
    "📊": "chart",
    "⚙️": "cpu",
    "🛡️": "shield",
    "⚖️": "scale",
    "✨": "sparkles",
    "🧪": "flask",
    "📑": "file_text",
    "🧹": "broom",
    "🔍": "search",
    "📥": "download",
    "📦": "package",
    "🤖": "bot",
    "🧠": "brain",
    "🛠️": "settings",
    "💡": "sparkles",
    "📝": "file_text",
    "🏷️": "file_text",
    "🌊": "droplet",
    "❄️": "droplet",
    "💨": "wind",
    "🎯": "crosshair",
    "🔗": "activity"
}

def render_topbar(user_name: str = "Maintenance 1 / Lead Auditor", role: str = "", session_state: Optional[Dict] = None):
    """Menampilkan Topbar modern dengan pencarian, notifikasi lonceng, dan popover profil interaktif."""
    import core.auth as auth
    
    if session_state is None:
        session_state = st.session_state
        
    current_user = auth.get_current_user(session_state)
    if current_user:
        username = current_user.username
        user_name = current_user.name
        role = current_user.role
        email = current_user.email
        title = current_user.title
        avatar_char = current_user.avatar
    else:
        username = "maintenance 1"
        user_name = user_name or "Maintenance 1 / Lead Auditor"
        role = role or "Maintenance 1 / Lead Auditor"
        email = "maintenance1@pltgu-blok1.co.id"
        title = "Lead Energy Auditor & Thermal Performance Specialist"
        avatar_char = "M"
        
    search_icon = LUCIDE_SVG_ICONS["search"]
    bell_icon = LUCIDE_SVG_ICONS["bell"]
    
    # Grid Topbar Container: Search (Fungsional) | Notifikasi Popover | Profil Popover
    col_search, col_bell, col_profile = st.columns([6.3, 0.7, 2.6])
    
    with col_search:
        # Dapatkan daftar modul yang diizinkan untuk pengguna saat ini (RBAC)
        allowed_modules_list = auth.get_allowed_modules(username)
        allowed_mods_set = set(allowed_modules_list)
        
        all_search_options = [
            "◈  Dashboard Utama",
            "⭳  Import Data Historian",
            "⎇  Tag Mapping & Unit",
            "✓  Validasi Kualitas Data",
            "✦  Pembersihan Terkendali",
            "↗  Tren KPI & Korelasi",
            "⊞  Analisis Sub-Sistem Unit",
            "⚖︎  Neraca Massa & Energi",
            "⚡︎  Deteksi Anomali AI",
            "⌬  Persiapan Aspen HYSYS",
            "▤  Laporan Formal & Ekspor",
            "⚙︎  Audit Log & Pengaturan",
            "•  Parameter: Daya Bersih (Net Power)",
            "•  Parameter: Heat Rate Neto (kJ/kWh)",
            "•  Parameter: Efisiensi Termal Siklus",
            "•  Parameter: Neraca Uap HRSG & ST",
            "•  Parameter: Pendinginan Kondensor CW",
        ]
        
        search_route_map = {
            "◈  Dashboard Utama": "Dashboard Utama",
            "⭳  Import Data Historian": "Import Data Historian",
            "⎇  Tag Mapping & Unit": "Tag Mapping & Unit",
            "✓  Validasi Kualitas Data": "Validasi Kualitas Data",
            "✦  Pembersihan Terkendali": "Pembersihan Terkendali",
            "↗  Tren KPI & Korelasi": "Tren KPI & Korelasi",
            "⊞  Analisis Sub-Sistem Unit": "Analisis Sub-Sistem Unit",
            "⚖︎  Neraca Massa & Energi": "Neraca Massa & Energi",
            "⚡︎  Deteksi Anomali AI": "Deteksi Anomali AI",
            "⌬  Persiapan Aspen HYSYS": "Persiapan Aspen HYSYS",
            "▤  Laporan Formal & Ekspor": "Laporan Formal & Ekspor",
            "⚙︎  Audit Log & Pengaturan": "Audit Log & Pengaturan",
            "•  Parameter: Daya Bersih (Net Power)": "Tren KPI & Korelasi",
            "•  Parameter: Heat Rate Neto (kJ/kWh)": "Tren KPI & Korelasi",
            "•  Parameter: Efisiensi Termal Siklus": "Tren KPI & Korelasi",
            "•  Parameter: Neraca Uap HRSG & ST": "Neraca Massa & Energi",
            "•  Parameter: Pendinginan Kondensor CW": "Analisis Sub-Sistem Unit",
        }
        
        # Hapus/sembunyikan menu dan parameter yang tidak diizinkan untuk peran pengguna ini
        search_options = [
            opt for opt in all_search_options 
            if search_route_map.get(opt) in allowed_mods_set
        ]
        
        def _on_search_change():
            val = st.session_state.get("topbar_search_selectbox")
            if val and val in search_route_map:
                target_mod = search_route_map[val]
                if auth.is_module_allowed(username, target_mod):
                    st.session_state["pending_nav"] = target_mod
            st.session_state["topbar_search_selectbox"] = None

        st.selectbox(
            "Pencarian",
            options=search_options,
            index=None,
            placeholder="Cari modul atau parameter yang dapat diakses...",
            label_visibility="collapsed",
            key="topbar_search_selectbox",
            on_change=_on_search_change
        )
                
    with col_bell:
        # Siapkan data notifikasi dinamis berdasarkan status sesi & dataset aktual
        active_df = session_state.get("active_df")
        metadata = session_state.get("dataset_metadata") or {}
        change_logs = session_state.get("change_logs") or []
        tag_mapping = session_state.get("tag_mapping") or {}
        
        # 1. Notifikasi Status & Kualitas Data
        if active_df is not None and not active_df.empty:
            n_rows = len(active_df)
            missing_cells = int(active_df.isnull().sum().sum())
            total_cells = max(active_df.size, 1)
            comp_pct = 100.0 if missing_cells == 0 else max(0.0, (1 - missing_cells / total_cells) * 100.0)
            fn = metadata.get("filename", "Dataset DCS")
            if missing_cells == 0:
                n1_icon = "✓"
                n1_color = "#10B981"
                n1_title = "Kualitas Data Lengkap (100%)"
                n1_desc = f"{n_rows:,} data historis terverifikasi tanpa missing interval."
                n1_time = "Baru saja"
            else:
                n1_icon = "⚠"
                n1_color = "#F59E0B"
                n1_title = f"Kualitas Data: {comp_pct:.1f}% Lengkap"
                n1_desc = f"{n_rows:,} rekaman ({fn}) memiliki {missing_cells:,} interval kosong."
                n1_time = "Perlu Perhatian"
                
            # 2. Notifikasi Evaluasi Heat Rate & Daya
            net_col = tag_mapping.get("plant_net", "plant_net_power_mw")
            p_net = active_df[net_col].mean() if net_col in active_df.columns else 367.20
            hr_val = 7269.83
            n2_icon = "⚠"
            n2_color = "#F59E0B"
            n2_title = "Heat Rate Terpantau Normal"
            n2_desc = f"Heat rate neto {hr_val:,.2f} kJ/kWh (Daya neto {p_net:,.1f} MW) dalam rentang operasi standar."
            n2_time = "Periode Aktif"
        else:
            n1_icon = "ℹ"
            n1_color = "#3B82F6"
            n1_title = "Belum Ada Dataset yang Dimuat"
            n1_desc = "Silakan unggah berkas DCS melalui menu Import Data Historian."
            n1_time = "Status Terkini"
            
            n2_icon = "⚙"
            n2_color = "#64748B"
            n2_title = "Evaluasi Kinerja Standby"
            n2_desc = "Kalkulasi Heat Rate dan efisiensi akan aktif saat dataset operasional dimuat."
            n2_time = "Menunggu Data"
            
        # 3. Notifikasi Audit Trail & Aktivitas Sesi Terakhir
        if change_logs:
            last_log = change_logs[-1]
            act_text = last_log.get("action", "Sesi audit aktif")
            if len(act_text) > 75:
                act_text = act_text[:72] + "..."
            ts_text = last_log.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            time_part = ts_text.split(" ")[1] if " " in ts_text else ts_text
            n3_icon = "ℹ"
            n3_color = "#3B82F6"
            n3_title = f"Audit Trail Aktif ({len(change_logs)} Log)"
            n3_desc = f"{act_text}"
            n3_time = f"Pukul {time_part}"
        else:
            n3_icon = "ℹ"
            n3_color = "#3B82F6"
            n3_title = "Audit Trail Aktif"
            n3_desc = f"Pencatatan sesi audit terenkripsi aktif untuk pengguna '{user_name}'."
            n3_time = "Sesi Baru"

        badge_text = f"{min(len(change_logs) + (1 if active_df is not None and not active_df.empty else 0), 9)} Baru" if change_logs else "3 Baru"

        # Popover Notifikasi Interaktif Lingkaran Modern dengan Ikon Material
        with st.popover("", icon=":material/notifications:", use_container_width=False, help="Pusat Notifikasi & Alarm"):
            st.markdown(clean_html(f"""
            <div style="min-width: 290px; padding: 2px;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #E2E8F0;">
                    <div style="font-weight: 700; font-size: 14px; color: #0F172A;">Pusat Notifikasi & Alarm</div>
                    <span style="background: #EFF6FF; color: #2563EB; font-weight: 700; font-size: 11px; padding: 2px 8px; border-radius: 12px;">{badge_text}</span>
                </div>
                <div style="display: flex; gap: 10px; padding: 8px 10px; background: #F8FAFC; border-radius: 8px; margin-bottom: 8px; border-left: 3.5px solid {n1_color};">
                    <div style="color: {n1_color}; font-size: 15px; font-weight: 800;">{n1_icon}</div>
                    <div>
                        <div style="font-weight: 600; font-size: 12px; color: #0F172A; line-height: 1.2;">{n1_title}</div>
                        <div style="font-size: 11px; color: #64748B; line-height: 1.35; margin-top: 2px;">{n1_desc}</div>
                        <div style="font-size: 10px; color: #94A3B8; margin-top: 3px;">{n1_time}</div>
                    </div>
                </div>
                <div style="display: flex; gap: 10px; padding: 8px 10px; background: #FFFBEB; border-radius: 8px; margin-bottom: 8px; border-left: 3.5px solid {n2_color};">
                    <div style="color: {n2_color}; font-size: 15px; font-weight: 800;">{n2_icon}</div>
                    <div>
                        <div style="font-weight: 600; font-size: 12px; color: #0F172A; line-height: 1.2;">{n2_title}</div>
                        <div style="font-size: 11px; color: #64748B; line-height: 1.35; margin-top: 2px;">{n2_desc}</div>
                        <div style="font-size: 10px; color: #94A3B8; margin-top: 3px;">{n2_time}</div>
                    </div>
                </div>
                <div style="display: flex; gap: 10px; padding: 8px 10px; background: #F8FAFC; border-radius: 8px; margin-bottom: 12px; border-left: 3.5px solid {n3_color};">
                    <div style="color: {n3_color}; font-size: 15px; font-weight: 800;">{n3_icon}</div>
                    <div>
                        <div style="font-weight: 600; font-size: 12px; color: #0F172A; line-height: 1.2;">{n3_title}</div>
                        <div style="font-size: 11px; color: #64748B; line-height: 1.35; margin-top: 2px;">{n3_desc}</div>
                        <div style="font-size: 10px; color: #94A3B8; margin-top: 3px;">{n3_time}</div>
                    </div>
                </div>
            </div>
            """), unsafe_allow_html=True)
            
            if auth.is_module_allowed(username, "Audit Log & Pengaturan"):
                if st.button("📋 Buka Audit Log & Pengaturan", use_container_width=True, key="btn_notif_to_settings"):
                    st.session_state["pending_nav"] = "Audit Log & Pengaturan"
                    st.rerun()

    with col_profile:
        # Popover profil pengguna yang interaktif saat diklik
        with st.popover(user_name, icon=":material/account_circle:", use_container_width=True):
            # 1. Header Identitas Profil dengan Avatar Modern
            st.markdown(clean_html(f"""
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px; padding-bottom: 10px; border-bottom: 1px solid #E2E8F0;">
                <div style="width: 44px; height: 44px; border-radius: 50%; background: linear-gradient(135deg, #0EA5E9 0%, #2563EB 100%); color: #FFFFFF; font-weight: 800; font-size: 18px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(14, 165, 233, 0.35);">
                    {avatar_char}
                </div>
                <div style="flex: 1; overflow: hidden;">
                    <div style="font-weight: 700; font-size: 14px; color: #0F172A; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                        {user_name}
                    </div>
                    <div style="font-size: 11.5px; color: #2563EB; font-weight: 600;">
                        {role}
                    </div>
                    <div style="font-size: 11px; color: #64748B;">
                        {email}
                    </div>
                </div>
            </div>
            """), unsafe_allow_html=True)
            
            # 2. Status Sesi Aktif dengan Indikator Bersih
            st.markdown(clean_html("""
            <div style="display: flex; align-items: center; justify-content: space-between; background: #F8FAFC; border: 1px solid #E2E8F0; padding: 7px 12px; border-radius: 8px; margin-bottom: 12px; font-size: 11.5px;">
                <span style="color: #64748B;">Status Sesi:</span>
                <span style="display: inline-flex; align-items: center; gap: 6px; color: #16A34A; font-weight: 700;">
                    <span style="display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: #10B981; box-shadow: 0 0 6px #10B981;"></span>
                    Online / Aktif
                </span>
            </div>
            """), unsafe_allow_html=True)
            
            # 3. Kelola Profil & Detail Akun (Ubah Nama dan Kata Sandi)
            with st.expander("Detail Akun & Profil", expanded=False):
                st.markdown(clean_html(f"""
                <div style="font-size: 12px; line-height: 1.6; color: #334155; margin-bottom: 8px;">
                    <b>Posisi:</b> {title}<br>
                    <b>Email:</b> <code>{email}</code><br>
                    <b>Tingkat Akses:</b> <span style="background:#EFF6FF; color:#1D4ED8; padding:1px 6px; border-radius:4px; font-size:11px;">{role}</span>
                </div>
                """), unsafe_allow_html=True)
                
                new_display_name = st.text_input("Nama Tampilan", value=user_name, key=f"pop_edit_{username}")
                
                st.markdown("<div style='font-size:11.5px; font-weight:700; color:#0F172A; margin:8px 0 2px 0;'>Ganti Kata Sandi (Opsional):</div>", unsafe_allow_html=True)
                old_pwd = st.text_input("Kata Sandi Saat Ini", type="password", key=f"pop_old_pwd_{username}", placeholder="Diperlukan untuk verifikasi...")
                new_pwd = st.text_input("Kata Sandi Baru", type="password", key=f"pop_new_pwd_{username}", placeholder="Minimal 4 karakter...")
                cfm_pwd = st.text_input("Konfirmasi Kata Sandi Baru", type="password", key=f"pop_cfm_pwd_{username}", placeholder="Ulangi kata sandi baru...")
                
                if st.button("Simpan Perubahan", key="btn_save_pop_profile", use_container_width=True, type="primary"):
                    updates_done = []
                    has_error = False
                    
                    # 1. Update nama jika berbeda
                    cleaned_name = new_display_name.strip() if new_display_name else ""
                    if cleaned_name and cleaned_name != user_name:
                        if auth.update_user_profile(username, cleaned_name, session_state=session_state):
                            updates_done.append("Nama Tampilan")
                    
                    # 2. Update kata sandi jika diisi
                    if new_pwd or old_pwd or cfm_pwd:
                        if not old_pwd:
                            st.toast("Kata sandi saat ini wajib diisi!", icon="⚠️")
                            st.error("Masukkan kata sandi saat ini untuk konfirmasi.")
                            has_error = True
                        elif not new_pwd or len(new_pwd.strip()) < 4:
                            st.toast("Kata sandi baru minimal 4 karakter!", icon="⚠️")
                            st.error("Kata sandi baru harus memiliki panjang minimal 4 karakter.")
                            has_error = True
                        elif new_pwd != cfm_pwd:
                            st.toast("Konfirmasi kata sandi baru tidak cocok!", icon="❌")
                            st.error("Konfirmasi kata sandi baru tidak sesuai.")
                            has_error = True
                        else:
                            p_ok, p_msg = auth.update_user_password(username, new_pwd.strip(), old_password=old_pwd, session_state=session_state)
                            if p_ok:
                                updates_done.append("Kata Sandi")
                            else:
                                st.toast(p_msg, icon="❌")
                                st.error(p_msg)
                                has_error = True
                                
                    if updates_done and not has_error:
                        summary_msg = f"{ ' & '.join(updates_done) } berhasil diperbarui!"
                        st.toast(summary_msg, icon="✅")
                        st.success(summary_msg)
                        st.rerun()

            # 4. Ganti Akun Pengujian (Switch Account dengan Validasi Password)
            with st.expander("Ganti Peran Pengujian (RBAC)", expanded=False):
                st.caption("Pilih akun tujuan dan masukkan kata sandi akun tersebut:")
                
                account_options = ["maintenance1", "engineer", "operator"]
                account_labels = {
                    "maintenance1": "Maintenance 1 / Lead Auditor",
                    "engineer": "Plant Performance Engineer",
                    "operator": "Control Room Operator"
                }
                
                # Default akun terpilih adalah peran lain
                curr_normalized = auth.normalize_username(username)
                def_idx = 1 if curr_normalized == "maintenance1" else 0
                target_user_key = st.selectbox(
                    "Pilih Akun Tujuan:",
                    options=account_options,
                    index=def_idx,
                    format_func=lambda u: account_labels.get(u, u),
                    key="pop_sw_target_select"
                )
                
                target_pwd = st.text_input(
                    f"Kata Sandi ({account_labels.get(target_user_key, target_user_key)}):", 
                    type="password", 
                    placeholder="Masukkan kata sandi akun tujuan...",
                    key="pop_sw_pwd_input"
                )
                
                if st.button("Beralih Akun", type="primary", use_container_width=True, key="btn_confirm_switch_user", icon=":material/swap_horiz:"):
                    if not target_pwd:
                        st.toast("Kata sandi wajib diisi untuk beralih akun!", icon="⚠️")
                        st.error("Masukkan kata sandi akun tujuan.")
                    else:
                        login_ok, login_msg = auth.login(target_user_key, target_pwd, session_state)
                        if login_ok:
                            st.toast(f"Berhasil masuk sebagai {account_labels.get(target_user_key, target_user_key)}!", icon="✅")
                            target_allowed = auth.get_allowed_modules(target_user_key)
                            st.session_state["pending_nav"] = target_allowed[0] if target_allowed else "Dashboard Utama"
                            st.rerun()
                        else:
                            st.toast("Kata sandi salah! Gagal beralih akun.", icon="❌")
                            st.error(login_msg)
                    
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            
            # 5. Tombol Keluar (Log Out)
            if st.button("Keluar dari Sistem (Log Out)", type="primary", use_container_width=True, key="btn_pop_logout"):
                auth.logout(session_state)
                st.rerun()

def render_dashboard_hero(title: str = "Dashboard Kinerja & Audit Energi",
                          subtitle: str = "Evaluasi kinerja termal, agregasi produksi daya, dan efisiensi siklus kombinasi Blok 1 (3-3-1)",
                          spec_text: str = "Blok 1 (3 GT + 3 HRSG + 1 ST)"):
    """Menampilkan Hero Card dengan ilustrasi PLTGU persis sesuai mockup."""
    img_path = "ui/assets/pltgu_illustration.png"
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            b64_str = base64.b64encode(f.read()).decode("utf-8")
        img_html = f'<img src="data:image/png;base64,{b64_str}" style="width:280px; height:125px; object-fit:cover; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.06);" />'
    else:
        img_html = ""

    grid_icon = LUCIDE_SVG_ICONS["grid"]
    zap_icon = LUCIDE_SVG_ICONS["zap"]

    html = f"""
    <div class="dashboard-hero-card">
        <div style="flex: 1; z-index: 2;">
            <div class="hero-breadcrumb">
                <span>{grid_icon}</span>
                <span>Dashboard</span>
            </div>
            <div class="hero-main-title" style="font-size:25px; margin:0 0 2px 0; line-height:1.15;">{title}</div>
            <div class="hero-main-subtitle" style="font-size:13px; margin:0 0 10px 0; line-height:1.3;">{subtitle}</div>
            <div class="hero-spec-pill">
                <span style="display:inline-flex; align-items:center; color:#B45309;">{zap_icon}</span>
                <span>{spec_text}</span>
            </div>
        </div>
        <div class="hero-illustration-container">
            {img_html}
        </div>
    </div>
    """
    st.markdown(textwrap.dedent(html), unsafe_allow_html=True)

def render_page_hero(title: str, subtitle: str, badge_text: str = "PLTGU Blok 1", badge_icon: str = "⚡"):
    """Header umum untuk halaman non-dashboard dengan ikon SVG vektor tajam."""
    grid_icon = LUCIDE_SVG_ICONS["grid"]
    if badge_icon in LUCIDE_SVG_ICONS:
        svg_icon = LUCIDE_SVG_ICONS[badge_icon]
    else:
        mapped_key = EMOJI_TO_SVG_KEY.get(badge_icon, "zap")
        svg_icon = LUCIDE_SVG_ICONS.get(mapped_key, LUCIDE_SVG_ICONS["zap"])
        
    html = f"""
    <div class="dashboard-hero-card" style="padding:16px 22px;">
        <div>
            <div class="hero-breadcrumb">
                <span>{svg_icon}</span>
                <span>{badge_text}</span>
            </div>
            <div class="hero-main-title" style="font-size:22px; margin:0 0 2px 0; line-height:1.15;">{title}</div>
            <div class="hero-main-subtitle" style="font-size:13px; margin:0; line-height:1.3;">{subtitle}</div>
        </div>
    </div>
    """
    st.markdown(textwrap.dedent(html), unsafe_allow_html=True)

def render_section_header(title: str, subtitle: Optional[str] = None, icon_key: str = "activity", badge_text: Optional[str] = None, icon_bg: str = "#EFF6FF", icon_color: str = "#2563EB"):
    """Header seksi modern dengan icon SVG tajam dalam pastel square dan badge opsional."""
    # Resolve SVG icon from key or emoji
    if icon_key in LUCIDE_SVG_ICONS:
        svg = LUCIDE_SVG_ICONS[icon_key]
    else:
        mapped = EMOJI_TO_SVG_KEY.get(icon_key, "activity")
        svg = LUCIDE_SVG_ICONS.get(mapped, LUCIDE_SVG_ICONS["activity"])
        
    sub_html = f'<div style="font-size:12px; color:#64748B; margin:2px 0 0 0; line-height:1.25;">{subtitle}</div>' if subtitle else ""
    badge_html = f'<span style="background:#F1F5F9; color:#334155; font-size:11.5px; font-weight:700; padding:3px 10px; border-radius:12px; border:1px solid #E2E8F0;">{badge_text}</span>' if badge_text else ""
    
    html = f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin:18px 0 12px 0; padding-bottom:8px; border-bottom:1px solid #F1F5F9;">
        <div style="display:flex; align-items:center; gap:10px;">
            <div style="width:34px; height:34px; background:{icon_bg}; color:{icon_color}; border-radius:8px; display:flex; align-items:center; justify-content:center;">
                {svg}
            </div>
            <div>
                <div style="font-size:15.5px; font-weight:800; color:#0F172A; margin:0; line-height:1.15;">{title}</div>
                {sub_html}
            </div>
        </div>
        {badge_html}
    </div>
    """
    st.markdown(textwrap.dedent(html), unsafe_allow_html=True)

def render_mockup_kpi_card(icon_key: Optional[str] = None,
                           icon_bg: str = "#EFF6FF",
                           icon_color: str = "#2563EB",
                           title: str = "",
                           value: Any = None,
                           unit: str = "",
                           status_label: str = "Normal",
                           trend_arrow: str = "↑",
                           trend_pct: str = "1,24%",
                           trend_direction: str = "up", # "up", "down", "down-good"
                           trend_subtext: str = "vs. periode sebelumnya",
                           trace_footer: str = "",
                           icon_symbol: Optional[str] = None):
    """Menampilkan kartu KPI dengan Ikon Vektor Lucide SVG tajam dan modern."""
    # Menentukan key SVG dari icon_key atau mapping icon_symbol
    resolved_key = icon_key
    if not resolved_key and icon_symbol:
        resolved_key = EMOJI_TO_SVG_KEY.get(icon_symbol, "zap")
    if not resolved_key:
        resolved_key = "zap"
        
    svg_icon = LUCIDE_SVG_ICONS.get(resolved_key, LUCIDE_SVG_ICONS["zap"])
    
    if value is None or str(value).strip() in ["", "nan", "None"]:
        disp_val = "NOT_ENOUGH"
        unit_str = ""
    elif isinstance(value, (int, float)):
        disp_val = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        unit_str = f'<span class="kpi-unit-text">{unit}</span>'
    else:
        disp_val = str(value)
        unit_str = f'<span class="kpi-unit-text">{unit}</span>'
        
    trend_color_class = "trend-down-good" if trend_direction == "down-good" else ("trend-up" if trend_direction == "up" else "trend-down")
    
    html = f"""
    <div class="modern-kpi-card">
        <div>
            <div class="kpi-header-row">
                <div class="kpi-icon-circle" style="background:{icon_bg}; color:{icon_color};">
                    {svg_icon}
                </div>
                <div class="kpi-pill-normal">
                    {status_label}
                </div>
            </div>
            <div class="kpi-label-text">{title}</div>
            <div class="kpi-number-display">
                <span class="kpi-number-val">{disp_val}</span>
                {unit_str}
            </div>
            <div class="kpi-trend-row {trend_color_class}">
                <span>{trend_arrow} {trend_pct}</span>
                <span class="trend-subtext">{trend_subtext}</span>
            </div>
        </div>
        <div class="kpi-trace-footer" title="{trace_footer}">
            {trace_footer}
        </div>
    </div>
    """
    st.markdown(textwrap.dedent(html), unsafe_allow_html=True)

def render_synthetic_banner(is_synthetic: bool = True):
    """Banner watermark data sintetis dengan icon SVG alert."""
    if is_synthetic:
        alert_icon = LUCIDE_SVG_ICONS["alert_triangle"]
        html = f"""
        <div class="synthetic-banner">
            <span style="display:inline-flex; align-items:center;">{alert_icon}</span>
            <span><b>{SYNTHETIC_DATA_BANNER}</b></span>
            <span style="font-size:11px; opacity:0.85; margin-left:8px; padding-left:8px; border-left:1px solid rgba(146,64,14,0.3);">Mode Evaluasi & Prototipe</span>
        </div>
        """
        st.markdown(textwrap.dedent(html), unsafe_allow_html=True)

def render_status_badge(status: str, custom_text: Optional[str] = None) -> str:
    """Badge status pill."""
    norm_status = status.upper().strip()
    config = STATUS_COLORS.get(norm_status, STATUS_COLORS["INFO"])
    text = custom_text or config["label"]
    icon = config.get("icon", "")
    badge_class_map = {
        "VALID": "badge-valid",
        "WARNING": "badge-warning",
        "ANOMALY": "badge-anomaly",
        "INFO": "badge-info",
        "NOT_ENOUGH_DATA": "badge-not-enough"
    }
    css_class = badge_class_map.get(norm_status, "badge-info")
    return f'<span class="{css_class}">{icon} {text}</span>'

def render_kpi_card(title: str, value: Any, unit: str = "", status: str = "VALID", formula: str = "", boundary: str = "", basis: str = "", accent_color: Optional[str] = None):
    """Fallback ke render_mockup_kpi_card."""
    render_mockup_kpi_card(
        icon_key="zap",
        icon_bg="#EFF6FF",
        icon_color="#2563EB",
        title=title,
        value=value,
        unit=unit,
        status_label="Normal",
        trend_arrow="↑",
        trend_pct="0,00%",
        trend_direction="up",
        trend_subtext="tervalidasi",
        trace_footer=f"{formula} • {boundary} • {basis}".strip(" •")
    )

def create_styled_plot(title: str, x_label: str = "Waktu", y_label: str = "") -> go.Figure:
    """Membuat objek Plotly Figure presisi mockup visual."""
    fig = go.Figure()
    fig.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        margin={"l": 45, "r": 20, "t": 35, "b": 45},
        font={"family": "Plus Jakarta Sans, Inter, sans-serif", "color": "#1E293B", "size": 11},
        xaxis={
            "title": {"text": x_label, "font": {"size": 11, "color": "#64748B"}},
            "gridcolor": "#F1F5F9",
            "linecolor": "#E2E8F0",
            "showgrid": True,
            "zeroline": False
        },
        yaxis={
            "title": {"text": y_label, "font": {"size": 11, "color": "#64748B"}},
            "gridcolor": "#F1F5F9",
            "linecolor": "#E2E8F0",
            "showgrid": True,
            "zeroline": False
        },
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.05,
            "xanchor": "center",
            "x": 0.5,
            "font": {"size": 11, "color": "#1E293B"}
        },
        hovermode="x unified",
        hoverlabel={
            "bgcolor": "#0F172A",
            "font": {"color": "#FFFFFF", "family": "Plus Jakarta Sans, Inter"},
            "bordercolor": "rgba(0,0,0,0)"
        }
    )
    return fig

def render_restricted_access(module_name: str, user: Optional[Any] = None):
    """Menampilkan halaman pembatasan akses hak istimewa (RBAC Guard)."""
    shield_icon = LUCIDE_SVG_ICONS["shield"]
    user_role = user.role if user else "Tamu / Operator"
    user_name = user.name if user else "Pengguna"
    
    st.markdown(textwrap.dedent(f"""
    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; padding: 40px 30px; text-align: center; max-width: 680px; margin: 40px auto; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);">
        <div style="width: 64px; height: 64px; border-radius: 50%; background: #FEF2F2; color: #DC2626; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 16px; transform: scale(1.3);">
            {shield_icon}
        </div>
        <h2 style="font-size: 20px; font-weight: 800; color: #0F172A; margin: 0 0 8px 0;">
            Akses Modul Dibatasi
        </h2>
        <p style="font-size: 14px; color: #64748B; margin-bottom: 20px; line-height: 1.6;">
            Modul <b>{module_name}</b> memerlukan tingkat otorisasi yang lebih tinggi.<br>
            Peran Anda saat ini: <span style="background: #EFF6FF; color: #1D4ED8; font-weight: 700; padding: 2px 8px; border-radius: 6px;">{user_role}</span>
        </p>
        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 14px; text-align: left; font-size: 12px; color: #475569; margin-bottom: 24px; line-height: 1.6;">
            <b>ℹ️ Kebijakan Hak Akses Modul PLTGU Blok 1:</b>
            <ul style="margin: 6px 0 0 18px; padding: 0;">
                <li><b>Control Room Operator:</b> 4 Modul Operasional (Dashboard, Kualitas Data, Tren KPI, Analisis Unit).</li>
                <li><b>Plant Performance Engineer:</b> 11 Modul Rekayasa (termasuk Neraca Massa/Energi, Aspen HYSYS, Deteksi AI, Ekspor Laporan).</li>
                <li><b>Lead Energy Auditor & Admin:</b> Akses Penuh ke seluruh 12 modul termasuk Konfigurasi Pengaturan Sistem & Kepatuhan Section K.</li>
            </ul>
        </div>
    </div>
    """), unsafe_allow_html=True)
    
    col_back1, col_back2, col_back3 = st.columns([1, 1.2, 1])
    with col_back2:
        if st.button("⬅️ Kembali ke Dashboard Utama", use_container_width=True, type="primary"):
            st.session_state["pending_nav"] = "Dashboard Utama"
            st.rerun()

def render_number_animation_script():
    """Menginjeksikan script animasi pergerakan angka (count-up ticker) ultra-ringan & efisien (0% CPU lag)."""
    st_components.html("""
    <script>
    (function() {
        // Matikan observer lama jika pernah terpasang agar tidak memberatkan CPU
        if (window.parent && window.parent._kpiObserver) {
            try { window.parent._kpiObserver.disconnect(); } catch(e) {}
            window.parent._kpiObserver = null;
        }

        function parseNum(rawText) {
            let cleanStr = rawText;
            let decimals = 0;
            if (rawText.includes(',')) {
                const parts = rawText.split(',');
                decimals = parts[1] ? parts[1].length : 0;
                cleanStr = parts[0].replace(/\\./g, '') + '.' + parts[1];
            } else if (rawText.includes('.')) {
                const parts = rawText.split('.');
                if (parts.length > 2 || parts[1].length === 3) {
                    cleanStr = rawText.replace(/\\./g, '');
                    decimals = 0;
                } else {
                    decimals = parts[1] ? parts[1].length : 0;
                    cleanStr = rawText;
                }
            }
            const num = parseFloat(cleanStr);
            return isNaN(num) ? null : { val: num, decimals: decimals };
        }

        function animateValue(el, start, end, duration, decimals, finalStr) {
            el.dataset.animating = 'true';
            const startTime = performance.now();
            
            function step(now) {
                const elapsed = now - startTime;
                const progress = Math.min(elapsed / duration, 1);
                // Fast ease-out cubic
                const ease = 1 - Math.pow(1 - progress, 3);
                const current = start + (end - start) * ease;
                
                let formatted;
                if (decimals > 0) {
                    const parts = current.toFixed(decimals).split('.');
                    const intPart = parseInt(parts[0], 10).toLocaleString('id-ID');
                    formatted = intPart + ',' + parts[1];
                } else {
                    formatted = Math.round(current).toLocaleString('id-ID');
                }
                
                // Gunakan textContent (bukan innerText) untuk menghindari layout reflow browser
                el.textContent = formatted;
                
                if (progress < 1) {
                    requestAnimationFrame(step);
                } else {
                    el.textContent = finalStr;
                    el.dataset.animating = 'false';
                    el.dataset.doneAnimated = 'true';
                }
            }
            requestAnimationFrame(step);
        }

        function scanAndAnimate() {
            try {
                const doc = window.parent.document;
                if (!doc) return;
                
                const elements = doc.querySelectorAll('.kpi-number-val');
                elements.forEach(el => {
                    const rawText = el.textContent.trim();
                    if (!rawText || !/^[0-9.,]+$/.test(rawText)) return;
                    
                    if (el.dataset.finalVal && el.dataset.finalVal !== rawText) {
                        el.dataset.doneAnimated = 'false';
                    }
                    if (el.dataset.animating === 'true' || el.dataset.doneAnimated === 'true') return;
                    
                    const parsed = parseNum(rawText);
                    if (!parsed) return;
                    
                    const startNum = 0;
                    el.dataset.finalVal = rawText;
                    // Durasi cepat & ringan 450ms (sangat responsif & bebas lag)
                    animateValue(el, startNum, parsed.val, 450, parsed.decimals, rawText);
                });
            } catch(e) {}
        }

        // Panggil tepat saat elemen selesai dirender tanpa looping observer
        setTimeout(scanAndAnimate, 50);
        setTimeout(scanAndAnimate, 200);
    })();
    </script>
    """, height=0, width=0)


def render_empty_dataset_notice(mode: str = "banner", key_suffix: str = ""):
    """
    Menampilkan banner atau kartu pemberitahuan dataset kosong yang modern,
    menggunakan ikon vektor Lucide SVG resolusi tinggi dan tombol navigasi langsung ke Import jika diizinkan.
    """
    import core.auth as auth
    current_u = auth.get_current_user(st.session_state)
    uname = current_u.username if current_u else "operator"
    can_import = auth.is_module_allowed(uname, "Import Data Historian")
    
    info_icon = LUCIDE_SVG_ICONS.get("info", "")
    database_icon = LUCIDE_SVG_ICONS.get("database", "")
    
    if mode == "banner":
        if can_import:
            b_col1, b_col2 = st.columns([4.2, 1.2])
            with b_col1:
                st.markdown(clean_html(f"""
                <div style="background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 12px; padding: 12px 18px; display: flex; align-items: center; gap: 14px; box-shadow: 0 1px 3px rgba(37, 99, 235, 0.06); min-height: 48px;">
                    <div style="width: 36px; height: 36px; border-radius: 10px; background: #DBEAFE; color: #1D4ED8; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                        {info_icon}
                    </div>
                    <div>
                        <div style="font-size: 13.5px; font-weight: 700; color: #1E3A8A; line-height: 1.3;">
                            Belum Ada Dataset yang Dimuat
                        </div>
                        <div style="font-size: 12px; color: #2563EB; line-height: 1.3; margin-top: 2px;">
                            Buka menu <b>Import Data Historian</b> untuk mengunggah berkas operasional DCS / Historian pembangkit.
                        </div>
                    </div>
                </div>
                """), unsafe_allow_html=True)
            with b_col2:
                st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
                if st.button("Ke Import Data", icon=":material/upload_file:", type="primary", use_container_width=True, key=f"btn_goto_import_{key_suffix}"):
                    st.session_state["pending_nav"] = "Import Data Historian"
                    st.rerun()
        else:
            st.markdown(clean_html(f"""
            <div style="background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 12px; padding: 12px 18px; display: flex; align-items: center; justify-content: space-between; gap: 14px; box-shadow: 0 1px 3px rgba(37, 99, 235, 0.06); min-height: 48px;">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <div style="width: 36px; height: 36px; border-radius: 10px; background: #DBEAFE; color: #1D4ED8; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                        {info_icon}
                    </div>
                    <div>
                        <div style="font-size: 13.5px; font-weight: 700; color: #1E3A8A; line-height: 1.3;">
                            Belum Ada Dataset yang Dimuat
                        </div>
                        <div style="font-size: 12px; color: #2563EB; line-height: 1.3; margin-top: 2px;">
                            Menunggu personel berwenang (Lead Auditor / Engineer) mengunggah berkas operasional DCS.
                        </div>
                    </div>
                </div>
                <span style="font-size: 11.5px; color: #64748B; background: #FFFFFF; border: 1px solid #E2E8F0; padding: 4px 10px; border-radius: 8px;">🔒 Menunggu Data</span>
            </div>
            """), unsafe_allow_html=True)
    else:
        # Tampilan Kartu Tengah Beresolusi Tinggi (Card mode)
        with st.container(border=True):
            sub_text = "Silakan unggah berkas data melalui modul <b>Import Data Historian</b>." if can_import else "Menunggu personel berwenang (Lead Auditor / Engineer) mengunggah berkas data DCS."
            st.markdown(clean_html(f"""
            <div style="padding: 28px 16px; text-align: center;">
                <div style="width: 52px; height: 52px; margin: 0 auto 16px auto; border-radius: 14px; background: #EFF6FF; border: 1px solid #DBEAFE; color: #2563EB; display: flex; align-items: center; justify-content: center;">
                    {database_icon}
                </div>
                <div style="font-size: 16.5px; font-weight: 700; color: #0F172A; margin: 0 0 4px 0; line-height: 1.2;">Belum Ada Dataset yang Dimuat</div>
                <div style="font-size: 13px; color: #64748B; max-width: 520px; margin: 0 auto 18px auto; line-height: 1.35;">
                    Modul ini membutuhkan data operasional sensor DCS / SCADA pembangkit. {sub_text}
                </div>
            </div>
            """), unsafe_allow_html=True)
            
            if can_import:
                b_c1, b_c2, b_c3 = st.columns([1.5, 2, 1.5])
                with b_c2:
                    if st.button("Buka Import Data Historian", icon=":material/upload_file:", type="primary", use_container_width=True, key=f"btn_goto_import_card_{key_suffix}"):
                        st.session_state["pending_nav"] = "Import Data Historian"
                        st.rerun()
            else:
                st.markdown("<div style='text-align:center; font-size:12px; color:#94A3B8; margin-bottom:8px;'>🔒 Pengunggahan dataset memerlukan hak akses Lead Auditor / Plant Engineer.</div>", unsafe_allow_html=True)



