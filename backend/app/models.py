"""
Data Models and Enums for the Cheque Analysis System.
Defines core data structures and constants used throughout the application.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class FileType(Enum):
    """Supported file types for analysis."""

    PAYABLE = ("Payable", "اسناد پرداختنی")
    RECEIVABLE = ("Receivable", "حساب‌های دریافتنی")
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
    CASH_FLOW = ("Cash Flow", "جریان وجوه نقد")
    ACCOUNTS_AGING = ("Accounts Aging", "سنجش سررسید حساب‌ها")
    PROFITABILITY_ANALYSIS = ("Profitability Analysis", "تحلیل سودآوری")
    FORECAST = ("Forecast", "پیش‌بینی مالی")
    INTEGRATED_TREND = ("Integrated Trend", "روند یکپارچه تجاری")

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


class DBPayable(Base):
    """SQLAlchemy model for Payable cheques."""

    __tablename__ = "payables"

    id = Column(Integer, primary_key=True, index=True)
    row_id = Column(Integer)
    document_number = Column(String)
    document_date = Column(String)
    description = Column(String)
    amount = Column(Float)
    due_date = Column(String)
    beneficiary = Column(String)
    account_name = Column(String)
    internal_due_date = Column(String)


class DBReceivable(Base):
    """SQLAlchemy model for Receivable accounts."""

    __tablename__ = "receivables"

    id = Column(Integer, primary_key=True, index=True)
    row_id = Column(Integer)
    document_date = Column(String)
    amount = Column(Float)
    due_date = Column(String)
    internal_due_date = Column(String)
    company_name = Column(String)


class DBInvoice(Base):
    """SQLAlchemy model for Invoices."""

    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    row_id = Column(String)
    invoice_type = Column(String)
    invoice_date = Column(String)
    customer_code = Column(String, index=True)
    customer_name = Column(String)
    order_code = Column(String, index=True)
    account_detail = Column(String)
    subtotal = Column(Float)
    tax = Column(Float)
    total_amount = Column(Float)


class DBPerforma(Base):
    """SQLAlchemy model for Performa."""

    __tablename__ = "performa"

    id = Column(Integer, primary_key=True, index=True)
    row_id = Column(Integer)
    performa_type = Column(String)
    performa_date = Column(String)
    series = Column(String)
    sale_type = Column(String)
    order_code = Column(String, index=True)
    account_detail = Column(String)
    customer_code = Column(String, index=True)
    customer_name = Column(String)
    status = Column(String)
    amount = Column(Float)
    description = Column(String)
