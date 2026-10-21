"""
Modul Pembersihan Terkendali (Controlled Cleaning) & Filter Periode (Halaman 2, 3 & 4)
Menghasilkan dataset turunan berversi dan log perubahan tanpa mengubah data mentah asli.
"""

from typing import Dict, Any, List, Tuple, Optional
import pandas as pd
import numpy as np
from datetime import datetime

class CleaningManager:
    """Mengelola versi dataset turunan dan riwayat audit trail (Halaman 3 Poin 10)"""
    
    def __init__(self, raw_df: pd.DataFrame, version_name: str = "v1_raw"):
        self.versions: Dict[str, pd.DataFrame] = {version_name: raw_df.copy()}
        self.change_logs: List[Dict[str, Any]] = [{
            "version": version_name,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "rows": len(raw_df),
            "columns": len(raw_df.columns),
            "action": "Inisialisasi dataset mentah (raw data utuh)"
        }]
        self.active_version: str = version_name

    def get_current_df(self) -> pd.DataFrame:
        return self.versions[self.active_version]

    def create_cleaned_version(self, 
                               new_version_name: str,
                               df_filtered: pd.DataFrame, 
                               action_description: str,
                               filter_rules: Dict[str, Any]) -> str:
        """Menyimpan versi baru dengan log perubahan eksplisit"""
        self.versions[new_version_name] = df_filtered.copy()
        self.active_version = new_version_name
        self.change_logs.append({
            "version": new_version_name,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "rows": len(df_filtered),
            "columns": len(df_filtered.columns),
            "action": action_description,
            "rules": filter_rules
        })
        return new_version_name


def filter_steady_state_periods(df: pd.DataFrame, 
                                power_col: str, 
                                min_load_mw: float = 30.0,
                                max_ramp_rate_mw_per_min: float = 1.0,
                                interval_min: float = 5.0) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Memisahkan operasi stabil (steady-state) dari start-up, trip, dan transien cepat.
    Sesuai Halaman 3 Poin 6 & Halaman 14 Poin 6.
    Mengembalikan (df_steady, mask_steady).
    """
    if df.empty or power_col not in df.columns:
        return df, pd.Series(True, index=df.index)
        
    power_series = pd.to_numeric(df[power_col], errors="coerce")
    
    # Kriteria 1: Beban di atas batas minimum (bukan idle / offline / shutdown)
    load_cond = power_series >= min_load_mw
    
    # Kriteria 2: Laju perubahan beban (ramp rate) rendah (steady-state)
    power_diff = power_series.diff().abs()
    max_step_change = max_ramp_rate_mw_per_min * interval_min
    ramp_cond = (power_diff <= max_step_change) | power_diff.isna()
    
    steady_mask = load_cond & ramp_cond
    df_steady = df[steady_mask].copy()
    
    return df_steady, steady_mask


def filter_by_date_range(df: pd.DataFrame, 
                         timestamp_col: str, 
                         start_date: Optional[str] = None, 
                         end_date: Optional[str] = None) -> pd.DataFrame:
    """
    Menyaring dataset berdasarkan rentang waktu tanpa menghapus baris di versi awal.
    """
    if df.empty or timestamp_col not in df.columns:
        return df
        
    ts_series = pd.to_datetime(df[timestamp_col], errors="coerce")
    mask = pd.Series(True, index=df.index)
    
    if start_date:
        mask = mask & (ts_series >= pd.to_datetime(start_date))
    if end_date:
        mask = mask & (ts_series <= pd.to_datetime(end_date))
        
    return df[mask].copy()
