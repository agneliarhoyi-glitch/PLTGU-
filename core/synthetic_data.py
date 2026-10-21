"""
Modul Generator Dataset Sintetis PLTGU Blok 1 (1 Bulan, Interval 5 Menit)
Menghasilkan ~8.640 baris data operasional realistis dengan label jelas 'SINTETIS' (Halaman 1, 5, & 10).
"""

import os
from typing import Optional
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_pltgu_synthetic_data(days: int = 30, interval_min: int = 5, seed: int = 42) -> pd.DataFrame:
    """
    Menghasilkan dataset deret waktu realistis untuk 3 GT, 3 HRSG, 1 ST, Condenser, dan Aux.
    Disertai variasi siklus siang-malam ambient, transien beban, dan deviasi halus untuk pengujian AI.
    """
    np.random.seed(seed)
    start_time = datetime(2026, 10, 1, 0, 0, 0)
    total_minutes = days * 24 * 60
    num_points = int(total_minutes / interval_min)
    
    timestamps = [start_time + timedelta(minutes=i * interval_min) for i in range(num_points)]
    
    # 1. Variasi Lingkungan (Ambient) Siang-Malam
    hours = np.array([ts.hour + ts.minute / 60.0 for ts in timestamps])
    # Temperatur terendah jam 05:00 (~25 C), tertinggi jam 14:00 (~33 C)
    ambient_temp = 28.5 + 4.0 * np.sin((hours - 9.0) * (2 * np.pi / 24.0)) + np.random.normal(0, 0.3, num_points)
    ambient_press = 1.013 + np.random.normal(0, 0.002, num_points)
    
    # 2. Status Operasi & Profil Beban PLTGU (Pola Dispatch Siang Beban Penuh, Malam Sebagian)
    base_load_profile = 0.88 + 0.10 * np.sin((hours - 8.0) * (2 * np.pi / 24.0))  # 78% - 98%
    
    # 3. Gas Turbine 1, 2, 3
    # Kapasitas desain per GT: 105 MW gross
    gt1_mw = (105.0 * base_load_profile) - (ambient_temp - 25.0) * 0.45 + np.random.normal(0, 0.4, num_points)
    gt2_mw = (103.0 * base_load_profile) - (ambient_temp - 25.0) * 0.45 + np.random.normal(0, 0.4, num_points)
    gt3_mw = (104.0 * base_load_profile) - (ambient_temp - 25.0) * 0.45 + np.random.normal(0, 0.4, num_points)
    
    # Simulasikan kejadian operasional:
    # Hari ke-10: Startup GT-3 setelah inspeksi singkat (jam 02:00 - 05:00)
    for i, ts in enumerate(timestamps):
        if ts.day == 10 and 2 <= ts.hour < 5:
            gt3_mw[i] = max(0.0, 35.0 * (ts.hour - 2 + ts.minute / 60.0) / 3.0)
            
    # Simulasikan anomali halus untuk pengujian AI:
    # Mulai hari ke-20, GT-2 mengalami kenaikan exhaust temp dan sedikit penurunan PR kompresor (indikasi fouling kompresor)
    gt2_fouling_factor = np.zeros(num_points)
    for i, ts in enumerate(timestamps):
        if ts.day >= 20:
            gt2_fouling_factor[i] = min(0.06, (ts.day - 20) * 0.006)
            
    # Gas Fuel Flow (LHV basis 49.500 kJ/kg, efisiensi turbin gas ~36%)
    lhv_kj_kg = 49500.0
    gt1_fuel_kg_s = (gt1_mw * 1000.0) / (lhv_kj_kg * 0.365) + np.random.normal(0, 0.03, num_points)
    gt2_fuel_kg_s = (gt2_mw * 1000.0) / (lhv_kj_kg * (0.362 - gt2_fouling_factor * 0.02)) + np.random.normal(0, 0.03, num_points)
    gt3_fuel_kg_s = (gt3_mw * 1000.0) / (lhv_kj_kg * 0.364) + np.random.normal(0, 0.03, num_points)
    
    # Compressor Parameters
    gt1_pr = 14.8 - (ambient_temp - 25.0) * 0.05 + np.random.normal(0, 0.04, num_points)
    gt2_pr = 14.7 - (ambient_temp - 25.0) * 0.05 - (gt2_fouling_factor * 0.8) + np.random.normal(0, 0.04, num_points)
    gt3_pr = 14.8 - (ambient_temp - 25.0) * 0.05 + np.random.normal(0, 0.04, num_points)
    
    gt1_p_out_bar = ambient_press * gt1_pr
    gt2_p_out_bar = ambient_press * gt2_pr
    gt3_p_out_bar = ambient_press * gt3_pr
    
    gt1_exhaust_temp = 540.0 + (105.0 - gt1_mw) * 0.3 + np.random.normal(0, 1.2, num_points)
    gt2_exhaust_temp = 542.0 + (103.0 - gt2_mw) * 0.3 + (gt2_fouling_factor * 25.0) + np.random.normal(0, 1.2, num_points)
    gt3_exhaust_temp = 541.0 + (104.0 - gt3_mw) * 0.3 + np.random.normal(0, 1.2, num_points)

    # 4. HRSG 1, 2, 3
    # Laju uap utama ~38-42 kg/s per HRSG
    hrsg1_steam_flow = gt1_mw * 0.40 + np.random.normal(0, 0.2, num_points)
    hrsg2_steam_flow = gt2_mw * 0.395 + np.random.normal(0, 0.2, num_points)
    hrsg3_steam_flow = gt3_mw * 0.40 + np.random.normal(0, 0.2, num_points)
    
    hrsg1_stack_temp = 98.0 + (ambient_temp - 25.0) * 0.3 + np.random.normal(0, 0.5, num_points)
    hrsg2_stack_temp = 99.0 + (ambient_temp - 25.0) * 0.3 + np.random.normal(0, 0.5, num_points)
    hrsg3_stack_temp = 98.5 + (ambient_temp - 25.0) * 0.3 + np.random.normal(0, 0.5, num_points)
    
    hrsg_main_steam_p = 68.0 + np.random.normal(0, 0.3, num_points)
    hrsg_main_steam_t = 515.0 + np.random.normal(0, 1.0, num_points)
    
    # Feedwater
    hrsg1_fw_flow = hrsg1_steam_flow * 1.015 + np.random.normal(0, 0.1, num_points)  # 1.5% blowdown
    hrsg2_fw_flow = hrsg2_steam_flow * 1.015 + np.random.normal(0, 0.1, num_points)
    hrsg3_fw_flow = hrsg3_steam_flow * 1.015 + np.random.normal(0, 0.1, num_points)
    fw_temp = 125.0 + np.random.normal(0, 0.5, num_points)
    fw_press = 78.0 + np.random.normal(0, 0.4, num_points)

    # 5. Steam Turbine (ST)
    st_total_steam_flow = hrsg1_steam_flow + hrsg2_steam_flow + hrsg3_steam_flow
    st_mw = (st_total_steam_flow * 1.05) - 2.0 + np.random.normal(0, 0.5, num_points)
    
    # 6. Condenser & Cooling Water
    condenser_press = 0.075 + (ambient_temp - 25.0) * 0.002 + np.random.normal(0, 0.001, num_points)
    cw_inlet_t = ambient_temp - 2.0 + np.random.normal(0, 0.2, num_points)
    cw_flow_kg_s = 7800.0 + np.random.normal(0, 20.0, num_points)
    cw_outlet_t = cw_inlet_t + ((st_mw * 1000.0 * 1.4) / (cw_flow_kg_s * 4.184)) + np.random.normal(0, 0.15, num_points)
    hotwell_temp = cw_outlet_t + 2.5 + np.random.normal(0, 0.2, num_points)

    # 7. Daya Total PLTGU & Auxiliary
    pltgu_gross_mw = gt1_mw + gt2_mw + gt3_mw + st_mw
    pltgu_aux_mw = 4.0 + (pltgu_gross_mw * 0.024) + np.random.normal(0, 0.1, num_points)
    pltgu_net_mw = pltgu_gross_mw - pltgu_aux_mw

    # Satuan kg/h untuk fuel flow (konversi standar)
    gt1_fuel_kg_h = gt1_fuel_kg_s * 3600.0
    gt2_fuel_kg_h = gt2_fuel_kg_s * 3600.0
    gt3_fuel_kg_h = gt3_fuel_kg_s * 3600.0
    total_fuel_kg_h = gt1_fuel_kg_h + gt2_fuel_kg_h + gt3_fuel_kg_h

    # Kumpulkan DataFrame
    df = pd.DataFrame({
        "timestamp": [ts.strftime("%Y-%m-%d %H:%M:%S") for ts in timestamps],
        "data_source_label": ["SINTETIS"] * num_points,
        "ambient_temp_c": np.round(ambient_temp, 2),
        "ambient_press_bar": np.round(ambient_press, 4),
        "fuel_lhv_kj_kg": [lhv_kj_kg] * num_points,
        
        # GT-1
        "gt1_gross_mw": np.round(gt1_mw, 2),
        "gt1_fuel_flow_kg_s": np.round(gt1_fuel_kg_s, 3),
        "gt1_fuel_flow_kg_h": np.round(gt1_fuel_kg_h, 1),
        "gt1_comp_p_in_bar": np.round(ambient_press, 4),
        "gt1_comp_p_out_bar": np.round(gt1_p_out_bar, 2),
        "gt1_comp_pr": np.round(gt1_pr, 2),
        "gt1_exhaust_temp_c": np.round(gt1_exhaust_temp, 1),
        
        # GT-2
        "gt2_gross_mw": np.round(gt2_mw, 2),
        "gt2_fuel_flow_kg_s": np.round(gt2_fuel_kg_s, 3),
        "gt2_fuel_flow_kg_h": np.round(gt2_fuel_kg_h, 1),
        "gt2_comp_p_in_bar": np.round(ambient_press, 4),
        "gt2_comp_p_out_bar": np.round(gt2_p_out_bar, 2),
        "gt2_comp_pr": np.round(gt2_pr, 2),
        "gt2_exhaust_temp_c": np.round(gt2_exhaust_temp, 1),
        
        # GT-3
        "gt3_gross_mw": np.round(gt3_mw, 2),
        "gt3_fuel_flow_kg_s": np.round(gt3_fuel_kg_s, 3),
        "gt3_fuel_flow_kg_h": np.round(gt3_fuel_kg_h, 1),
        "gt3_comp_p_in_bar": np.round(ambient_press, 4),
        "gt3_comp_p_out_bar": np.round(gt3_p_out_bar, 2),
        "gt3_comp_pr": np.round(gt3_pr, 2),
        "gt3_exhaust_temp_c": np.round(gt3_exhaust_temp, 1),
        
        # HRSG 1, 2, 3
        "hrsg1_main_steam_flow_kg_s": np.round(hrsg1_steam_flow, 2),
        "hrsg1_stack_temp_c": np.round(hrsg1_stack_temp, 1),
        "hrsg1_feedwater_flow_kg_s": np.round(hrsg1_fw_flow, 2),
        
        "hrsg2_main_steam_flow_kg_s": np.round(hrsg2_steam_flow, 2),
        "hrsg2_stack_temp_c": np.round(hrsg2_stack_temp, 1),
        "hrsg2_feedwater_flow_kg_s": np.round(hrsg2_fw_flow, 2),
        
        "hrsg3_main_steam_flow_kg_s": np.round(hrsg3_steam_flow, 2),
        "hrsg3_stack_temp_c": np.round(hrsg3_stack_temp, 1),
        "hrsg3_feedwater_flow_kg_s": np.round(hrsg3_fw_flow, 2),
        
        "main_steam_pressure_bar": np.round(hrsg_main_steam_p, 2),
        "main_steam_temp_c": np.round(hrsg_main_steam_t, 1),
        "feedwater_temp_c": np.round(fw_temp, 1),
        "feedwater_pressure_bar": np.round(fw_press, 2),
        
        # Steam Turbine
        "st_gross_mw": np.round(st_mw, 2),
        "st_inlet_steam_flow_kg_s": np.round(st_total_steam_flow, 2),
        
        # Condenser & CW
        "condenser_pressure_bar": np.round(condenser_press, 4),
        "cw_inlet_temp_c": np.round(cw_inlet_t, 2),
        "cw_outlet_temp_c": np.round(cw_outlet_t, 2),
        "cw_flow_kg_s": np.round(cw_flow_kg_s, 1),
        "hotwell_temp_c": np.round(hotwell_temp, 2),
        
        # Plant Totals
        "plant_total_fuel_kg_h": np.round(total_fuel_kg_h, 1),
        "plant_gross_mw": np.round(pltgu_gross_mw, 2),
        "plant_aux_power_mw": np.round(pltgu_aux_mw, 2),
        "plant_net_power_mw": np.round(pltgu_net_mw, 2),
        "operating_status": ["NORMAL" if (ts.day != 10 or ts.hour >= 5) else "STARTUP" for ts in timestamps]
    })
    
    return df

def save_default_synthetic_dataset(output_path: str = "data/demo/data_pltgu_sintetis_1bulan.csv") -> str:
    """Menyimpan dataset sintetis ke folder demo jika belum ada."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if not os.path.exists(output_path):
        df = generate_pltgu_synthetic_data(days=30, interval_min=5)
        df.to_csv(output_path, index=False)
    return output_path
