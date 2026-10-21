"""
Struktur Data dan Model untuk Website Audit Energi PLTGU
Menjamin penelusuran (traceability), metadata, dan transparansi sesuai spesifikasi.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime

@dataclass
class KPIResult:
    """Hasil perhitungan KPI dengan metadata penelusuran lengkap (Halaman 6 & 10)"""
    code: str
    name: str
    value: Optional[float]
    unit: str
    status: str  # VALID, WARNING, NOT_ENOUGH_DATA, INVALID_UNIT, OUT_OF_SCOPE
    status_reason: str = ""
    equipment: str = "Plant"
    boundary: str = "Plant Total"
    formula: str = ""
    formula_version: str = "v1.0.0"
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    sample_count_valid: int = 0
    sample_count_flagged: int = 0
    basis: str = "LHV Gross"
    inputs_used: Dict[str, Any] = field(default_factory=dict)
    assumptions: str = ""
    interpretation_limits: str = ""

@dataclass
class AnomalyFinding:
    """Temuan deteksi anomali AI dan rule-based screening (Halaman 15)"""
    id: str
    timestamp_start: str
    timestamp_end: str
    duration_min: float
    equipment: str
    tags: List[str]
    finding_type: str  # Anomali Proses, Deviasi KPI, Kualitas Data, Kandidat Peluang Optimasi
    actual_value: Optional[float]
    expected_value: Optional[float]
    unit: str
    deviation_pct: Optional[float]
    confidence_severity: str  # Informasi, Perhatian, Anomali Perlu Ditinjau
    confidence_score: float
    hypothesis: str
    recommended_action: str
    review_status: str = "Belum Ditinjau"  # Belum Ditinjau, Dikonfirmasi, False Positive, Perlu Investigasi
    review_notes: str = ""
    data_quality_context: str = "Normal"
    model_version: str = "IsoForest-RuleHybrid-v1.0"
    analyzed_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@dataclass
class QualityReport:
    """Laporan hasil pemeriksaan kualitas data sebelum analisis (Halaman 2 & 7)"""
    total_rows: int = 0
    total_columns: int = 0
    expected_intervals: int = 0
    coverage_pct: float = 0.0
    missing_pct: float = 0.0
    gap_count: int = 0
    duplicate_count: int = 0
    outlier_count: int = 0
    issues: List[Dict[str, Any]] = field(default_factory=list)
    column_stats: Dict[str, Any] = field(default_factory=dict)
