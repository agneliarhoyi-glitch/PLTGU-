"""
Modul Validasi Kualitas Data Operasi PLTGU (Halaman 2 & 7)
Mendeteksi missing data, gap waktu, duplikasi timestamp+tag, flatline, dan outlier fisik.
"""

from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np
from core.models import QualityReport

# Batas fisik operasi PLTGU wajar untuk screening outlier
PHYSICAL_BOUNDS = {
    "gt_power_mw": (0.0, 150.0),
    "st_power_mw": (0.0, 200.0),
    "fuel_flow_kg_s": (0.0, 20.0),
    "fuel_flow_kg_h": (0.0, 72000.0),
    "compressor_inlet_t_c": (10.0, 50.0),
    "compressor_outlet_t_c": (250.0, 500.0),
    "compressor_outlet_p_bar": (1.0, 25.0),
    "gt_exhaust_t_c": (400.0, 700.0),
    "hrsg_main_steam_t_c": (300.0, 600.0),
    "hrsg_main_steam_p_bar": (20.0, 150.0),
    "hrsg_stack_t_c": (70.0, 200.0),
    "condenser_pressure_bar": (0.03, 0.25),
    "cw_inlet_t_c": (15.0, 40.0),
    "cw_outlet_t_c": (20.0, 50.0),
}

def analyze_data_quality(df: pd.DataFrame, 
                         timestamp_col: str = "timestamp", 
                         expected_interval_min: Optional[float] = None,
                         tag_mapping: Dict[str, str] = None) -> QualityReport:
    """
    Melakukan pemeriksaan kualitas data menyeluruh tanpa memodifikasi data mentah.
    """
    report = QualityReport()
    report.total_rows = len(df)
    report.total_columns = len(df.columns)
    
    if df.empty:
        report.issues.append({
            "severity": "ANOMALY",
            "type": "Empty Dataset",
            "description": "Dataset tidak memiliki baris data."
        })
        return report

    # 1. Validasi Timestamp
    if timestamp_col not in df.columns:
        report.issues.append({
            "severity": "ANOMALY",
            "type": "Missing Timestamp Column",
            "description": f"Kolom timestamp '{timestamp_col}' tidak ditemukan."
        })
        return report

    ts_series = pd.to_datetime(df[timestamp_col], errors="coerce")
    invalid_ts_count = int(ts_series.isna().sum())
    
    if invalid_ts_count > 0:
        report.issues.append({
            "severity": "ANOMALY",
            "type": "Invalid Timestamps",
            "description": f"Terdapat {invalid_ts_count} baris dengan format timestamp tidak valid.",
            "count": invalid_ts_count
        })

    valid_ts = ts_series.dropna().sort_values()
    if len(valid_ts) > 1:
        t_start = valid_ts.iloc[0]
        t_end = valid_ts.iloc[-1]
        total_span_min = max(0.0, (t_end - t_start).total_seconds() / 60.0)
        
        # Deteksi interval data aktual secara cerdas jika tidak diberikan secara eksplisit
        if expected_interval_min is None or expected_interval_min <= 0:
            diffs_sec = valid_ts.diff().dt.total_seconds().dropna()
            valid_diffs = diffs_sec[(diffs_sec > 0) & (diffs_sec < 7200)]
            if not valid_diffs.empty:
                actual_int_min = float(valid_diffs.median() / 60.0)
                expected_interval_min = actual_int_min if actual_int_min > 0 else 5.0
            else:
                expected_interval_min = 5.0

        expected_points = int(np.floor(total_span_min / max(0.01, expected_interval_min))) + 1
        report.expected_intervals = expected_points
        report.coverage_pct = round(min(100.0, (len(valid_ts) / max(1, expected_points)) * 100.0), 2)
        
        # 2. Cek Gap Waktu
        time_diffs_min = valid_ts.diff().dt.total_seconds() / 60.0
        gap_threshold = expected_interval_min * 1.5
        gaps = time_diffs_min[time_diffs_min > gap_threshold]
        report.gap_count = len(gaps)
        
        if report.gap_count > 0:
            max_gap = gaps.max()
            report.issues.append({
                "severity": "WARNING",
                "type": "Data Time Gap",
                "description": f"Ditemukan {report.gap_count} gap waktu (gap terpanjang: {max_gap:.1f} menit).",
                "count": report.gap_count
            })

    # 3. Cek Duplikasi Timestamp
    duplicate_ts_count = int(df.duplicated(subset=[timestamp_col]).sum())
    report.duplicate_count = duplicate_ts_count
    if duplicate_ts_count > 0:
        report.issues.append({
            "severity": "WARNING",
            "type": "Duplicate Timestamps",
            "description": f"Terdapat {duplicate_ts_count} baris dengan timestamp duplikat.",
            "count": duplicate_ts_count
        })

    # 4. Cek Missing Values per Kolom
    total_cells = report.total_rows * max(1, report.total_columns - 1)
    missing_cells = int(df.drop(columns=[timestamp_col], errors="ignore").isna().sum().sum())
    report.missing_pct = round((missing_cells / max(1, total_cells)) * 100.0, 2)
    
    col_missing = df.isna().sum()
    for col, count in col_missing.items():
        if count > 0 and col != timestamp_col:
            pct = (count / report.total_rows) * 100.0
            report.issues.append({
                "severity": "WARNING" if pct < 20 else "ANOMALY",
                "type": "Missing Values in Column",
                "column": col,
                "description": f"Kolom '{col}' memiliki {count} data kosong ({pct:.1f}%).",
                "count": int(count)
            })

    # 5. Cek Flatline (Sensor stuck pada nilai sama terus-menerus > 12 sampel = 1 jam)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) >= 12:
            rolling_std = series.rolling(window=12).std()
            flatlines = (rolling_std == 0.0) & (series.rolling(window=12).mean() > 0.0)
            flatline_count = int(flatlines.sum())
            if flatline_count > 0:
                report.issues.append({
                    "severity": "WARNING",
                    "type": "Sensor Flatline",
                    "column": col,
                    "description": f"Sensor '{col}' terindikasi flatline/macet selama {flatline_count} interval.",
                    "count": flatline_count
                })

    # 6. Cek Batas Fisik Outlier
    if tag_mapping:
        for var_name, col_name in tag_mapping.items():
            if col_name in df.columns and var_name in PHYSICAL_BOUNDS:
                low, high = PHYSICAL_BOUNDS[var_name]
                series = pd.to_numeric(df[col_name], errors="coerce").dropna()
                outliers = series[(series < low) | (series > high)]
                if len(outliers) > 0:
                    report.outlier_count += len(outliers)
                    report.issues.append({
                        "severity": "WARNING",
                        "type": "Physical Outlier",
                        "column": col_name,
                        "description": f"Kolom '{col_name}' memiliki {len(outliers)} titik di luar batas fisik [{low}, {high}].",
                        "count": len(outliers)
                    })

    return report
