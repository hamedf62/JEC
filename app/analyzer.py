"""
Data Analyzer for performing various analyses on loaded data.
Provides comprehensive analysis methods for each file type.
"""

import logging
from typing import Optional, Dict, List
from datetime import datetime
import pandas as pd
import numpy as np
import jdatetime

from app.models import FileType, AnalysisType, AnalysisResult
from app.cache import CacheManager
from app.data_manager import DataManager

logger = logging.getLogger(__name__)


class DataAnalyzer:
    """Performs analysis on Excel data."""

    def __init__(
        self, data_manager: DataManager, cache_manager: Optional[CacheManager] = None
    ):
        """
        Initialize analyzer.

        Args:
            data_manager: DataManager instance
            cache_manager: Optional cache manager
        """
        self.data_manager = data_manager
        self.cache_manager = cache_manager or CacheManager()

    def _jalali_to_gregorian(self, jalali_str: str) -> Optional:
        """Convert Jalali date string to Gregorian datetime."""
        if pd.isna(jalali_str) or not jalali_str:
            return None
        try:
            # Handle string date formats like "1404/01/18"
            if isinstance(jalali_str, str):
                parts = jalali_str.strip().split("/")
                if len(parts) == 3:
                    jy, jm, jd = int(parts[0]), int(parts[1]), int(parts[2])
                    j_date = jdatetime.date(jy, jm, jd)
                    return j_date.togregorian()
            return None
        except Exception:
            return None

    def _to_jalali(self, date_obj) -> str:
        """Convert Gregorian date to Jalali string."""
        if pd.isna(date_obj):
            return ""
        try:
            # Handle both datetime and date objects
            if hasattr(date_obj, "date"):
                date_val = date_obj.date()
            else:
                date_val = date_obj
            return jdatetime.date.fromgregorian(date=date_val).strftime("%Y/%m/%d")
        except Exception:
            return str(date_obj)

    def analyze(
        self, file_type: FileType, analysis_type: AnalysisType, **kwargs
    ) -> Optional[AnalysisResult]:
        """
        Perform analysis on file.

        Args:
            file_type: Type of file to analyze
            analysis_type: Type of analysis
            **kwargs: Additional parameters

        Returns:
            AnalysisResult or None if failed
        """
        # Generate cache key
        cache_key = self.cache_manager.get_cache_key(
            f"analysis:{file_type.id}:{analysis_type.id}", **kwargs
        )

        # Check cache
        cached = self.cache_manager.get(cache_key)
        if cached:
            logger.info(f"Loaded analysis from cache: {cache_key}")
            return AnalysisResult(
                file_type=file_type,
                analysis_type=analysis_type,
                data=cached,
                timestamp=datetime.now(),
                cache_key=cache_key,
            )

        # Load data
        df = self.data_manager.get_dataframe(file_type)
        if df is None or df.empty:
            if analysis_type not in [
                AnalysisType.ON_TIME_PAYMENT,
                AnalysisType.ADVANCED_REPORT,
            ]:
                logger.error(f"No data available for {file_type.id}")
                return None

        # Perform analysis based on type
        if analysis_type == AnalysisType.DAILY_BREAKDOWN:
            result_data = self._analyze_daily_breakdown(file_type, df, **kwargs)
        elif analysis_type == AnalysisType.CUMULATIVE:
            result_data = self._analyze_cumulative(file_type, df, **kwargs)
        elif analysis_type == AnalysisType.TOP_BENEFICIARIES:
            result_data = self._analyze_top_beneficiaries(file_type, df, **kwargs)
        elif analysis_type == AnalysisType.SUMMARY_STATS:
            result_data = self._analyze_summary_stats(file_type, df, **kwargs)
        elif analysis_type == AnalysisType.ON_TIME_PAYMENT:
            result_data = self._analyze_on_time_payment(**kwargs)
        elif analysis_type == AnalysisType.CUSTOMER_LOYALTY:
            result_data = self._analyze_customer_loyalty(file_type, df, **kwargs)
        elif analysis_type == AnalysisType.ADVANCED_REPORT:
            result_data = self._analyze_advanced_report(**kwargs)
        else:
            logger.warning(f"Unknown analysis type: {analysis_type}")
            return None

        if result_data is None:
            return None

        # Cache result
        self.cache_manager.set(cache_key, result_data)

        return AnalysisResult(
            file_type=file_type,
            analysis_type=analysis_type,
            data=result_data,
            timestamp=datetime.now(),
            cache_key=cache_key,
        )

    def _analyze_daily_breakdown(
        self, file_type: FileType, df: pd.DataFrame, **kwargs
    ) -> Optional[Dict]:
        """Analyze daily breakdown."""
        try:
            if df.empty:
                return {"error": "No data available"}

            # Find numeric columns (excluding row numbers)
            numeric_cols = [
                col
                for col in df.select_dtypes(include=[np.number]).columns
                if col not in ["ردیف", "Unnamed: 0"]
            ]
            if not numeric_cols:
                return {"columns": list(df.columns), "rows": len(df)}

            # Find date columns (look for text columns with date-like patterns)
            date_cols = []
            for col in df.columns:
                if df[col].dtype == "object":
                    # Check if column contains date patterns (e.g., "1404/01/18")
                    sample = df[col].dropna().astype(str).head(5)
                    if sample.str.contains(r"\d{4}/\d{1,2}/\d{1,2}", regex=True).any():
                        date_cols.append(col)

            result = {
                "file_type": file_type.id,
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "numeric_columns": numeric_cols,
                "date_columns": date_cols,
                "sample_data": df.head(5).to_dict("records"),
            }

            # If there's a date column and numeric column, create daily breakdown
            if date_cols and numeric_cols:
                date_col = date_cols[0]
                amount_col = numeric_cols[0]

                # Create a copy and parse dates
                df_copy = df[[date_col, amount_col]].copy()
                df_copy["gregorian_date"] = df_copy[date_col].apply(
                    self._jalali_to_gregorian
                )
                df_copy["gregorian_date"] = pd.to_datetime(
                    df_copy["gregorian_date"], errors="coerce"
                )

                # Filter out rows with invalid dates or amounts
                df_copy = df_copy.dropna(
                    subset=["gregorian_date", amount_col], how="any"
                )

                if len(df_copy) > 0:
                    # Convert amount to numeric if it's string
                    if df_copy[amount_col].dtype == "object":
                        df_copy[amount_col] = pd.to_numeric(
                            df_copy[amount_col], errors="coerce"
                        )
                        df_copy = df_copy.dropna(subset=[amount_col])

                    if len(df_copy) > 0:
                        # Group by date
                        daily = df_copy.groupby(df_copy["gregorian_date"].dt.date)[
                            amount_col
                        ].agg(["sum", "count", "mean"])
                        daily = daily.reset_index()
                        daily.columns = ["date", "sum", "count", "mean"]
                        daily["jalali_date"] = daily["date"].apply(self._to_jalali)
                        result["daily_breakdown"] = daily.to_dict("records")

            return result
        except Exception as e:
            logger.error(f"Error in daily breakdown analysis: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return None

    def _analyze_cumulative(
        self, file_type: FileType, df: pd.DataFrame, **kwargs
    ) -> Optional[Dict]:
        """Analyze cumulative trends."""
        try:
            if df.empty:
                return {"error": "No data available"}

            numeric_cols = [
                col
                for col in df.select_dtypes(include=[np.number]).columns
                if col not in ["ردیف", "Unnamed: 0"]
            ]

            # Find date columns
            date_cols = []
            for col in df.columns:
                if df[col].dtype == "object":
                    sample = df[col].dropna().astype(str).head(5)
                    if sample.str.contains(r"\d{4}/\d{1,2}/\d{1,2}", regex=True).any():
                        date_cols.append(col)

            result = {
                "file_type": file_type.id,
                "total_sum": 0,
                "total_mean": 0,
            }

            if numeric_cols:
                # Try to convert to numeric
                numeric_data = df[numeric_cols[0]].copy()
                if numeric_data.dtype == "object":
                    numeric_data = pd.to_numeric(numeric_data, errors="coerce")

                numeric_data = numeric_data.dropna()
                if len(numeric_data) > 0:
                    result["total_sum"] = float(numeric_data.sum())
                    result["total_mean"] = float(numeric_data.mean())

            if numeric_cols and date_cols:
                date_col = date_cols[0]
                amount_col = numeric_cols[0]

                df_copy = df[[date_col, amount_col]].copy()
                df_copy["gregorian_date"] = df_copy[date_col].apply(
                    self._jalali_to_gregorian
                )
                df_copy["gregorian_date"] = pd.to_datetime(
                    df_copy["gregorian_date"], errors="coerce"
                )

                # Convert amount to numeric
                if df_copy[amount_col].dtype == "object":
                    df_copy[amount_col] = pd.to_numeric(
                        df_copy[amount_col], errors="coerce"
                    )

                df_copy = df_copy.dropna(
                    subset=["gregorian_date", amount_col], how="any"
                )

                if len(df_copy) > 0:
                    df_sorted = df_copy.sort_values("gregorian_date").copy()
                    df_sorted["jalali_date"] = df_sorted["gregorian_date"].apply(
                        self._to_jalali
                    )
                    df_sorted["cumulative"] = df_sorted[amount_col].cumsum()

                    result["cumulative_data"] = df_sorted[
                        ["gregorian_date", "jalali_date", amount_col, "cumulative"]
                    ].to_dict("records")

            return result
        except Exception as e:
            logger.error(f"Error in cumulative analysis: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return None

    def _analyze_top_beneficiaries(
        self, file_type: FileType, df: pd.DataFrame, top_n: int = 10, **kwargs
    ) -> Optional[Dict]:
        """Analyze top beneficiaries/categories."""
        try:
            if df.empty:
                return {"error": "No data available"}

            numeric_cols = [
                col
                for col in df.select_dtypes(include=[np.number]).columns
                if col not in ["ردیف", "Unnamed: 0"]
            ]
            string_cols = [
                col
                for col in df.select_dtypes(include=["object"]).columns
                if col not in ["تاریخ", "تاریخ سررسید", "شرح عملیات"]
            ]

            result = {"file_type": file_type.id, "top_n": top_n, "beneficiaries": []}

            if string_cols and numeric_cols:
                # Use first string column as beneficiary and first numeric as amount
                beneficiary_col = string_cols[0]
                amount_col = numeric_cols[0]

                df_copy = df[[beneficiary_col, amount_col]].copy()

                # Convert amount to numeric if it's string
                if df_copy[amount_col].dtype == "object":
                    df_copy[amount_col] = pd.to_numeric(
                        df_copy[amount_col], errors="coerce"
                    )

                df_copy = df_copy.dropna(subset=[amount_col])

                if len(df_copy) > 0:
                    top_data = (
                        df_copy.groupby(beneficiary_col)[amount_col]
                        .agg(["sum", "count", "mean"])
                        .sort_values("sum", ascending=False)
                        .head(top_n)
                        .reset_index()
                    )

                    result["beneficiaries"] = top_data.to_dict("records")

            return result
        except Exception as e:
            logger.error(f"Error in top beneficiaries analysis: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return None

    def _analyze_summary_stats(
        self, file_type: FileType, df: pd.DataFrame, **kwargs
    ) -> Optional[Dict]:
        """Generate summary statistics."""
        try:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

            result = {
                "file_type": file_type.id,
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "memory_usage_mb": float(df.memory_usage(deep=True).sum() / 1024**2),
                "null_values": df.isnull().sum().to_dict(),
            }

            if numeric_cols:
                stats = df[numeric_cols].describe().to_dict()
                result["numeric_statistics"] = stats

            return result
        except Exception as e:
            logger.error(f"Error in summary statistics: {e}")
            return None

    def get_all_analyses(self, file_type: FileType) -> Dict[str, AnalysisResult]:
        """
        Perform all analyses for a file type.

        Args:
            file_type: Type of file

        Returns:
            Dictionary of analysis results
        """
        results = {}
        for analysis_type in AnalysisType:
            # Skip cross-file analyses in single file context
            if analysis_type in [
                AnalysisType.ON_TIME_PAYMENT,
                AnalysisType.ADVANCED_REPORT,
            ]:
                continue
            result = self.analyze(file_type, analysis_type)
            if result:
                results[analysis_type.id] = result
        return results

    def _analyze_on_time_payment(self, **kwargs) -> Optional[Dict]:
        """Analyze if performa was paid (converted to invoice) on time."""
        try:
            df_performa = self.data_manager.get_dataframe(FileType.PERFORMA)
            df_invoices = self.data_manager.get_dataframe(FileType.INVOICES)

            if df_performa is None or df_invoices is None:
                return {"error": "Missing data for analysis"}

            # Join on OC
            joined = pd.merge(
                df_performa[["OC", "تاریخ", "نام مشتری", "جمع بهای برگه"]],
                df_invoices[["OC", "تاریخ", "جمع بهای کالاها و خدمات "]],
                on="OC",
                how="left",
                suffixes=("_performa", "_invoice"),
            )

            # Convert dates
            joined["date_performa"] = joined["تاریخ_performa"].apply(
                self._jalali_to_gregorian
            )
            joined["date_invoice"] = joined["تاریخ_invoice"].apply(
                self._jalali_to_gregorian
            )

            joined["date_performa"] = pd.to_datetime(joined["date_performa"])
            joined["date_invoice"] = pd.to_datetime(joined["date_invoice"])

            # Calculate gap
            joined["gap_days"] = (
                joined["date_invoice"] - joined["date_performa"]
            ).dt.days

            # Paid status
            joined["is_paid"] = joined["date_invoice"].notna()

            # On-time: assume within 7 days is on-time
            joined["is_on_time"] = joined["gap_days"] <= 7

            return {
                "total_performa": len(df_performa),
                "total_paid": int(joined["is_paid"].sum()),
                "total_on_time": int(joined["is_on_time"].sum()),
                "on_time_rate": (
                    float(joined["is_on_time"].mean()) if len(joined) > 0 else 0
                ),
                "average_gap_days": float(joined["gap_days"].mean()),
                "payment_details": joined[
                    ["OC", "نام مشتری", "gap_days", "is_paid", "is_on_time"]
                ].to_dict("records"),
            }
        except Exception as e:
            logger.error(f"Error in on-time payment analysis: {e}")
            return None

    def _analyze_customer_loyalty(
        self, file_type: FileType, df: pd.DataFrame, **kwargs
    ) -> Optional[Dict]:
        """Analyze customer loyalty based on purchase frequency."""
        try:
            if df.empty:
                return {"error": "No data"}

            name_col = "نام مشتری"
            amount_col = (
                "جمع بهای کالاها و خدمات "
                if file_type == FileType.INVOICES
                else "جمع بهای برگه"
            )

            if file_type == FileType.PAYABLE:
                name_col = "نام تفصیلی 1"
                amount_col = "بستانکار"

            if name_col not in df.columns or amount_col not in df.columns:
                return {
                    "error": f"ستون‌های مورد نیاز ({name_col}, {amount_col}) یافت نشدند"
                }

            loyalty = (
                df.groupby(name_col)
                .agg(
                    {
                        amount_col: ["sum", "count", "mean"],
                        "تاریخ": "max",  # Last purchase
                    }
                )
                .reset_index()
            )

            loyalty.columns = [
                "customer_name",
                "total_value",
                "order_count",
                "average_value",
                "last_purchase",
            ]
            loyalty = loyalty.sort_values(by="order_count", ascending=False)

            return {
                "file_type": file_type.id,
                "loyalty_data": loyalty.to_dict("records"),
                "total_customers": len(loyalty),
            }
        except Exception as e:
            logger.error(f"Error in customer loyalty analysis: {e}")
            return None

    def _analyze_advanced_report(self, **kwargs) -> Optional[Dict]:
        """Generate a comprehensive management report."""
        try:
            df_payable = self.data_manager.get_dataframe(FileType.PAYABLE)
            df_invoices = self.data_manager.get_dataframe(FileType.INVOICES)
            df_performa = self.data_manager.get_dataframe(FileType.PERFORMA)

            report = {
                "total_sales": (
                    float(df_invoices["جمع بهای کالاها و خدمات "].sum())
                    if df_invoices is not None
                    else 0
                ),
                "total_payable": (
                    float(df_payable["بستانکار"].sum()) if df_payable is not None else 0
                ),
                "performa_count": len(df_performa) if df_performa is not None else 0,
                "invoice_count": len(df_invoices) if df_invoices is not None else 0,
                "conversion_rate": (
                    (len(df_invoices) / len(df_performa))
                    if (df_performa is not None and len(df_performa) > 0)
                    else 0
                ),
            }

            # Net position (Sales - Payable)
            report["net_position"] = report["total_sales"] - report["total_payable"]

            return report
        except Exception as e:
            logger.error(f"Error in advanced report: {e}")
            return None
