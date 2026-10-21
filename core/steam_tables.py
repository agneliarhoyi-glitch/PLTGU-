"""
Modul Properti Termodinamika Air dan Uap (IAPWS-IF97)
Menghitung entalpi, entropi, dan ekspansi isentropik untuk HRSG, ST, dan Kondensor.
"""

import math
from typing import Optional, Tuple

try:
    from pyXSteam.XSteam import XSteam
    _steam_table = XSteam(XSteam.UNIT_SYSTEM_MKS)  # bar, deg C, kJ/kg, m3/kg, kJ/kgK
    HAS_PYXSTEAM = True
except ImportError:
    HAS_PYXSTEAM = False
    _steam_table = None

def get_water_enthalpy(p_bar: float, t_c: float) -> float:
    """
    Menghitung entalpi air cair (feedwater / condensate) dalam kJ/kg.
    """
    if p_bar is None or t_c is None:
        return 0.0
    if HAS_PYXSTEAM and _steam_table is not None:
        try:
            return float(_steam_table.h_pt(p_bar, t_c))
        except Exception:
            pass
    # Fallback aproksimasi standar: h ≈ cp * T + v * dp
    # cp air ≈ 4.184 kJ/kg.K, basis 0 C = 0 kJ/kg
    return 4.184 * t_c + (p_bar * 100.0 * 0.001)

def get_steam_enthalpy(p_bar: float, t_c: float) -> float:
    """
    Menghitung entalpi uap superheated / uap utama (main steam) dalam kJ/kg.
    """
    if p_bar is None or t_c is None:
        return 0.0
    if HAS_PYXSTEAM and _steam_table is not None:
        try:
            return float(_steam_table.h_pt(p_bar, t_c))
        except Exception:
            pass
    # Fallback korelasi steam superheated aproksimatif
    # h ≈ 2501 + 1.88 * T
    return 2501.0 + 1.95 * t_c + 0.1 * p_bar

def get_saturation_temp(p_bar: float) -> float:
    """
    Temperatur saturasi air pada tekanan p (bar) dalam deg C.
    """
    if p_bar is None or p_bar <= 0:
        return 100.0
    if HAS_PYXSTEAM and _steam_table is not None:
        try:
            return float(_steam_table.tsat_p(p_bar))
        except Exception:
            pass
    # Antoine aproksimasi untuk air
    p_kpa = p_bar * 100.0
    # Logaritma pendekatan
    return 42.6776 + 3892.7 / (9.65 - math.log10(max(p_kpa, 0.1))) - 273.15

def get_isentropic_expansion(p_in_bar: float, t_in_c: float, p_out_bar: float) -> Tuple[float, float, float]:
    """
    Menghitung ekspansi isentropik uap pada Steam Turbine.
    Mengembalikan: (h_in, h_out_isentropic, delta_h_ideal) dalam kJ/kg.
    """
    if p_in_bar is None or t_in_c is None or p_out_bar is None:
        return (0.0, 0.0, 0.0)
    
    if HAS_PYXSTEAM and _steam_table is not None:
        try:
            h_in = float(_steam_table.h_pt(p_in_bar, t_in_c))
            s_in = float(_steam_table.s_pt(p_in_bar, t_in_c))
            h_out_s = float(_steam_table.h_ps(p_out_bar, s_in))
            delta_h = max(0.0, h_in - h_out_s)
            return (h_in, h_out_s, delta_h)
        except Exception:
            pass
            
    # Fallback estimasi
    h_in = get_steam_enthalpy(p_in_bar, t_in_c)
    # Estimasi ekspansi isentropik uap (rasio tekanan)
    expansion_ratio = max(0.01, min(1.0, p_out_bar / max(p_in_bar, 0.01)))
    delta_h = h_in * (1.0 - (expansion_ratio ** 0.23))
    h_out_s = h_in - delta_h
    return (h_in, h_out_s, delta_h)
