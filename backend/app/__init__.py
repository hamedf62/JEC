"""
Professional Multi-File Data Analysis System.
Demonstrates enterprise-grade Python architecture with classes, caching, and async support.
"""

from app.models import FileType, AnalysisType, FileConfig, AnalysisResult
from app.cache import CacheManager
from app.data_manager import DataManager
from app.analyzer import DataAnalyzer

__version__ = "2.0.0"
__author__ = "Data Analysis Team"

__all__ = [
    "FileType",
    "AnalysisType",
    "FileConfig",
    "AnalysisResult",
    "CacheManager",
    "DataManager",
    "DataAnalyzer",
]
