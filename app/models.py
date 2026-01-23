"""
Data Models and Enums for the Cheque Analysis System.
Defines core data structures and constants used throughout the application.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


class FileType(Enum):
    """Supported file types for analysis."""

    PAYABLE = ("Payable", "اسناد پرداختنی")
    INVOICES = ("Invoices", "فاکتورهای فروش")
    PERFORMA = ("Performa", "پیش‌فاکتورها")

    @property
    def label(self):
        return self.value[1]

    @property
    def id(self):
        return self.value[0]


class AnalysisType(Enum):
    """Types of analysis available."""

    DAILY_BREAKDOWN = ("Daily Breakdown", "تجزیه و تحلیل روزانه")
    CUMULATIVE = ("Cumulative", "تحلیل انباشته")
    TOP_BENEFICIARIES = ("Top Beneficiaries", "ذینفعان برتر")
    SUMMARY_STATS = ("Summary Statistics", "آمار خلاصه")
    ON_TIME_PAYMENT = ("On-time Payment", "پرداخت به موقع")
    CUSTOMER_LOYALTY = ("Customer Loyalty", "وفاداری مشتریان")
    ADVANCED_REPORT = ("Advanced Report", "گزارش مدیریتی پیشرفته")

    @property
    def label(self):
        return self.value[1]

    @property
    def id(self):
        return self.value[0]


@dataclass
class FileConfig:
    """Configuration for a specific file type."""

    file_type: FileType
    filepath: str
    sheet_index: int = 0
    header_row: int = 1
    description: str = ""
    required_columns: List[str] = None

    def __post_init__(self):
        if self.required_columns is None:
            self.required_columns = []


@dataclass
class AnalysisResult:
    """Result of data analysis."""

    file_type: FileType
    analysis_type: AnalysisType
    data: dict
    timestamp: datetime
    cache_key: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return {
            "file_type": self.file_type.value,
            "analysis_type": self.analysis_type.value,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "cache_key": self.cache_key,
        }
