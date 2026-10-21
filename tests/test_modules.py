"""
Unit Test Menyeluruh untuk Modul Kualitas Data, Steam Tables, Neraca Massa, dan Deteksi AI
"""

import pytest
import pandas as pd
import numpy as np
from core.steam_tables import get_steam_enthalpy, get_water_enthalpy, get_isentropic_expansion
from core.data_quality import analyze_data_quality
from core.mass_energy_balance import evaluate_mass_balance, evaluate_energy_balance_hrsg
from core.ai_anomaly import AnomalyDetector

def test_steam_tables_iapws():
    """Memastikan entalpi uap dan air berada dalam rentang wajar IAPWS-IF97"""
    # Main steam superheated pada 68 bar, 515 C -> h ~ 3450 kJ/kg
    h_steam = get_steam_enthalpy(p_bar=68.0, t_c=515.0)
    assert 3400.0 < h_steam < 3550.0

    # Feedwater subcooled pada 78 bar, 125 C -> h ~ 530 kJ/kg
    h_fw = get_water_enthalpy(p_bar=78.0, t_c=125.0)
    assert 500.0 < h_fw < 560.0

    # Isentropic expansion
    h_in, h_out_s, delta_h = get_isentropic_expansion(p_in_bar=68.0, t_in_c=515.0, p_out_bar=0.08)
    assert delta_h > 800.0  # Penurunan entalpi kerja yang signifikan

def test_data_quality_detection():
    """Memastikan validator kualitas data mendeteksi missing, gap, dan duplikasi"""
    df = pd.DataFrame({
        "timestamp": ["2026-10-01 00:00:00", "2026-10-01 00:05:00", "2026-10-01 00:20:00", "2026-10-01 00:20:00"],
        "power_mw": [100.0, None, 105.0, 105.0]
    })
    report = analyze_data_quality(df, timestamp_col="timestamp", expected_interval_min=5.0)
    assert report.total_rows == 4
    assert report.duplicate_count == 1
    assert report.gap_count >= 1
    assert report.missing_pct > 0

def test_mass_balance_evaluation():
    """Memastikan neraca massa menghitung residual dan persentase relatif dengan benar"""
    inlets = {"Stream A": 50.0, "Stream B": 50.0}
    outlets = {"Stream C": 98.0}
    res = evaluate_mass_balance("Test Boundary", inlets, outlets, flow_unit="kg/s")
    assert res["status"] == "VALID"
    assert res["residual_abs"] == 2.0
    assert res["residual_pct"] == 2.0  # (2.0 / 100.0) * 100%

def test_ai_anomaly_detection_with_debounce():
    """Memastikan deteksi anomali dengan persistence window tidak terpicu oleh spike tunggal"""
    np.random.seed(42)
    ts_range = pd.date_range("2026-10-01 00:00:00", periods=30, freq="5min")
    timestamps = [ts.strftime("%Y-%m-%d %H:%M:%S") for ts in ts_range]
    val_normal = np.random.normal(100.0, 0.5, 30)
    # Tambahkan spike 1 titik di index 10
    val_normal[10] = 180.0
    
    df = pd.DataFrame({
        "timestamp": timestamps,
        "feature_1": val_normal
    })
    
    # Persistence window = 3 (membutuhkan 3 titik berurutan) -> spike 1 titik tidak boleh jadi temuan
    detector = AnomalyDetector(contamination=0.05, persistence_window=3)
    findings = detector.detect_anomalies(df, timestamp_col="timestamp", feature_cols=["feature_1"], equipment_name="TestEQ")
    assert len(findings) == 0
