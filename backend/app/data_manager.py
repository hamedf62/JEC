"""
Data Manager for handling Excel file operations.
Manages loading, parsing, and caching of Excel data.
"""

import logging
from typing import Optional, Dict, Tuple, List
from pathlib import Path
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session

from app.models import (
    FileType,
    FileConfig,
    DBPayable,
    DBReceivable,
    DBInvoice,
    DBPerforma,
)
from app.cache import CacheManager
from app.database import SessionLocal

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[1]
CSV_DIR = BASE_DIR / "data" / "csv"


class DataManager:
    """Manages data loading and preprocessing from SQLite database."""

    # Configuration for each file type
    FILE_CONFIGS = {
        FileType.PAYABLE: FileConfig(
            file_type=FileType.PAYABLE,
            filepath=str(CSV_DIR / "payable.csv"),
            description="Payable Cheques Analysis",
            required_columns=["amount", "due_date"],
        ),
        FileType.RECEIVABLE: FileConfig(
            file_type=FileType.RECEIVABLE,
            filepath=str(CSV_DIR / "receivable.csv"),
            description="Accounts Receivable Analysis",
            required_columns=["amount", "due_date"],
        ),
        FileType.INVOICES: FileConfig(
            file_type=FileType.INVOICES,
            filepath=str(CSV_DIR / "invoices.csv"),
            description="Invoices Analysis",
            required_columns=["total_amount", "invoice_date"],
        ),
        FileType.PERFORMA: FileConfig(
            file_type=FileType.PERFORMA,
            filepath=str(CSV_DIR / "performa.csv"),
            description="Performa Analysis",
            required_columns=["amount", "performa_date"],
        ),
    }

    # Mapping FileType to DB Models
    MODEL_MAP = {
        FileType.PAYABLE: DBPayable,
        FileType.RECEIVABLE: DBReceivable,
        FileType.INVOICES: DBInvoice,
        FileType.PERFORMA: DBPerforma,
    }

    def __init__(self, cache_manager: Optional[CacheManager] = None):
        """
        Initialize DataManager.

        Args:
            cache_manager: Optional cache manager instance
        """
        self.cache_manager = cache_manager or CacheManager()
        self._loaded_data: Dict[FileType, pd.DataFrame] = {}

    def load_file(
        self, file_type: FileType, force_reload: bool = False
    ) -> Optional[pd.DataFrame]:
        """
        Load data from SQLite database with caching.

        Args:
            file_type: Type of data to load
            force_reload: Force reload even if cached

        Returns:
            DataFrame or None if failed
        """
        # Check cache
        cache_key = f"db_data:{file_type.id}"
        if not force_reload:
            cached = self.cache_manager.get(cache_key)
            if cached is not None:
                logger.info(f"Loaded {file_type.id} from cache")
                df = pd.DataFrame(cached)
                self._loaded_data[file_type] = df
                return df

        # Load from DB
        model = self.MODEL_MAP.get(file_type)
        if not model:
            logger.error(f"No model mapping for {file_type}")
            return None

        db = SessionLocal()
        try:
            logger.info(f"READING FROM SQLITE DB: {file_type.id}")
            query = db.query(model)
            df = pd.read_sql(query.statement, db.bind)

            if df.empty:
                logger.warning(f"No data found in DB for {file_type.id}")
                return None

            # Remove SQLAlchemy internal state if any (though read_sql usually doesn't have it)
            if "_sa_instance_state" in df.columns:
                df = df.drop("_sa_instance_state", axis=1)

            logger.info(
                f"Loaded {file_type.id} from DB: {len(df)} rows, {len(df.columns)} columns"
            )

            # Cache the data
            self.cache_manager.set(cache_key, df.to_dict("records"))
            self._loaded_data[file_type] = df

            return df
        except Exception as e:
            logger.error(f"Error loading {file_type.value} from DB: {e}")
            return None
        finally:
            db.close()

    def load_all_files(
        self, force_reload: bool = False
    ) -> Dict[FileType, pd.DataFrame]:
        """
        Load all available files.

        Args:
            force_reload: Force reload even if cached

        Returns:
            Dictionary of file types to DataFrames
        """
        results = {}
        for file_type in FileType:
            df = self.load_file(file_type, force_reload)
            if df is not None:
                results[file_type] = df
        return results

    def get_file_info(self, file_type: FileType) -> Optional[Dict]:
        """
        Get information about loaded file.

        Args:
            file_type: Type of file

        Returns:
            File information dictionary
        """
        if file_type not in self._loaded_data:
            df = self.load_file(file_type)
            if df is None:
                return None
        else:
            df = self._loaded_data[file_type]

        config = self.FILE_CONFIGS[file_type]
        return {
            "file_type": file_type.id,
            "description": config.description,
            "filepath": config.filepath,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
            "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024**2,
            "loaded_at": datetime.now().isoformat(),
        }

    def get_dataframe(
        self, file_type: FileType, force_reload: bool = False
    ) -> Optional[pd.DataFrame]:
        """
        Get DataFrame for file type.

        Args:
            file_type: Type of file
            force_reload: Force reload

        Returns:
            DataFrame or None
        """
        if file_type in self._loaded_data and not force_reload:
            return self._loaded_data[file_type]
        return self.load_file(file_type, force_reload)

    def get_all_dataframes(self) -> Dict[FileType, pd.DataFrame]:
        """Get all loaded DataFrames."""
        return self._loaded_data.copy()

    def clear_cache(self, file_type: Optional[FileType] = None) -> bool:
        """
        Clear cache for file(s).

        Args:
            file_type: Specific file type to clear, or None for all

        Returns:
            True if successful
        """
        if file_type:
            cache_key = f"file_data:{file_type.id}"
            return self.cache_manager.delete(cache_key)
        else:
            return self.cache_manager.clear()
