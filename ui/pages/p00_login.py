"""
Halaman 0: Portal Login & Autentikasi Pengguna
Sistem Audit Energi & Kinerja PLTGU Blok 1
Sesuai Mockup Visual Presisi Industrial Modern - Pas Layar (No-Scroll Viewport)
"""

import streamlit as st
from core.auth import login
from ui.components import LUCIDE_SVG_ICONS

def render(session_state):
    """Merender halaman login dengan ukuran kartu proporsional dan pas di layar tanpa perlu scroll."""
    zap_icon = LUCIDE_SVG_ICONS["zap"]
    shield_icon = LUCIDE_SVG_ICONS["shield"]
    user_icon = LUCIDE_SVG_ICONS["user"]
    
    # CSS terfokus agar halaman login pas satu layar (Zero-Scroll) dan berada di posisi atas yang proporsional
    st.markdown("""
    <style>
    /* Hilangkan total spasi header bawaan Streamlit khusus halaman login */
    header[data-testid="stHeader"] {
        display: none !important;
        height: 0px !important;
        min-height: 0px !important;
        visibility: hidden !important;
    }
    
    /* Naikkan container utama ke bagian atas layar */
    .block-container {
        padding-top: 0rem !important;
        margin-top: -28px !important;
        padding-bottom: 0.8rem !important;
        max-width: 95% !important;
    }
    
    /* Reset jarak per kalimat agar rapat dan rapi */
    .block-container p, .block-container h1, .block-container h2, .block-container h3 {
        margin-top: 0 !important;
        margin-bottom: 2px !important;
        line-height: 1.2 !important;
    }
    
    /* Styling kartu formulir putih tetap lega dan modern */
    [data-testid="stForm"] {
        padding: 16px 26px !important;
        border-radius: 16px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 10px 30px -4px rgba(15, 23, 42, 0.08) !important;
        background: #FFFFFF !important;
        margin-top: 0 !important;
    }
    
    [data-testid="stForm"] div[data-testid="stTextInput"] {
        margin-bottom: -3px !important;
    }
    
    /* Tombol login tetap tebal dan jelas */
    [data-testid="stFormSubmitButton"] button {
        height: 44px !important;
        font-size: 14.5px !important;
        font-weight: 700 !important;
        border-radius: 9px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Aksen Tiga Garis Miring (///) di Pojok Kanan Atas
    st.markdown("""
    <div style="display: flex; justify-content: flex-end; padding: 0 8px 0 0; margin-bottom: -16px; margin-top: -14px;">
        <div style="display: flex; gap: 5px; opacity: 0.95;">
            <div style="width: 5px; height: 16px; background: #93C5FD; transform: skewX(-24deg); border-radius: 2px;"></div>
            <div style="width: 5px; height: 16px; background: #3B82F6; transform: skewX(-24deg); border-radius: 2px;"></div>
            <div style="width: 5px; height: 16px; background: #1D4ED8; transform: skewX(-24deg); border-radius: 2px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Grid Kolom Tengah Proporsional (Tetap Lebar & Lega Sesuai Ukuran Awal)
    col_l, col_center, col_r = st.columns([1, 2.4, 1])
    
    with col_center:
        # Header Brand Hero: Horizontal Layout (Ikon + Judul Sejajar agar Efisien Tinggi tapi Tetap Besar)
        st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: center; gap: 14px; margin-top: -10px; margin-bottom: 4px;">
            <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #0EA5E9 0%, #2563EB 100%); border-radius: 14px; box-shadow: 0 6px 18px rgba(14, 165, 233, 0.35); color: #FFFFFF; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                <div style="transform: scale(1.3); display: flex;">
                    {zap_icon}
                </div>
            </div>
            <div style="text-align: left;">
                <div style="font-size: 25px; font-weight: 800; color: #0F172A; margin: 0; padding: 0; line-height: 1.08; letter-spacing: -0.02em;">
                    PLTGU BLOK 1
                </div>
                <div style="font-size: 13px; font-weight: 600; color: #1E3A8A; margin: 2px 0 0 0; padding: 0; line-height: 1.15;">
                    Sistem Audit Energi & Evaluasi Kinerja Termal
                </div>
            </div>
        </div>
        <div style="text-align: center; margin-bottom: 8px;">
            <span style="display: inline-flex; align-items: center; gap: 6px; background: #F1F6FD; border: 1px solid #D0E1FD; padding: 3px 12px; border-radius: 20px; font-size: 11px; color: #1E40AF; font-weight: 600;">
                <span style="display: flex; color: #2563EB;">{shield_icon}</span>
                <span>Area Akses Terbatas • Personel Berwenang</span>
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        # Kartu Form Login Utama
        with st.form("login_form", clear_on_submit=False):
            # Banner Header di dalam Kartu Form (Tetap Lega, Jarak Perkalimat Rapat)
            st.markdown(f"""
            <div style="background: #F0F6FE; border: 1px solid #DBEAFE; border-radius: 12px; padding: 9px 13px; margin-bottom: 10px; display: flex; align-items: center; gap: 12px;">
                <div style="width: 36px; height: 36px; border-radius: 50%; background: #E0EDFD; display: flex; align-items: center; justify-content: center; color: #2563EB; flex-shrink: 0;">
                    {user_icon}
                </div>
                <div>
                    <div style="font-size: 14.5px; font-weight: 700; color: #0F172A; margin: 0; padding: 0; line-height: 1.15;">Masuk ke Portal Audit</div>
                    <div style="font-size: 11.5px; color: #64748B; margin: 2px 0 0 0; padding: 0; line-height: 1.25;">Gunakan kredensial akun terdaftar untuk mengakses seluruh modul analitik.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            username_input = st.text_input(
                "Nama Pengguna (Username)",
                placeholder="Masukkan username (contoh: maintenance 1)",
                key="login_username"
            )
            password_input = st.text_input(
                "Kata Sandi (Password)",
                type="password",
                placeholder="Masukkan kata sandi",
                key="login_password"
            )
            
            remember = st.checkbox("Ingat sesi saya", value=True)
            
            st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
            
            submitted = st.form_submit_button(
                "⚡ Masuk ke Sistem →",
                use_container_width=True,
                type="primary"
            )
            
            if submitted:
                if not username_input or not password_input:
                    st.error("Mohon isi Nama Pengguna dan Kata Sandi.", icon=":material/warning:")
                else:
                    success, message = login(username_input, password_input, session_state)
                    if success:
                        st.success(message, icon=":material/check_circle:")
                        st.rerun()
                    else:
                        st.error(message, icon=":material/error:")

        # Footer Kepatuhan & Keamanan Sesuai Mockup
        st.markdown("""
        <div style="text-align: center; margin-top: 14px; padding-top: 10px; border-top: 1px solid #E2E8F0; color: #64748B; font-size: 11.5px; line-height: 1.5;">
            PLTGU Blok 1 (3-3-1) Energy Audit System - Standar IAPWS-IF97 & ISO 50001<br>
            <span style="color: #94A3B8;">Dilengkapi Audit Trail Terenkripsi & Versioned Dataset</span>
        </div>
        """, unsafe_allow_html=True)
