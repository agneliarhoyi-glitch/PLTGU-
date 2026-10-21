"""
Modul AI & Deteksi Anomali Operasi PLTGU (Halaman 13-16)
Menggabungkan Rule-Based Checks, Unsupervised ML (Isolation Forest), Persistence Filter, dan Workflow Review Engineer.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from core.models import AnomalyFinding
from core.config import AI_DISCLAIMER

class AnomalyDetector:
    """Detektor Anomali Multi-layer (Fisik + Statistik + Isolation Forest) dengan Persistence Debounce"""
    
    def __init__(self, contamination: float = 0.03, persistence_window: int = 3):
        self.contamination = contamination
        self.persistence_window = persistence_window  # Minimal N interval berurutan untuk menghindari false spike
        self.model = IsolationForest(contamination=self.contamination, random_state=42)
        self.feature_columns: List[str] = []

    def detect_anomalies(self, 
                         df: pd.DataFrame, 
                         timestamp_col: str, 
                         feature_cols: List[str], 
                         equipment_name: str = "GT-1",
                         tag_labels: Dict[str, str] = None) -> List[AnomalyFinding]:
        """
        Menjalankan deteksi anomali pada fitur-fitur operasi yang valid.
        """
        findings: List[AnomalyFinding] = []
        if df.empty or len(df) < 20 or not feature_cols:
            return findings

        # Filter hanya kolom numerik yang ada di DataFrame
        valid_features = [c for c in feature_cols if c in df.columns]
        if not valid_features:
            return findings
            
        self.feature_columns = valid_features
        clean_df = df.copy().dropna(subset=valid_features)
        if len(clean_df) < 15:
            return findings

        X = clean_df[valid_features].values
        
        # Fit & Predict Isolation Forest
        try:
            self.model.fit(X)
            scores = self.model.decision_function(X)
            preds = self.model.predict(X)  # -1 = anomali, 1 = normal
        except Exception:
            # Fallback jika model gagal
            scores = np.zeros(len(X))
            preds = np.ones(len(X))

        clean_df["_anomaly_score"] = scores
        clean_df["_is_anomaly"] = (preds == -1)

        # Terapkan Persistence Filter (Debounce window)
        # Mengharuskan minimal persistence_window berturut-turut bernilai anomali
        rolling_anomaly = clean_df["_is_anomaly"].rolling(window=self.persistence_window, min_periods=self.persistence_window).sum()
        persisted_anomalies = (rolling_anomaly >= self.persistence_window)
        
        # Ekstrak rentang kejadian (event clustering)
        in_event = False
        event_start_idx = None
        
        timestamps = pd.to_datetime(clean_df[timestamp_col], errors="coerce").values
        
        for idx in range(len(clean_df)):
            is_anom = persisted_anomalies.iloc[idx]
            if is_anom and not in_event:
                in_event = True
                event_start_idx = max(0, idx - self.persistence_window + 1)
            elif not is_anom and in_event:
                in_event = False
                event_end_idx = idx - 1
                
                # Buat objek temuan
                t_start = pd.to_datetime(timestamps[event_start_idx]).strftime("%Y-%m-%d %H:%M")
                t_end = pd.to_datetime(timestamps[event_end_idx]).strftime("%Y-%m-%d %H:%M")
                dur_min = (pd.to_datetime(timestamps[event_end_idx]) - pd.to_datetime(timestamps[event_start_idx])).total_seconds() / 60.0
                
                # Cari fitur mana yang paling menyimpang dari median populasi
                event_slice = clean_df.iloc[event_start_idx:event_end_idx + 1]
                overall_median = clean_df[valid_features].median()
                event_median = event_slice[valid_features].median()
                
                rel_deviations = ((event_median - overall_median) / overall_median.abs().replace(0, 1.0)) * 100.0
                worst_feature = rel_deviations.abs().idxmax()
                dev_val = rel_deviations[worst_feature]
                
                # Severity categorization
                if abs(dev_val) > 15.0 or dur_min >= 60.0:
                    severity = "Anomali Perlu Ditinjau"
                    confidence = 0.88
                elif abs(dev_val) > 8.0:
                    severity = "Perhatian"
                    confidence = 0.75
                else:
                    severity = "Informasi"
                    confidence = 0.60
                    
                label_name = tag_labels.get(worst_feature, worst_feature) if tag_labels else worst_feature
                
                finding = AnomalyFinding(
                    id=f"ANOM-{equipment_name}-{len(findings)+1:03d}",
                    timestamp_start=t_start,
                    timestamp_end=t_end,
                    duration_min=max(dur_min, 5.0),
                    equipment=equipment_name,
                    tags=[worst_feature],
                    finding_type="Anomali Proses",
                    actual_value=round(float(event_median[worst_feature]), 2),
                    expected_value=round(float(overall_median[worst_feature]), 2),
                    unit="engineering unit",
                    deviation_pct=round(float(dev_val), 2),
                    confidence_severity=severity,
                    confidence_score=confidence,
                    hypothesis=f"Terdeteksi pergeseran parameter {label_name} sebesar {dev_val:+.1f}% dari nilai median operasi normal.",
                    recommended_action=f"Verifikasi kalibrasi instrumen {label_name}, periksa filter/katup terkait, dan cross-check dengan kurva performa OEM.",
                    review_status="Belum Ditinjau",
                    review_notes="",
                    model_version="IsolationForest+PersistenceDebounce-v1.0"
                )
                findings.append(finding)
                
        # Tangani jika event masih berlangsung sampai akhir data
        if in_event:
            event_end_idx = len(clean_df) - 1
            t_start = pd.to_datetime(timestamps[event_start_idx]).strftime("%Y-%m-%d %H:%M")
            t_end = pd.to_datetime(timestamps[event_end_idx]).strftime("%Y-%m-%d %H:%M")
            dur_min = (pd.to_datetime(timestamps[event_end_idx]) - pd.to_datetime(timestamps[event_start_idx])).total_seconds() / 60.0
            
            event_slice = clean_df.iloc[event_start_idx:event_end_idx + 1]
            overall_median = clean_df[valid_features].median()
            event_median = event_slice[valid_features].median()
            
            rel_deviations = ((event_median - overall_median) / overall_median.abs().replace(0, 1.0)) * 100.0
            worst_feature = rel_deviations.abs().idxmax()
            dev_val = rel_deviations[worst_feature]
            
            finding = AnomalyFinding(
                id=f"ANOM-{equipment_name}-{len(findings)+1:03d}",
                timestamp_start=t_start,
                timestamp_end=t_end,
                duration_min=max(dur_min, 5.0),
                equipment=equipment_name,
                tags=[worst_feature],
                finding_type="Anomali Proses",
                actual_value=round(float(event_median[worst_feature]), 2),
                expected_value=round(float(overall_median[worst_feature]), 2),
                unit="engineering unit",
                deviation_pct=round(float(dev_val), 2),
                confidence_severity="Perhatian",
                confidence_score=0.80,
                hypothesis=f"Deviasi persisten pada {worst_feature} ({dev_val:+.1f}%) hingga akhir periode pengamatan.",
                recommended_action="Lakukan inspeksi lokal dan validasi transmitter sebelum menyimpulkan degradasi peralatan.",
                review_status="Belum Ditinjau"
            )
            findings.append(finding)
            
        return findings
