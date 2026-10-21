"""
Unit Test - Pengujian Acceptance Test Sesuai Lampiran Teknis K (Halaman 9-10)
Memastikan seluruh perhitungan deterministik menghasilkan angka yang persis sesuai spesifikasi.
"""

import pytest
import pandas as pd
import numpy as np
from core.calculation_engine import (
    calc_fuel_heat_input,
    calc_net_power,
    calc_auxiliary_load_ratio,
    calc_period_heat_rate,
    calc_period_efficiency,
    calc_compressor_pressure_ratio,
    calc_cooling_water_duty,
    integrate_time_series_energy
)

def test_acceptance_fuel_flow_conversion():
    """Test 1: 1000 kg/h dan LHV 50.000 kJ/kg -> Qdot_fuel = 13.888,89 kW"""
    result = calc_fuel_heat_input(flow=1000.0, flow_unit="kg/h", lhv=50000.0, lhv_unit="kJ/kg")
    assert result.status == "VALID"
    assert result.value == pytest.approx(13888.89, abs=0.01)

def test_acceptance_net_power():
    """Test 2: P gross 100 MW, auxiliary 5 MW -> P net = 95 MW"""
    result = calc_net_power(p_gross_mw=100.0, p_aux_mw=5.0)
    assert result.status == "VALID"
    assert result.value == pytest.approx(95.0, abs=0.01)

def test_acceptance_heat_rate():
    """Test 3: Qdot_fuel 100.000 kW dan P net 50.000 kW konstan -> HR = 7.200 kJ/kWh"""
    # Untuk 1 jam operasi konstan: E_fuel = 100.000 kW * 3600 s = 360.000.000 kJ; E_net = 50.000 kWh
    e_fuel_kj = 100000.0 * 3600.0
    e_net_kwh = 50000.0
    result = calc_period_heat_rate(total_fuel_energy_kj=e_fuel_kj, total_net_elec_energy_kwh=e_net_kwh)
    assert result.status == "VALID"
    assert result.value == pytest.approx(7200.0, abs=0.01)

def test_acceptance_net_efficiency():
    """Test 4: Heat input 100.000 kW, net power 50.000 kW -> Efisiensi neto = 50%"""
    e_fuel_kj = 100000.0 * 3600.0
    e_net_kwh = 50000.0
    result = calc_period_efficiency(total_elec_energy_kwh=e_net_kwh, total_fuel_energy_kj=e_fuel_kj)
    assert result.status == "VALID"
    assert result.value == pytest.approx(50.0, abs=0.01)

def test_acceptance_auxiliary_load():
    """Test 5: Paux 5 MW, Pgross 100 MW -> Auxiliary load = 5%"""
    result = calc_auxiliary_load_ratio(p_aux_mw=5.0, p_gross_mw=100.0)
    assert result.status == "VALID"
    assert result.value == pytest.approx(5.0, abs=0.01)

def test_acceptance_missing_data_not_zero():
    """Test 6: LHV tidak ada -> Heat input & Heat rate harus NOT_ENOUGH_DATA, bukan 0"""
    result_fuel = calc_fuel_heat_input(flow=1000.0, flow_unit="kg/h", lhv=None)
    assert result_fuel.status == "NOT_ENOUGH_DATA"
    assert result_fuel.value is None

    result_hr = calc_period_heat_rate(total_fuel_energy_kj=None, total_net_elec_energy_kwh=50000.0)
    assert result_hr.status == "NOT_ENOUGH_DATA"
    assert result_hr.value is None

def test_acceptance_uneven_intervals_integration():
    """Test 7: Periode tidak seragam menggunakan durasi aktual, bukan rata-rata baris"""
    # Interval 1: durasi 10 menit (10/60 jam), Daya 60.000 kW -> Energi = 10.000 kWh
    # Interval 2: durasi 20 menit (20/60 jam), Daya 30.000 kW -> Energi = 10.000 kWh
    # Total kWh = 20.000 kWh (bukan rata-rata daya 45.000 kW * interval sembarangan)
    data = {
        "timestamp": ["2026-10-01 00:00:00", "2026-10-01 00:10:00", "2026-10-01 00:30:00"],
        "power_kw": [60000.0, 30000.0, 30000.0]
    }
    df = pd.DataFrame(data)
    integ = integrate_time_series_energy(df, power_col="power_kw", time_col="timestamp", default_interval_min=10.0)
    
    # Interval 1: 10 min -> 60000 * (10/60) = 10000 kWh
    # Interval 2: 20 min -> 30000 * (20/60) = 10000 kWh
    assert integ["uneven_intervals"] is True
    assert integ["total_kwh"] == pytest.approx(20000.0, abs=1.0)
