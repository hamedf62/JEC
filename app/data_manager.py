"""
Data Manager for handling Excel file operations.
Manages loading, parsing, and caching of Excel data.
"""

import logging
from typing import Optional, Dict, Tuple
import pandas as pd
from datetime import datetime

from app.models import FileType, FileConfig
from app.cache import CacheManager

logger = logging.getLogger(__name__)


class DataManager:
    """Manages data loading and preprocessing from Excel files."""

    # Configuration for each file type
    FILE_CONFIGS = {
        FileType.PAYABLE: FileConfig(
            file_type=FileType.PAYABLE,
            filepath="data/Payable.xlsx",
            sheet_index=0,
            header_row=1,
            description="Payable Cheques Analysis",
            required_columns=["بستانکار", "تاریخ سررسید"],
        ),
        FileType.INVOICES: FileConfig(
            file_type=FileType.INVOICES,
            filepath="data/invoices.xlsx",
            sheet_index=0,
            header_row=1,
            description="Invoices Analysis",
            required_columns=[],
        ),
        FileType.PERFORMA: FileConfig(
            file_type=FileType.PERFORMA,
            filepath="data/performa.xlsx",
            sheet_index=0,
            header_row=0,
            description="Performa Analysis",
            required_columns=[],
        ),
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
        Load Excel file with caching.

        Args:
            file_type: Type of file to load
            force_reload: Force reload even if cached

        Returns:
            DataFrame or None if failed
        """
        # Check cache
        cache_key = f"file_data:{file_type.id}"
        if not force_reload:
            cached = self.cache_manager.get(cache_key)
            if cached is not None:
                logger.info(f"Loaded {file_type.id} from cache")
                self._loaded_data[file_type] = pd.DataFrame(cached)
                return self._loaded_data[file_type]

        # Load from file
        config = self.FILE_CONFIGS.get(file_type)
        if not config:
            logger.error(f"No configuration for {file_type}")
            return None

        try:
            # Read with proper header row from config
            df = pd.read_excel(
                config.filepath, sheet_name=config.sheet_index, header=config.header_row
            )

            # Drop the first column if it's unnamed (row numbers)
            if "Unnamed: 0" in df.columns:
                df = df.drop("Unnamed: 0", axis=1)

            # Remove completely empty rows
            df = df.dropna(how="all")

            # Rial to Toman conversion (Rial / 10)
            # Identify columns that likely contain amounts
            amount_cols = [
                "بستانکار",
                "جمع بهای کالاها و خدمات ",
                "جمع بهای برگه",
            ]
            for col in df.columns:
                if col in amount_cols:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0) / 10

            logger.info(
                f"Loaded {file_type.id}: {len(df)} rows, {len(df.columns)} columns"
            )

            # Cache the data
            self.cache_manager.set(cache_key, df.to_dict("records"))
            self._loaded_data[file_type] = df

            return df
        except FileNotFoundError:
            logger.error(f"File not found: {config.filepath}")
            return None
        except Exception as e:
            logger.error(f"Error loading {file_type.value}: {e}")
            return None

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
