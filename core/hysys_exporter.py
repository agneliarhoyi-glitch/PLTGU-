"""
Modul Persiapan Simulasi Aspen HYSYS (Halaman 4 & 9)
Mengekstrak kondisi operasi representatif (baseline) dan menyusun paket data masukan HYSYS.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

FALLBACK_ALIASES = {
    "ambient_temp_c": ["ambient_temp_c", "ambient_temp", "t_ambient", "suhu_lingkungan"],
    "ambient_press_bar": ["ambient_press_bar", "ambient_press", "p_ambient"],
    "fuel_lhv_kj_kg": ["fuel_lhv_kj_kg", "lhv_kj_kg", "lhv", "fuel_lhv"],
    "gt1_fuel_flow": ["CFGAAI-0004", "GTDL-19161", "gt1_fuel_flow_kg_h", "gt1_fuel_flow_kg_s", "gt1_fuel_flow"],
    "gt2_fuel_flow": ["CFGAAI-0005", "GTDL-29161", "gt2_fuel_flow_kg_h", "gt2_fuel_flow_kg_s", "gt2_fuel_flow"],
    "gt3_fuel_flow": ["CFGAAI-0006", "GTDL-39161", "gt3_fuel_flow_kg_h", "gt3_fuel_flow_kg_s", "gt3_fuel_flow"],
    "gt1_comp_p_out": ["GTDL-19149", "gt1_comp_p_out_bar", "gt1_comp_pr"],
    "gt1_exhaust_temp": ["GTDL-19071", "gt1_exhaust_temp_c", "gt1_exhaust_temp"],
    "hrsg1_steam_flow": ["hrsg1_main_steam_flow_kg_s", "hrsg1_steam_flow"],
    "main_steam_p": ["main_steam_pressure_bar", "main_steam_p"],
    "main_steam_t": ["main_steam_temp_c", "main_steam_t"],
    "feedwater_temp_c": ["feedwater_temp_c", "fw_temp_c"],
    "feedwater_pressure_bar": ["feedwater_pressure_bar", "fw_pressure_bar"],
    "condenser_p": ["condenser_pressure_bar", "condenser_p"],
    "cw_in_t": ["4HRCTE-0002", "cw_inlet_temp_c", "cw_in_t"],
    "cw_out_t": ["4HRCTE-0003", "cw_outlet_temp_c", "cw_out_t"],
    "cw_flow": ["cw_flow_kg_s", "cw_flow"],
}

def generate_hysys_input_package(df: pd.DataFrame, 
                                 tag_mapping: Dict[str, str], 
                                 baseline_period_label: str = "Beban Penuh Siang Hari (Oct 01-15)") -> pd.DataFrame:
    """
    Menghasilkan tabel ringkasan kondisi operasi representatif untuk pemodelan Aspen HYSYS.
    Mencakup nilai rata-rata, min, max, standar deviasi, satuan, dan catatan data gap.
    """
    package_rows: List[Dict[str, Any]] = []
    
    # Definisi parameter yang dibutuhkan HYSYS
    hysys_parameters = [
        {"key": "ambient_temp_c", "desc": "Temperatur Udara Ambient", "unit": "°C", "stream": "Air Inlet GT", "req": True},
        {"key": "ambient_press_bar", "desc": "Tekanan Barometrik Ambient", "unit": "bar(a)", "stream": "Air Inlet GT", "req": True},
        {"key": "fuel_lhv_kj_kg", "desc": "Nilai Kalor Bawah Bahan Bakar (LHV)", "unit": "kJ/kg", "stream": "Fuel Gas Feed", "req": True},
        {"key": "gt1_fuel_flow", "desc": "Laju Alir Bahan Bakar Gas GT-1", "unit": "kg/h", "stream": "GT-1 Combustor", "req": True},
        {"key": "gt2_fuel_flow", "desc": "Laju Alir Bahan Bakar Gas GT-2", "unit": "kg/h", "stream": "GT-2 Combustor", "req": True},
        {"key": "gt3_fuel_flow", "desc": "Laju Alir Bahan Bakar Gas GT-3", "unit": "kg/h", "stream": "GT-3 Combustor", "req": True},
        {"key": "gt1_comp_p_out", "desc": "Tekanan Keluar Kompresor GT-1", "unit": "bar(a)", "stream": "GT-1 Compressor Out", "req": False},
        {"key": "gt1_exhaust_temp", "desc": "Temperatur Gas Buang GT-1 (Inlet HRSG-1)", "unit": "°C", "stream": "Flue Gas HRSG-1", "req": True},
        {"key": "hrsg1_steam_flow", "desc": "Laju Alir Uap Utama HRSG-1", "unit": "kg/s", "stream": "Main Steam HP", "req": True},
        {"key": "main_steam_p", "desc": "Tekanan Uap Utama HP", "unit": "bar(a)", "stream": "Main Steam HP", "req": True},
        {"key": "main_steam_t", "desc": "Temperatur Uap Utama HP", "unit": "°C", "stream": "Main Steam HP", "req": True},
        {"key": "feedwater_temp_c", "desc": "Temperatur Feedwater Masuk Economizer", "unit": "°C", "stream": "Feedwater", "req": True},
        {"key": "feedwater_pressure_bar", "desc": "Tekanan Feedwater", "unit": "bar(a)", "stream": "Feedwater", "req": True},
        {"key": "condenser_p", "desc": "Tekanan Operasi Kondensor", "unit": "bar(a)", "stream": "Exhaust ST", "req": True},
        {"key": "cw_in_t", "desc": "Temperatur Air Pendingin Masuk Kondensor", "unit": "°C", "stream": "Cooling Water", "req": True},
        {"key": "cw_out_t", "desc": "Temperatur Air Pendingin Keluar Kondensor", "unit": "°C", "stream": "Cooling Water", "req": True},
        {"key": "cw_flow", "desc": "Laju Alir Air Pendingin Kondensor", "unit": "kg/s", "stream": "Cooling Water", "req": False},
    ]

    for item in hysys_parameters:
        var_key = item["key"]
        col_name = tag_mapping.get(var_key) if tag_mapping else None
        if not col_name or col_name not in df.columns:
            for alias in FALLBACK_ALIASES.get(var_key, [var_key]):
                if alias in df.columns:
                    col_name = alias
                    break
        if not col_name:
            col_name = var_key
        
        if col_name in df.columns:
            series = pd.to_numeric(df[col_name], errors="coerce").dropna()
            if not series.empty:
                package_rows.append({
                    "Parameter": item["desc"],
                    "Boundary / Stream HYSYS": item["stream"],
                    "Nilai Representatif (Mean)": round(float(series.mean()), 2),
                    "Median": round(float(series.median()), 2),
                    "Min": round(float(series.min()), 2),
                    "Max": round(float(series.max()), 2),
                    "Satuan": item["unit"],
                    "Sumber Kolom / Tag": col_name,
                    "Kelengkapan Data (%)": round((len(series) / len(df)) * 100.0, 1),
                    "Status / Gap": "Tersedia Lengkap"
                })
            else:
                package_rows.append({
                    "Parameter": item["desc"],
                    "Boundary / Stream HYSYS": item["stream"],
                    "Nilai Representatif (Mean)": "DATA_KOSONG",
                    "Median": "-",
                    "Min": "-",
                    "Max": "-",
                    "Satuan": item["unit"],
                    "Sumber Kolom / Tag": col_name,
                    "Kelengkapan Data (%)": 0.0,
                    "Status / Gap": "Perlu data lab / OEM (Data Gap)"
                })
        else:
            package_rows.append({
                "Parameter": item["desc"],
                "Boundary / Stream HYSYS": item["stream"],
                "Nilai Representatif (Mean)": "NOT_MAPPED",
                "Median": "-",
                "Min": "-",
                "Max": "-",
                "Satuan": item["unit"],
                "Sumber Kolom / Tag": "-",
                "Kelengkapan Data (%)": 0.0,
                "Status / Gap": "Tag DCS Belum Dipetakan" if item["req"] else "Opsional"
            })
            
    return pd.DataFrame(package_rows)
