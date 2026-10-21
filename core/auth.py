"""
Modul Autentikasi dan Manajemen Pengguna (Core Authentication & RBAC)
Sistem Audit Energi dan Kinerja PLTGU Blok 1

Menyediakan:
- Verifikasi kredensial terenkripsi (SHA-256 + Salt)
- Manajemen sesi login (Streamlit Session State)
- Role-Based Access Control (Lead Auditor, Performance Engineer, Operator)
- Integrasi riwayat audit log (Audit Trail Section K)
"""

import os
import json
import hashlib
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Tuple, List

# Salt sistem untuk pengamanan digest kata sandi
AUTH_SALT = "PLTGU_BLOK1_SECURE_SALT_2026"

@dataclass
class User:
    username: str
    name: str
    role: str
    title: str
    email: str
    avatar: str
    permissions: List[str]

    def to_dict(self) -> Dict:
        return asdict(self)

def hash_password(password: str, salt: str = AUTH_SALT) -> str:
    """Menghasilkan hash SHA-256 kata sandi yang disalting."""
    payload = f"{salt}:{password}:{salt}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()

def normalize_username(username: str) -> str:
    """Normalisasi alias username ke primary key akun di database."""
    if not username:
        return ""
    c = str(username).strip().lower()
    c_clean = c.replace(" ", "").replace("_", "")
    if c_clean in ["maintenance1", "auditor", "admin", "rafli"] or c in ["maintenance 1", "maintenance_1"]:
        return "maintenance1"
    return c_clean

# Daftar Pengguna Bawaan (Default Seed Accounts)
DEFAULT_USERS = {
    "maintenance1": {
        "username": "maintenance 1",
        "name": "Maintenance 1 / Lead Auditor",
        "role": "Maintenance 1 / Lead Auditor",
        "title": "Lead Energy Auditor & Thermal Performance Specialist",
        "email": "maintenance1@pltgu-blok1.co.id",
        "avatar": "M",
        "password_hash": hash_password("pltgu2026"),
        "permissions": ["all", "admin", "config", "export", "edit_mappings", "ai_run"]
    },
    "engineer": {
        "username": "engineer",
        "name": "Performance Engineer",
        "role": "Plant Performance Engineer",
        "title": "Senior Thermal Performance Engineer",
        "email": "engineer@pltgu-blok1.co.id",
        "avatar": "P",
        "password_hash": hash_password("engineer123"),
        "permissions": ["view", "calc", "hysys", "ai_run", "clean"]
    },
    "operator": {
        "username": "operator",
        "name": "Operator DCS",
        "role": "Control Room Operator",
        "title": "Blok 1 Control Room Senior Operator",
        "email": "operator@pltgu-blok1.co.id",
        "avatar": "O",
        "password_hash": hash_password("operator123"),
        "permissions": ["view", "dashboard", "kpi_trends"]
    }
}

USERS_STORE_PATH = "data/users.json"

def _load_users() -> Dict[str, Dict]:
    """Memuat database pengguna dari berkas JSON jika tersedia, atau menginisialisasi bawaan."""
    if os.path.exists(USERS_STORE_PATH):
        try:
            with open(USERS_STORE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_USERS
    _save_users(DEFAULT_USERS)
    return DEFAULT_USERS

def _save_users(users: Dict[str, Dict]):
    """Menyimpan database pengguna ke JSON."""
    os.makedirs(os.path.dirname(USERS_STORE_PATH), exist_ok=True)
    with open(USERS_STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

def update_user_profile(username: str, new_name: str, new_email: Optional[str] = None, session_state: Optional[dict] = None) -> bool:
    """Memperbarui informasi profil pengguna dan menyimpannya secara persisten ke data/users.json."""
    if not username or not new_name or not new_name.strip():
        return False
        
    users = _load_users()
    uname = normalize_username(username)
    
    if uname in users:
        cleaned_name = new_name.strip()
        users[uname]["name"] = cleaned_name
        users[uname]["avatar"] = cleaned_name[0].upper()
        if new_email and new_email.strip():
            users[uname]["email"] = new_email.strip()
            
        _save_users(users)
        
        # Perbarui juga di session_state yang sedang aktif
        if session_state and "auth_user" in session_state and session_state["auth_user"]:
            session_state["auth_user"]["name"] = cleaned_name
            session_state["auth_user"]["avatar"] = cleaned_name[0].upper()
            if new_email and new_email.strip():
                session_state["auth_user"]["email"] = new_email.strip()
                
            logs = session_state.setdefault("change_logs", [])
            logs.append({
                "version": session_state.get("active_version", "v1_raw"),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "rows": len(session_state.get("active_df", [])) if session_state.get("active_df") is not None else 0,
                "columns": len(session_state.get("active_df", {}).columns) if session_state.get("active_df") is not None else 0,
                "action": f"Profil Diperbarui: Pengguna '{uname}' mengubah nama tampilan menjadi '{cleaned_name}'."
            })
        return True
    return False


def update_user_password(username: str, new_password: str, old_password: Optional[str] = None, session_state: Optional[dict] = None) -> Tuple[bool, str]:
    """
    Memperbarui kata sandi pengguna secara aman ke data/users.json.
    Jika old_password diberikan, sistem memvalidasi kecocokan kata sandi saat ini terlebih dahulu.
    """
    if not username:
        return False, "Pengguna tidak valid."
    if not new_password or len(new_password.strip()) < 4:
        return False, "Kata sandi baru minimal 4 karakter."
        
    users = _load_users()
    uname = normalize_username(username)
    if uname not in users:
        return False, "Akun pengguna tidak ditemukan di basis data."
        
    u_data = users[uname]
    if old_password is not None and old_password != "":
        expected_hash = u_data.get("password_hash")
        if expected_hash != hash_password(old_password):
            return False, "Kata sandi saat ini tidak cocok."
            
    new_hash = hash_password(new_password.strip())
    users[uname]["password_hash"] = new_hash
    _save_users(users)
    
    if session_state:
        logs = session_state.setdefault("change_logs", [])
        logs.append({
            "version": session_state.get("active_version", "v1_raw"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "rows": len(session_state.get("active_df", [])) if session_state.get("active_df") is not None else 0,
            "columns": len(session_state.get("active_df", {}).columns) if session_state.get("active_df") is not None else 0,
            "action": f"Keamanan Akun: Kata sandi untuk pengguna '{uname}' berhasil diperbarui."
        })
    return True, "Kata sandi berhasil diperbarui!"


def authenticate(username: str, password: str) -> Optional[User]:
    """
    Memverifikasi username dan password.
    Mengembalikan instance User jika valid, atau None jika gagal.
    """
    if not username or not password:
        return None
        
    users = _load_users()
    uname = normalize_username(username)
    
    if uname in users:
        u_data = users[uname]
        expected_hash = u_data.get("password_hash")
        computed_hash = hash_password(password)
        if expected_hash == computed_hash:
            return User(
                username=u_data["username"],
                name=u_data["name"],
                role=u_data["role"],
                title=u_data.get("title", "Operasional PLTGU"),
                email=u_data.get("email", f"{uname}@pltgu-blok1.co.id"),
                avatar=u_data.get("avatar", uname[0].upper()),
                permissions=u_data.get("permissions", ["view"])
            )
    return None

SESSION_SECRET = "PLTGU_SESSION_KEY_2026_SECURE"

def create_session_token(username: str) -> str:
    """Membuat session token bertanda tangan kriptografis untuk persistensi login lintas reload."""
    timestamp = int(datetime.now().timestamp())
    raw = f"{username}:{timestamp}:{SESSION_SECRET}"
    signature = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]
    return f"{username}.{timestamp}.{signature}"

def verify_session_token(token: str, max_age_days: int = 7) -> Optional[User]:
    """Memverifikasi session token. Mengembalikan User jika valid dan belum kedaluwarsa."""
    if not token or "." not in token:
        return None
    parts = token.split(".")
    if len(parts) != 3:
        return None
    username, ts_str, signature = parts
    try:
        ts = int(ts_str)
        now = int(datetime.now().timestamp())
        if now - ts > max_age_days * 86400 or ts > now + 60:
            return None
        raw = f"{username}:{ts}:{SESSION_SECRET}"
        expected_sig = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]
        if signature != expected_sig:
            return None
            
        users = _load_users()
        uname = normalize_username(username)
        if uname in users:
            u_data = users[uname]
            return User(
                username=u_data["username"],
                name=u_data["name"],
                role=u_data["role"],
                title=u_data.get("title", "Operasional PLTGU"),
                email=u_data.get("email", f"{uname}@pltgu-blok1.co.id"),
                avatar=u_data.get("avatar", uname[0].upper()),
                permissions=u_data.get("permissions", ["view"])
            )
    except Exception:
        return None
    return None

def login(username: str, password: str, session_state: dict) -> Tuple[bool, str]:
    """
    Melakukan proses login ke dalam session state Streamlit.
    Mencatat log login ke dalam change_logs untuk keperluan audit trail.
    """
    user = authenticate(username, password)
    if user:
        session_state["is_authenticated"] = True
        session_state["auth_user"] = user.to_dict()
        session_state["login_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            import streamlit as st
            st.query_params["session"] = create_session_token(user.username)
        except Exception:
            pass
        
        # Tambahkan catatan login ke riwayat audit log
        logs = session_state.setdefault("change_logs", [])
        logs.append({
            "version": session_state.get("active_version", "v1_raw"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "rows": len(session_state.get("active_df", [])) if session_state.get("active_df") is not None else 0,
            "columns": len(session_state.get("active_df", {}).columns) if session_state.get("active_df") is not None else 0,
            "action": f"Autentikasi Berhasil: User '{user.username}' ({user.role}) masuk ke sesi audit."
        })
        return True, f"Selamat datang, {user.name}!"
    return False, "Nama pengguna atau kata sandi tidak sesuai. Silakan periksa kembali."

def quick_login(username: str, session_state: dict) -> Tuple[bool, str]:
    """Fasilitas akses cepat akun untuk pengujian langsung."""
    users = _load_users()
    uname = normalize_username(username)
    if uname in users:
        u_data = users[uname]
        user = User(
            username=u_data["username"],
            name=u_data["name"],
            role=u_data["role"],
            title=u_data.get("title", "Operasional PLTGU"),
            email=u_data.get("email", f"{uname}@pltgu-blok1.co.id"),
            avatar=u_data.get("avatar", uname[0].upper()),
            permissions=u_data.get("permissions", ["view"])
        )
        session_state["is_authenticated"] = True
        session_state["auth_user"] = user.to_dict()
        session_state["login_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            import streamlit as st
            st.query_params["session"] = create_session_token(user.username)
        except Exception:
            pass
        
        logs = session_state.setdefault("change_logs", [])
        logs.append({
            "version": session_state.get("active_version", "v1_raw"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "rows": len(session_state.get("active_df", [])) if session_state.get("active_df") is not None else 0,
            "columns": len(session_state.get("active_df", {}).columns) if session_state.get("active_df") is not None else 0,
            "action": f"Autentikasi Cepat: User '{user.username}' ({user.role}) aktif."
        })
        return True, f"Masuk sebagai {user.name}"
    return False, "Akun tidak ditemukan."

def logout(session_state: dict):
    """Menghapus sesi login pengguna dan mencatat event logout."""
    current_user = session_state.get("auth_user", {}).get("username", "Anonim")
    logs = session_state.setdefault("change_logs", [])
    logs.append({
        "version": session_state.get("active_version", "v1_raw"),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "rows": len(session_state.get("active_df", [])) if session_state.get("active_df") is not None else 0,
        "columns": len(session_state.get("active_df", {}).columns) if session_state.get("active_df") is not None else 0,
        "action": f"User '{current_user}' berhasil keluar (logout) dari sesi audit."
    })
    
    session_state["is_authenticated"] = False
    session_state["auth_user"] = None
    session_state["login_time"] = None
    try:
        import streamlit as st
        st.query_params.pop("session", None)
    except Exception:
        pass

def get_current_user(session_state: dict) -> Optional[User]:
    """Mendapatkan data pengguna aktif saat ini dari session state."""
    u_dict = session_state.get("auth_user")
    if u_dict:
        return User(**u_dict)
    return None

def is_authenticated(session_state: dict) -> bool:
    """Memeriksa apakah ada pengguna yang sedang terautentikasi."""
    return bool(session_state.get("is_authenticated", False))

# DAFTAR SELURUH 12 MODUL APLIKASI
ALL_MODULES = [
    "Dashboard Utama",
    "Import Data Historian",
    "Tag Mapping & Unit",
    "Validasi Kualitas Data",
    "Pembersihan Terkendali",
    "Tren KPI & Korelasi",
    "Analisis Sub-Sistem Unit",
    "Neraca Massa & Energi",
    "Deteksi Anomali AI",
    "Persiapan Aspen HYSYS",
    "Laporan Formal & Ekspor",
    "Audit Log & Pengaturan"
]

# MATRIKS IZIN AKSES PERAN (ROLE-BASED ACCESS CONTROL)
ROLE_ALLOWED_MODULES = {
    # 1. Maintenance 1 / Lead Auditor & Admin: Akses Penuh ke seluruh 12 Modul
    "maintenance1": ALL_MODULES,
    "maintenance 1": ALL_MODULES,
    "rafli": ALL_MODULES,
    "Maintenance 1 / Lead Auditor": ALL_MODULES,
    "Lead Auditor": ALL_MODULES,
    "Lead Auditor / Admin": ALL_MODULES,
    
    # 2. Plant Performance Engineer: 11 Modul Rekayasa Termal (Kecuali Pengaturan Sistem & Batas Fisik Inti)
    "engineer": [
        "Dashboard Utama",
        "Import Data Historian",
        "Tag Mapping & Unit",
        "Validasi Kualitas Data",
        "Pembersihan Terkendali",
        "Tren KPI & Korelasi",
        "Analisis Sub-Sistem Unit",
        "Neraca Massa & Energi",
        "Deteksi Anomali AI",
        "Persiapan Aspen HYSYS",
        "Laporan Formal & Ekspor"
    ],
    "Plant Performance Engineer": [
        "Dashboard Utama",
        "Import Data Historian",
        "Tag Mapping & Unit",
        "Validasi Kualitas Data",
        "Pembersihan Terkendali",
        "Tren KPI & Korelasi",
        "Analisis Sub-Sistem Unit",
        "Neraca Massa & Energi",
        "Deteksi Anomali AI",
        "Persiapan Aspen HYSYS",
        "Laporan Formal & Ekspor"
    ],
    
    # 3. Control Room Operator: 4 Modul Operasional Monitoring Real-Time
    "operator": [
        "Dashboard Utama",
        "Validasi Kualitas Data",
        "Tren KPI & Korelasi",
        "Analisis Sub-Sistem Unit"
    ],
    "Control Room Operator": [
        "Dashboard Utama",
        "Validasi Kualitas Data",
        "Tren KPI & Korelasi",
        "Analisis Sub-Sistem Unit"
    ]
}

def get_allowed_modules(username_or_role: str) -> List[str]:
    """Mendapatkan daftar modul yang diizinkan untuk peran atau username tertentu."""
    key = (username_or_role or "").strip()
    norm = normalize_username(key)
    if norm in ROLE_ALLOWED_MODULES:
        return ROLE_ALLOWED_MODULES[norm]
    if key in ROLE_ALLOWED_MODULES:
        return ROLE_ALLOWED_MODULES[key]
    
    key_lower = key.lower()
    if "admin" in key_lower or "auditor" in key_lower or "maintenance" in key_lower or key_lower == "rafli":
        return ALL_MODULES
    if "engineer" in key_lower:
        return ROLE_ALLOWED_MODULES["engineer"]
    if "operator" in key_lower:
        return ROLE_ALLOWED_MODULES["operator"]
        
    return ROLE_ALLOWED_MODULES.get(key_lower, ROLE_ALLOWED_MODULES["operator"])

def is_module_allowed(username_or_role: str, module_name: str) -> bool:
    """Memeriksa apakah modul tertentu diizinkan untuk user/role saat ini."""
    allowed = get_allowed_modules(username_or_role)
    return module_name in allowed

