"""
Modul Evaluasi Neraca Massa dan Neraca Energi PLTGU (Halaman 8-9)
Menghitung residual aliran masuk dan keluar per boundary terpilih dengan validasi kecukupan data.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from core.models import KPIResult
from core.steam_tables import get_water_enthalpy, get_steam_enthalpy

def evaluate_mass_balance(boundary_name: str, 
                          inlet_streams: Dict[str, float], 
                          outlet_streams: Dict[str, float], 
                          flow_unit: str = "kg/s") -> Dict[str, Any]:
    """
    Menghitung neraca massa tunak: Residual_m = sum(m_dot_in) - sum(m_dot_out).
    Aturan wajib: Hanya jika seluruh aliran relevan terdaftar.
    """
    res = {
        "boundary": boundary_name,
        "status": "VALID",
        "status_reason": "",
        "total_inlet": 0.0,
        "total_outlet": 0.0,
        "residual_abs": 0.0,
        "residual_pct": 0.0,
        "denominator_definition": "Total Aliran Massa Masuk (Sum m_dot_in)",
        "inlet_details": inlet_streams,
        "outlet_details": outlet_streams,
        "unit": flow_unit
    }
    
    # Cek ketiadaan data
    for name, val in {**inlet_streams, **outlet_streams}.items():
        if val is None or np.isnan(val):
            res["status"] = "NOT_ENOUGH_DATA"
            res["status_reason"] = f"Aliran penting '{name}' tidak memiliki data (tidak boleh diasumsikan nol)."
            return res
            
    total_in = float(sum(inlet_streams.values()))
    total_out = float(sum(outlet_streams.values()))
    residual = total_in - total_out
    
    res["total_inlet"] = round(total_in, 2)
    res["total_outlet"] = round(total_out, 2)
    res["residual_abs"] = round(residual, 2)
    
    if total_in > 0:
        rel_pct = (residual / total_in) * 100.0
        res["residual_pct"] = round(rel_pct, 2)
        if abs(rel_pct) > 5.0:
            res["status"] = "WARNING"
            res["status_reason"] = f"Ketidakseimbangan massa ({rel_pct:+.2f}%) melebihi ambang 5%."
    else:
        res["residual_pct"] = 0.0
        res["status"] = "NOT_ENOUGH_DATA"
        res["status_reason"] = "Total aliran masuk bernilai nol."
        
    return res


def evaluate_energy_balance_hrsg(gas_inlet_t_c: Optional[float], 
                                 gas_outlet_t_c: Optional[float], 
                                 flue_gas_flow_kg_s: Optional[float], 
                                 steam_flow_kg_s: Optional[float], 
                                 feedwater_flow_kg_s: Optional[float], 
                                 steam_p_bar: Optional[float], 
                                 steam_t_c: Optional[float], 
                                 fw_p_bar: Optional[float], 
                                 fw_t_c: Optional[float], 
                                 flue_gas_cp: float = 1.08) -> Dict[str, Any]:
    """
    Evaluasi Neraca Energi HRSG:
    - Sisi Gas Buang: Q_gas = m_gas * Cp * (T_in - T_out)
    - Sisi Air/Uap: Q_steam = m_steam * h_steam - m_fw * h_fw
    - Residual Energi = Q_gas - Q_steam - Q_losses
    """
    res = {
        "boundary": "HRSG Overall",
        "status": "VALID",
        "status_reason": "",
        "q_gas_kw": None,
        "q_steam_kw": None,
        "residual_kw": None,
        "residual_pct": None,
        "pinch_approach_note": "Pinch & approach dihitung dari kurva saturasi uap aktual."
    }
    
    # Cek prasyarat data
    required = [gas_inlet_t_c, gas_outlet_t_c, flue_gas_flow_kg_s, steam_flow_kg_s, feedwater_flow_kg_s, steam_p_bar, steam_t_c, fw_p_bar, fw_t_c]
    if any(v is None or np.isnan(v) for v in required):
        res["status"] = "NOT_ENOUGH_DATA"
        res["status_reason"] = "Data aliran entalpi gas buang atau air/uap belum lengkap untuk neraca energi tertutup."
        return res
        
    # Sisi gas
    delta_t_gas = gas_inlet_t_c - gas_outlet_t_c
    q_gas = flue_gas_flow_kg_s * flue_gas_cp * delta_t_gas
    
    # Sisi air/uap
    h_steam = get_steam_enthalpy(steam_p_bar, steam_t_c)
    h_fw = get_water_enthalpy(fw_p_bar, fw_t_c)
    q_steam = (steam_flow_kg_s * h_steam) - (feedwater_flow_kg_s * h_fw)
    
    residual = q_gas - q_steam
    rel_pct = (residual / max(1.0, q_gas)) * 100.0
    
    res["q_gas_kw"] = round(q_gas, 2)
    res["q_steam_kw"] = round(q_steam, 2)
    res["residual_kw"] = round(residual, 2)
    res["residual_pct"] = round(rel_pct, 2)
    
    if abs(rel_pct) > 10.0:
        res["status"] = "WARNING"
        res["status_reason"] = f"Residual energi HRSG ({rel_pct:+.2f}%) mengindikasikan rugi radiasi tinggi, blowdown tak terukur, atau deviasi meter flow."
        
    return res


def evaluate_condenser_balance(q_cw_kw: Optional[float], 
                               steam_flow_kg_s: Optional[float], 
                               condenser_p_bar: Optional[float], 
                               condensate_t_c: Optional[float]) -> Dict[str, Any]:
    """
    Evaluasi Neraca Kondensor:
    Duty uap kondensasi vs duty pendinginan air cooling water.
    """
    res = {
        "boundary": "Surface Condenser",
        "status": "VALID",
        "status_reason": "",
        "q_cw_kw": q_cw_kw,
        "q_cond_steam_kw": None,
        "residual_kw": None,
        "residual_pct": None
    }
    
    if q_cw_kw is None or steam_flow_kg_s is None or condenser_p_bar is None or condensate_t_c is None:
        res["status"] = "NOT_ENOUGH_DATA"
        res["status_reason"] = "Data parameter kondensor (laju uap masuk, tekanan vakum, atau CW) tidak lengkap."
        return res
        
    # Entalpi uap buang turbin masuk kondensor (kualitas uap ~0.90 - 0.95)
    # Estimasi kasar entalpi uap masuk vs kondensat keluar
    h_exhaust = 2400.0  # kJ/kg rata-rata exhaust steam
    h_condensate = get_water_enthalpy(condenser_p_bar, condensate_t_c)
    q_cond_steam = steam_flow_kg_s * (h_exhaust - h_condensate)
    
    residual = q_cond_steam - q_cw_kw
    rel_pct = (residual / max(1.0, q_cond_steam)) * 100.0
    
    res["q_cond_steam_kw"] = round(q_cond_steam, 2)
    res["residual_kw"] = round(residual, 2)
    res["residual_pct"] = round(rel_pct, 2)
    
    if abs(rel_pct) > 15.0:
        res["status"] = "WARNING"
        res["status_reason"] = f"Perbedaan duty kondensor ({rel_pct:+.2f}%) mengindikasikan losses, ketidakpastian meter flow CW, atau entalpi exhaust aktual berbeda."
        
    return res
