"""
Calculation Engine - Website Audit Energi dan Kinerja PLTGU
Mengimplementasikan seluruh rumus deterministik rekayasa sesuai Lampiran Teknis Wajib (Halaman 6-10).
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from core.models import KPIResult
from core.steam_tables import get_water_enthalpy, get_steam_enthalpy, get_isentropic_expansion

# Versi mesin hitung untuk audit trail
ENGINE_VERSION = "v1.2.0-deterministic"

def calc_fuel_heat_input(flow: Optional[float], 
                         flow_unit: str = "kg/h", 
                         lhv: Optional[float] = None, 
                         lhv_unit: str = "kJ/kg") -> KPIResult:
    """
    Menghitung Laju Kalor Bahan Bakar (Fuel Heat Input Q_dot_fuel) dalam kW.
    Acceptance test: 1000 kg/h & LHV 50.000 kJ/kg -> 13.888,89 kW
    """
    kpi = KPIResult(
        code="QDOT_FUEL",
        name="Fuel Heat Input",
        value=None,
        unit="kW",
        status="VALID",
        boundary="Fuel Gas Supply",
        formula="Qdot_fuel = flow * LHV / factor",
        formula_version=ENGINE_VERSION,
        basis="LHV"
    )
    
    if flow is None or lhv is None or np.isnan(flow) or np.isnan(lhv):
        kpi.status = "NOT_ENOUGH_DATA"
        kpi.status_reason = "Data hilang: flow atau LHV bahan bakar tidak tersedia (tidak boleh diisi nol)."
        return kpi
        
    if flow < 0 or lhv <= 0:
        kpi.status = "WARNING"
        kpi.status_reason = "Nilai flow negatif atau LHV tidak positif tidak valid secara fisik."
        return kpi

    unit_norm = flow_unit.strip().lower()
    if unit_norm in ["kg/s"]:
        q_kw = flow * lhv
    elif unit_norm in ["kg/h", "kg/jam"]:
        q_kw = (flow * lhv) / 3600.0
    elif unit_norm in ["nm3/h", "nm3/jam", "nm³/h"]:
        # Asumsi lhv dalam kJ/Nm3
        q_kw = (flow * lhv) / 3600.0
    elif unit_norm in ["t/h", "ton/h", "ton/jam"]:
        q_kw = (flow * 1000.0 * lhv) / 3600.0
    else:
        kpi.status = "INVALID_UNIT"
        kpi.status_reason = f"Satuan laju alir bahan bakar '{flow_unit}' tidak dikenali."
        return kpi
        
    kpi.value = round(float(q_kw), 2)
    kpi.inputs_used = {"flow": flow, "flow_unit": flow_unit, "lhv": lhv, "lhv_unit": lhv_unit}
    return kpi


def calc_net_power(p_gross_mw: Optional[float], 
                   p_aux_mw: Optional[float], 
                   p_net_direct_mw: Optional[float] = None) -> KPIResult:
    """
    Menghitung Daya Listrik Neto (P_net) dalam MW.
    Acceptance test: P_gross 100 MW, P_aux 5 MW -> P_net = 95 MW.
    """
    kpi = KPIResult(
        code="P_NET",
        name="Daya Listrik Neto PLTGU",
        value=None,
        unit="MW",
        status="VALID",
        boundary="High Voltage Switchyard / Delivery Point",
        formula="P_net = P_gross_total - P_aux",
        formula_version=ENGINE_VERSION,
        basis="Net"
    )
    
    if p_net_direct_mw is not None and not np.isnan(p_net_direct_mw):
        kpi.value = round(float(p_net_direct_mw), 2)
        kpi.formula = "P_net (measured direct from fiscal revenue meter)"
        kpi.inputs_used = {"p_net_direct_mw": p_net_direct_mw}
        return kpi
        
    if p_gross_mw is None or p_aux_mw is None or np.isnan(p_gross_mw) or np.isnan(p_aux_mw):
        kpi.status = "NOT_ENOUGH_DATA"
        kpi.status_reason = "Data hilang: P_gross atau P_aux tidak tersedia."
        return kpi
        
    p_net = p_gross_mw - p_aux_mw
    if p_net < 0:
        kpi.status = "WARNING"
        kpi.status_reason = "P_net bernilai negatif (pemakaian auxiliary melebihi daya gross)."
        
    kpi.value = round(float(p_net), 2)
    kpi.inputs_used = {"p_gross_mw": p_gross_mw, "p_aux_mw": p_aux_mw}
    return kpi


def calc_auxiliary_load_ratio(p_aux_mw: Optional[float], 
                              p_gross_mw: Optional[float]) -> KPIResult:
    """
    Menghitung Persentase Beban Auxiliary PLTGU (%).
    Acceptance test: P_aux 5 MW, P_gross 100 MW -> 5.0%.
    """
    kpi = KPIResult(
        code="AUX_LOAD_RATIO",
        name="Auxiliary Load Ratio",
        value=None,
        unit="%",
        status="VALID",
        boundary="Plant Auxiliary Transformer",
        formula="Auxiliary Load (%) = 100 * P_aux / P_gross_total",
        formula_version=ENGINE_VERSION
    )
    
    if p_aux_mw is None or p_gross_mw is None or np.isnan(p_aux_mw) or np.isnan(p_gross_mw):
        kpi.status = "NOT_ENOUGH_DATA"
        kpi.status_reason = "Data hilang: P_aux atau P_gross tidak tersedia."
        return kpi
        
    if p_gross_mw <= 0:
        kpi.status = "NOT_ENOUGH_DATA"
        kpi.status_reason = "P_gross nol atau negatif; rasio auxiliary tidak dapat dihitung (menghindari pembagian nol)."
        return kpi
        
    ratio = (p_aux_mw / p_gross_mw) * 100.0
    if ratio > 25.0:
        kpi.status = "WARNING"
        kpi.status_reason = f"Rasio auxiliary {ratio:.1f}% melebihi rentang wajar PLTGU (normal 2-6%)."
        
    kpi.value = round(float(ratio), 2)
    kpi.inputs_used = {"p_aux_mw": p_aux_mw, "p_gross_mw": p_gross_mw}
    return kpi


def calc_period_heat_rate(total_fuel_energy_kj: Optional[float], 
                          total_net_elec_energy_kwh: Optional[float],
                          basis: str = "Net LHV") -> KPIResult:
    """
    Menghitung Heat Rate Periode (kJ/kWh).
    Aturan wajib: Dihitung dari total energi periode, BUKAN rata-rata aritmetika heat rate baris!
    Acceptance test: Qdot_fuel 100.000 kW & Pnet 50.000 kW konstan -> 7.200 kJ/kWh.
    """
    kpi = KPIResult(
        code="HEAT_RATE",
        name=f"Heat Rate Periode ({basis})",
        value=None,
        unit="kJ/kWh",
        status="VALID",
        boundary="Fuel Gas Boundary to Net Meter",
        formula="HR = Total Energi Bahan Bakar (kJ) / Total Energi Listrik (kWh)",
        formula_version=ENGINE_VERSION,
        basis=basis
    )
    
    if total_fuel_energy_kj is None or total_net_elec_energy_kwh is None or np.isnan(total_fuel_energy_kj) or np.isnan(total_net_elec_energy_kwh):
        kpi.status = "NOT_ENOUGH_DATA"
        kpi.status_reason = "Data hilang: total energi bahan bakar atau energi listrik tidak tersedia."
        return kpi
        
    if total_net_elec_energy_kwh <= 0:
        kpi.status = "NOT_ENOUGH_DATA"
        kpi.status_reason = "Total energi listrik netto <= 0; heat rate periode tidak dapat dihitung."
        return kpi
        
    hr = total_fuel_energy_kj / total_net_elec_energy_kwh
    kpi.value = round(float(hr), 2)
    kpi.inputs_used = {
        "total_fuel_energy_kj": total_fuel_energy_kj, 
        "total_net_elec_energy_kwh": total_net_elec_energy_kwh
    }
    return kpi


def calc_period_efficiency(total_elec_energy_kwh: Optional[float], 
                           total_fuel_energy_kj: Optional[float],
                           basis: str = "Net LHV") -> KPIResult:
    """
    Menghitung Efisiensi Termal Listrik Periode (%).
    Acceptance test: Heat input 100.000 kW, net power 50.000 kW -> 50.0%.
    """
    kpi = KPIResult(
        code="EFFICIENCY",
        name=f"Efisiensi Listrik Periode ({basis})",
        value=None,
        unit="%",
        status="VALID",
        boundary="Plant Fuel to Switchyard",
        formula="Efficiency (%) = 100 * (E_elec_kWh * 3600 kJ/kWh) / E_fuel_kJ",
        formula_version=ENGINE_VERSION,
        basis=basis
    )
    
    if total_elec_energy_kwh is None or total_fuel_energy_kj is None or np.isnan(total_elec_energy_kwh) or np.isnan(total_fuel_energy_kj):
        kpi.status = "NOT_ENOUGH_DATA"
        kpi.status_reason = "Data hilang: energi listrik atau energi bahan bakar tidak tersedia."
        return kpi
        
    if total_fuel_energy_kj <= 0:
        kpi.status = "NOT_ENOUGH_DATA"
        kpi.status_reason = "Total energi bahan bakar <= 0; efisiensi tidak dapat dihitung."
        return kpi
        
    eff = (total_elec_energy_kwh * 3600.0 / total_fuel_energy_kj) * 100.0
    if eff > 65.0:
        kpi.status = "WARNING"
        kpi.status_reason = f"Efisiensi terhitung {eff:.1f}% melebihi batas teoritis siklus kombinasi saat ini (>65%)."
    elif eff < 20.0:
        kpi.status = "WARNING"
        kpi.status_reason = f"Efisiensi terhitung {eff:.1f}% sangat rendah untuk siklus PLTGU."
        
    kpi.value = round(float(eff), 2)
    kpi.inputs_used = {
        "total_elec_energy_kwh": total_elec_energy_kwh, 
        "total_fuel_energy_kj": total_fuel_energy_kj
    }
    return kpi


def calc_compressor_pressure_ratio(p_out_bar: Optional[float], 
                                   p_in_bar: Optional[float], 
                                   p_in_is_gauge: bool = False,
                                   p_out_is_gauge: bool = False,
                                   p_atm_bar: float = 1.01325) -> KPIResult:
    """
    Menghitung Compressor Pressure Ratio (PR_comp = P_out,abs / P_in,abs).
    Aturan wajib: Harus menggunakan tekanan absolut, bukan gauge!
    """
    kpi = KPIResult(
        code="COMPRESSOR_PR",
        name="Compressor Pressure Ratio",
        value=None,
        unit="ratio",
        status="VALID",
        boundary="Gas Turbine Compressor Flanges",
        formula="PR_comp = P_discharge,abs / P_inlet,abs",
        formula_version=ENGINE_VERSION
    )
    
    if p_out_bar is None or p_in_bar is None or np.isnan(p_out_bar) or np.isnan(p_in_bar):
        kpi.status = "NOT_ENOUGH_DATA"
        kpi.status_reason = "Data hilang: tekanan inlet atau outlet kompresor tidak tersedia."
        return kpi
        
    p_in_abs = p_in_bar + (p_atm_bar if p_in_is_gauge else 0.0)
    p_out_abs = p_out_bar + (p_atm_bar if p_out_is_gauge else 0.0)
    
    if p_in_abs <= 0:
        kpi.status = "WARNING"
        kpi.status_reason = "Tekanan inlet absolut <= 0 bar."
        return kpi
        
    pr = p_out_abs / p_in_abs
    if pr < 1.0:
        kpi.status = "WARNING"
        kpi.status_reason = "Tekanan keluar kompresor lebih rendah dari inlet (PR < 1)."
        
    kpi.value = round(float(pr), 2)
    kpi.inputs_used = {"p_in_abs_bar": p_in_abs, "p_out_abs_bar": p_out_abs}
    return kpi


def calc_cooling_water_duty(m_dot_cw_kg_s: Optional[float], 
                            t_in_c: Optional[float], 
                            t_out_c: Optional[float], 
                            cp_water: float = 4.184) -> KPIResult:
    """
    Menghitung Laju Pelepasan Kalor Cooling Water (kW):
    Q_CW = m_dot_cw * cp * (T_out - T_in)
    """
    kpi = KPIResult(
        code="Q_CW",
        name="Cooling Water Heat Duty",
        value=None,
        unit="kW",
        status="VALID",
        boundary="Condenser Waterbox Flanges",
        formula="Q_CW = m_dot_CW * cp_water * (T_out - T_in)",
        formula_version=ENGINE_VERSION
    )
    
    if m_dot_cw_kg_s is None or t_in_c is None or t_out_c is None:
        kpi.status = "NOT_ENOUGH_DATA"
        kpi.status_reason = "Data hilang: laju alir atau temperatur cooling water tidak lengkap."
        return kpi
        
    delta_t = t_out_c - t_in_c
    q_kw = m_dot_cw_kg_s * cp_water * delta_t
    kpi.value = round(float(q_kw), 2)
    kpi.inputs_used = {
        "m_dot_cw_kg_s": m_dot_cw_kg_s, 
        "t_in_c": t_in_c, 
        "t_out_c": t_out_c, 
        "delta_t_c": round(delta_t, 2)
    }
    return kpi


def integrate_time_series_energy(df: pd.DataFrame, 
                                 power_col: str, 
                                 time_col: str = "timestamp", 
                                 default_interval_min: float = 5.0) -> Dict[str, Any]:
    """
    Mengintegrasikan deret daya (kW) terhadap durasi interval aktual untuk menghitung total energi (kWh).
    Sesuai Halaman 3 Poin 5: Jika interval tidak seragam, gunakan durasi aktual delta t, bukan asumsi interval sama!
    """
    if df.empty or power_col not in df.columns or time_col not in df.columns:
        return {"total_kwh": 0.0, "total_hours": 0.0, "sample_count": 0, "uneven_intervals": False}
        
    df_sorted = df.copy().sort_values(by=time_col).reset_index(drop=True)
    timestamps = pd.to_datetime(df_sorted[time_col], errors="coerce")
    valid_mask = timestamps.notna() & df_sorted[power_col].notna()
    
    clean_df = df_sorted[valid_mask].copy()
    if clean_df.empty:
        return {"total_kwh": 0.0, "total_hours": 0.0, "sample_count": 0, "uneven_intervals": False}
        
    # Hitung selisih waktu aktual antar baris
    if len(clean_df) == 1:
        single_dt = default_interval_min / 60.0
        total_kwh = float(clean_df[power_col].iloc[0] * single_dt)
        return {
            "total_kwh": total_kwh,
            "total_hours": single_dt,
            "sample_count": 1,
            "uneven_intervals": False
        }
        
    clean_timestamps = pd.to_datetime(clean_df[time_col])
    # Durasi tiap interval dari t_i ke t_{i+1}
    dt_forward_hours = (clean_timestamps.shift(-1) - clean_timestamps).iloc[:-1].dt.total_seconds() / 3600.0
    
    # Tangani gap tidak wajar (misal outage/gap data > 2 jam)
    dt_forward_hours = dt_forward_hours.apply(lambda dt: (default_interval_min / 60.0) if (dt <= 0 or dt > 2.0) else dt)
    
    powers_kw = clean_df[power_col].iloc[:-1].values
    dts = dt_forward_hours.values
    
    unique_dts = np.unique(np.round(dts, 4))
    uneven = len(unique_dts) > 1
    
    energies_kwh = powers_kw * dts
    total_kwh = float(np.sum(energies_kwh))
    total_hours = float(np.sum(dts))
    
    return {
        "total_kwh": total_kwh,
        "total_hours": total_hours,
        "sample_count": len(clean_df),
        "uneven_intervals": bool(uneven)
    }
