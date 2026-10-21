"""
Unit tests untuk modul autentikasi (core.auth)
Menguji hashing, verifikasi password, manajemen sesi, dan audit log login/logout.
"""

import pytest
from core.auth import (
    hash_password,
    authenticate,
    login,
    logout,
    quick_login,
    is_authenticated,
    get_current_user,
    DEFAULT_USERS
)

def test_hash_password():
    h1 = hash_password("secret123")
    h2 = hash_password("secret123")
    h3 = hash_password("different")
    assert isinstance(h1, str)
    assert len(h1) == 64
    assert h1 == h2
    assert h1 != h3

def test_authenticate_success():
    # Maintenance 1 / Lead Auditor (dapat diakses via 'maintenance 1', 'maintenance1', 'auditor', atau legacy 'rafli')
    user_maint = authenticate("maintenance 1", "pltgu2026")
    assert user_maint is not None
    assert user_maint.username == "maintenance 1"
    assert "Lead Auditor" in user_maint.role
    assert "admin" in user_maint.permissions

    user_alias = authenticate("maintenance1", "pltgu2026")
    assert user_alias is not None
    assert user_alias.username == "maintenance 1"

    user_legacy = authenticate("rafli", "pltgu2026")
    assert user_legacy is not None
    assert user_legacy.username == "maintenance 1"

    # Engineer
    user_eng = authenticate("engineer", "engineer123")
    assert user_eng is not None
    assert user_eng.username == "engineer"
    assert "Engineer" in user_eng.role

    # Operator
    user_op = authenticate("operator", "operator123")
    assert user_op is not None
    assert user_op.username == "operator"

def test_authenticate_case_insensitive():
    user = authenticate("  MaInTeNaNce 1  ", "pltgu2026")
    assert user is not None
    assert user.username == "maintenance 1"

def test_authenticate_invalid():
    # Password salah
    assert authenticate("maintenance 1", "wrong_pass") is None
    # User tidak ditemukan
    assert authenticate("unknown_user", "pass") is None
    # Kredensial kosong
    assert authenticate("", "") is None
    assert authenticate("maintenance 1", "") is None

def test_login_and_logout_flow():
    mock_session = {
        "active_version": "v1_raw (TEST)",
        "change_logs": []
    }
    
    # Kondisi awal
    assert not is_authenticated(mock_session)
    assert get_current_user(mock_session) is None
    
    # Login gagal
    success, msg = login("maintenance 1", "wrong_pass", mock_session)
    assert not success
    assert not is_authenticated(mock_session)
    
    # Login berhasil
    success, msg = login("maintenance 1", "pltgu2026", mock_session)
    assert success
    assert is_authenticated(mock_session)
    curr = get_current_user(mock_session)
    assert curr is not None
    assert curr.username == "maintenance 1"
    
    # Periksa catatan audit trail
    assert len(mock_session["change_logs"]) > 0
    assert "Autentikasi Berhasil" in mock_session["change_logs"][-1]["action"]
    
    # Logout
    logout(mock_session)
    assert not is_authenticated(mock_session)
    assert get_current_user(mock_session) is None
    assert "berhasil keluar (logout)" in mock_session["change_logs"][-1]["action"]

def test_quick_login():
    mock_session = {"change_logs": []}
    success, msg = quick_login("engineer", mock_session)
    assert success
    assert is_authenticated(mock_session)
    curr = get_current_user(mock_session)
    assert curr is not None
    assert curr.username == "engineer"
    
    # Akun tidak valid
    success, msg = quick_login("non_existent", mock_session)
    assert not success

def test_rbac_module_permissions():
    from core.auth import get_allowed_modules, is_module_allowed, ALL_MODULES
    
    # 1. Operator: Hanya 4 modul operasional
    op_modules = get_allowed_modules("operator")
    assert len(op_modules) == 4
    assert is_module_allowed("operator", "Dashboard Utama")
    assert is_module_allowed("operator", "Validasi Kualitas Data")
    assert not is_module_allowed("operator", "Pembersihan Terkendali")
    assert not is_module_allowed("operator", "Audit Log & Pengaturan")
    
    # 2. Engineer: 11 modul rekayasa
    eng_modules = get_allowed_modules("engineer")
    assert len(eng_modules) == 11
    assert is_module_allowed("engineer", "Pembersihan Terkendali")
    assert is_module_allowed("engineer", "Neraca Massa & Energi")
    assert not is_module_allowed("engineer", "Audit Log & Pengaturan")
    
    # 3. Lead Auditor / Admin: Seluruh 12 modul
    admin_modules = get_allowed_modules("maintenance 1")
    assert len(admin_modules) == 12
    assert is_module_allowed("maintenance 1", "Audit Log & Pengaturan")
    assert is_module_allowed("maintenance 1", "Dashboard Utama")
    assert len(get_allowed_modules("maintenance1")) == 12
    assert len(get_allowed_modules("rafli")) == 12

def test_update_user_profile():
    from core.auth import update_user_profile, authenticate
    
    mock_session = {
        "active_version": "v1_raw",
        "change_logs": [],
        "auth_user": {"username": "maintenance 1", "name": "Maintenance 1 / Lead Auditor", "avatar": "M"}
    }
    
    # Update nama
    ok = update_user_profile("maintenance 1", "Auditor Eksternal", session_state=mock_session)
    assert ok is True
    assert mock_session["auth_user"]["name"] == "Auditor Eksternal"
    assert mock_session["auth_user"]["avatar"] == "A"
    
    # Cek login ulang mengambil nama yang sudah diperbarui
    re_auth = authenticate("maintenance 1", "pltgu2026")
    assert re_auth is not None
    assert re_auth.name == "Auditor Eksternal"
    
    # Kembalikan ke nama default untuk konsistensi tes
    update_user_profile("maintenance 1", "Maintenance 1 / Lead Auditor", session_state=mock_session)

def test_session_token_persistence():
    from core.auth import create_session_token, verify_session_token
    
    # Buat token untuk maintenance 1
    token = create_session_token("maintenance 1")
    assert token is not None
    assert token.startswith("maintenance 1.")
    
    # Verifikasi token valid
    user = verify_session_token(token)
    assert user is not None
    assert user.username == "maintenance 1"
    assert "Lead Auditor" in user.role
    
    # Token palsu / rusak ditolak
    assert verify_session_token("invalid_token") is None
    assert verify_session_token("maintenance 1.12345.wrong_signature") is None
    assert verify_session_token("") is None


def test_update_user_password():
    from core.auth import update_user_password
    
    mock_session = {"change_logs": []}
    
    # 1. Password lama salah
    ok, msg = update_user_password("operator", "newpass123", old_password="wrongpassword", session_state=mock_session)
    assert not ok
    assert "tidak cocok" in msg
    
    # 2. Password baru terlalu pendek (< 4 char)
    ok, msg = update_user_password("operator", "12", old_password="operator123", session_state=mock_session)
    assert not ok
    assert "minimal 4" in msg
    
    # 3. Sukses ganti password
    ok, msg = update_user_password("operator", "newpass123", old_password="operator123", session_state=mock_session)
    assert ok
    assert "berhasil" in msg
    
    # Verifikasi login pakai password baru
    user = authenticate("operator", "newpass123")
    assert user is not None
    assert user.username == "operator"
    
    # Verifikasi login pakai password lama gagal
    assert authenticate("operator", "operator123") is None
    
    # Kembalikan ke password semula
    ok, msg = update_user_password("operator", "operator123", old_password="newpass123", session_state=mock_session)
    assert ok
    assert authenticate("operator", "operator123") is not None



