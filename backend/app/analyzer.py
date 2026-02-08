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
            # If already a datetime object, return it (or its date)
            if hasattr(jalali_str, "date"):
                return jalali_str.date() if hasattr(jalali_str, "date") else jalali_str

            # Handle string date formats like "1404/01/18"
            if isinstance(jalali_str, str):
                # Remove any time component if present
                date_part = jalali_str.split(" ")[0]
                parts = date_part.strip().split("/")
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

    def _clean_data(self, data):
        """Recursively replace NaN values with None for JSON compliance."""
        if isinstance(data, dict):
            return {k: self._clean_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._clean_data(v) for v in data]
        if pd.isna(data):
            return None
        return data

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
        elif analysis_type == AnalysisType.CASH_FLOW:
            result_data = self._analyze_cash_flow(**kwargs)
        elif analysis_type == AnalysisType.ACCOUNTS_AGING:
            result_data = self._analyze_accounts_aging(**kwargs)
        elif analysis_type == AnalysisType.PROFITABILITY_ANALYSIS:
            result_data = self._analyze_profitability(**kwargs)
        elif analysis_type == AnalysisType.INTEGRATED_TREND:
            result_data = self._analyze_integrated_trend(**kwargs)
        else:
            logger.warning(f"Unknown analysis type: {analysis_type}")
            return None

        if result_data is None:
            return None

        # Clean NaN values
        result_data = self._clean_data(result_data)

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
                if col not in ["row_id", "id", "Unnamed: 0"]
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
                        # Convert date objects to strings for JSON serialization
                        daily["date"] = pd.to_datetime(daily["date"]).dt.strftime(
                            "%Y-%m-%d"
                        )
                        daily["jalali_date"] = daily["date"].apply(
                            lambda x: self._to_jalali(datetime.strptime(x, "%Y-%m-%d"))
                        )
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
                if col not in ["row_id", "id", "Unnamed: 0"]
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
                if col not in ["row_id", "id", "Unnamed: 0"]
            ]
            string_cols = [
                col
                for col in df.select_dtypes(include=["object"]).columns
                if col
                not in [
                    "document_date",
                    "due_date",
                    "description",
                    "invoice_date",
                    "performa_date",
                    "internal_due_date",
                ]
            ]

            result = {"file_type": file_type.id, "top_n": top_n, "beneficiaries": []}

            if string_cols and numeric_cols:
                # Prioritize 'customer_name' or 'beneficiary' or 'company_name'
                beneficiary_col = string_cols[0]
                priority_cols = ["customer_name", "beneficiary", "company_name"]
                for p in priority_cols:
                    if p in string_cols:
                        beneficiary_col = p
                        break

                # Prioritize specific amount columns
                amount_col = numeric_cols[0]
                priority_amounts = ["total_amount", "amount", "subtotal"]
                for p in priority_amounts:
                    if p in numeric_cols:
                        amount_col = p
                        break

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

            # Add total sum for specific amount columns if they exist
            amount_col = None
            if file_type == FileType.INVOICES:
                amount_col = "total_amount"
            elif file_type in [
                FileType.PAYABLE,
                FileType.RECEIVABLE,
                FileType.PERFORMA,
            ]:
                amount_col = "amount"

            if amount_col and amount_col in df.columns:
                result["total_sum"] = float(df[amount_col].sum())
                result["total_mean"] = float(df[amount_col].mean())

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

            # Join on order_code
            joined = pd.merge(
                df_performa[["order_code", "performa_date", "customer_name", "amount"]],
                df_invoices[["order_code", "invoice_date", "total_amount"]],
                on="order_code",
                how="left",
                suffixes=("_performa", "_invoice"),
            )

            # Convert dates
            joined["date_performa"] = joined["performa_date"].apply(
                self._jalali_to_gregorian
            )
            joined["date_invoice"] = joined["invoice_date"].apply(
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
                    ["order_code", "customer_name", "gap_days", "is_paid", "is_on_time"]
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

            name_col = "customer_name"
            amount_col = "total_amount" if file_type == FileType.INVOICES else "amount"

            if file_type == FileType.PAYABLE:
                name_col = "beneficiary"
                amount_col = "amount"

            if name_col not in df.columns or amount_col not in df.columns:
                return {
                    "error": f"ستون‌های مورد نیاز ({name_col}, {amount_col}) یافت نشدند"
                }

            # Map date column
            date_col = "document_date"
            if file_type == FileType.INVOICES:
                date_col = "invoice_date"
            elif file_type == FileType.PERFORMA:
                date_col = "performa_date"

            loyalty = (
                df.groupby(name_col)
                .agg(
                    {
                        amount_col: ["sum", "count", "mean"],
                        date_col: "max",  # Last purchase
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
                    float(df_invoices["total_amount"].sum())
                    if df_invoices is not None
                    else 0
                ),
                "total_payable": (
                    float(df_payable["amount"].sum()) if df_payable is not None else 0
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

    def _analyze_cash_flow(self, **kwargs) -> Optional[Dict]:
        """Analyze cash flow: income vs outcome with time series."""
        try:
            df_payable = self.data_manager.get_dataframe(FileType.PAYABLE)
            df_receivable = self.data_manager.get_dataframe(FileType.RECEIVABLE)
            df_invoices = self.data_manager.get_dataframe(FileType.INVOICES)
            df_performa = self.data_manager.get_dataframe(FileType.PERFORMA)

            # Initialize cash flow data
            cash_flows = []

            # Process payables (outgoing)
            if df_payable is not None and not df_payable.empty:
                payable_data = df_payable[["due_date", "amount"]].copy()
                payable_data["date"] = payable_data["due_date"].apply(
                    self._jalali_to_gregorian
                )
                payable_data["date"] = pd.to_datetime(
                    payable_data["date"], errors="coerce"
                )
                payable_data["amount"] = -pd.to_numeric(
                    payable_data["amount"], errors="coerce"
                )
                payable_data["type"] = "پرداختی (چک)"
                cash_flows.append(payable_data[["date", "amount", "type"]].dropna())

            # Process receivables (incoming)
            if df_receivable is not None and not df_receivable.empty:
                receivable_data = df_receivable[["due_date", "amount"]].copy()
                receivable_data["date"] = receivable_data["due_date"].apply(
                    self._jalali_to_gregorian
                )
                receivable_data["date"] = pd.to_datetime(
                    receivable_data["date"], errors="coerce"
                )
                receivable_data["amount"] = pd.to_numeric(
                    receivable_data["amount"], errors="coerce"
                )
                receivable_data["type"] = "دریافتی (چک)"
                cash_flows.append(receivable_data[["date", "amount", "type"]].dropna())

            # Process invoices (income from sales)
            if df_invoices is not None and not df_invoices.empty:
                invoice_data = df_invoices[["invoice_date", "total_amount"]].copy()
                invoice_data["date"] = invoice_data["invoice_date"].apply(
                    self._jalali_to_gregorian
                )
                invoice_data["date"] = pd.to_datetime(
                    invoice_data["date"], errors="coerce"
                )
                invoice_data["amount"] = pd.to_numeric(
                    invoice_data["total_amount"], errors="coerce"
                )
                invoice_data["type"] = "فروش (فاکتور)"
                cash_flows.append(invoice_data[["date", "amount", "type"]].dropna())

            # Process performas (potential income)
            if df_performa is not None and not df_performa.empty:
                performa_data = df_performa[["performa_date", "amount"]].copy()
                performa_data["date"] = performa_data["performa_date"].apply(
                    self._jalali_to_gregorian
                )
                performa_data["date"] = pd.to_datetime(
                    performa_data["date"], errors="coerce"
                )
                performa_data["amount"] = pd.to_numeric(
                    performa_data["amount"], errors="coerce"
                )
                performa_data["type"] = "پیش‌فاکتور (بالقوه)"
                cash_flows.append(performa_data[["date", "amount", "type"]].dropna())

            if not cash_flows:
                return {"error": "No cash flow data available"}

            # Combine all cash flows
            df_cash = pd.concat(cash_flows, ignore_index=True)
            df_cash = df_cash.sort_values("date")

            # Calculate cumulative cash position
            df_cash["cumulative"] = df_cash["amount"].cumsum()
            df_cash["jalali_date"] = df_cash["date"].apply(self._to_jalali)

            # Calculate daily net flow
            daily_flow = (
                df_cash.groupby(df_cash["date"].dt.date)
                .agg({"amount": "sum", "cumulative": "last"})
                .reset_index()
            )
            daily_flow["jalali_date"] = daily_flow["date"].apply(self._to_jalali)

            # Calculate summary by type
            type_summary = (
                df_cash.groupby("type")["amount"]
                .agg(["sum", "count", "mean"])
                .reset_index()
            )

            # Current position
            current_position = (
                float(df_cash["cumulative"].iloc[-1]) if len(df_cash) > 0 else 0
            )

            # Total income and outcome
            total_income = float(df_cash[df_cash["amount"] > 0]["amount"].sum())
            total_outcome = float(abs(df_cash[df_cash["amount"] < 0]["amount"].sum()))

            return {
                "current_position": current_position,
                "today": datetime.now().strftime("%Y-%m-%d"),
                "today_jalali": self._to_jalali(datetime.now()),
                "total_income": total_income,
                "total_outcome": total_outcome,
                "net_cash_flow": total_income - total_outcome,
                "daily_flow": daily_flow.to_dict("records"),
                "type_summary": type_summary.to_dict("records"),
                "detailed_transactions": df_cash.to_dict("records"),
            }
        except Exception as e:
            logger.error(f"Error in cash flow analysis: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return None

    def _analyze_accounts_aging(self, **kwargs) -> Optional[Dict]:
        """Analyze aging of receivables and payables (overdue analysis)."""
        try:
            from datetime import date

            today = date.today()

            df_payable = self.data_manager.get_dataframe(FileType.PAYABLE)
            df_receivable = self.data_manager.get_dataframe(FileType.RECEIVABLE)

            aging_buckets = {
                "current": [],  # Not yet due
                "1-30": [],  # 1-30 days overdue
                "31-60": [],  # 31-60 days overdue
                "61-90": [],  # 61-90 days overdue
                "90+": [],  # Over 90 days overdue
            }

            # Analyze payables
            payables_aging = {"total": 0, "overdue": 0, "buckets": aging_buckets.copy()}
            if df_payable is not None and not df_payable.empty:
                for _, row in df_payable.iterrows():
                    due_date = self._jalali_to_gregorian(row["due_date"])
                    if due_date:
                        amount = pd.to_numeric(row["amount"], errors="coerce")
                        if pd.notna(amount):
                            days_diff = (today - due_date).days
                            payables_aging["total"] += amount

                            if days_diff < 0:
                                payables_aging["buckets"]["current"].append(amount)
                            elif days_diff <= 30:
                                payables_aging["buckets"]["1-30"].append(amount)
                                payables_aging["overdue"] += amount
                            elif days_diff <= 60:
                                payables_aging["buckets"]["31-60"].append(amount)
                                payables_aging["overdue"] += amount
                            elif days_diff <= 90:
                                payables_aging["buckets"]["61-90"].append(amount)
                                payables_aging["overdue"] += amount
                            else:
                                payables_aging["buckets"]["90+"].append(amount)
                                payables_aging["overdue"] += amount

            # Analyze receivables
            receivables_aging = {
                "total": 0,
                "overdue": 0,
                "buckets": aging_buckets.copy(),
            }
            if df_receivable is not None and not df_receivable.empty:
                for _, row in df_receivable.iterrows():
                    due_date = self._jalali_to_gregorian(row["due_date"])
                    if due_date:
                        amount = pd.to_numeric(row["amount"], errors="coerce")
                        if pd.notna(amount):
                            days_diff = (today - due_date).days
                            receivables_aging["total"] += amount

                            if days_diff < 0:
                                receivables_aging["buckets"]["current"].append(amount)
                            elif days_diff <= 30:
                                receivables_aging["buckets"]["1-30"].append(amount)
                                receivables_aging["overdue"] += amount
                            elif days_diff <= 60:
                                receivables_aging["buckets"]["31-60"].append(amount)
                                receivables_aging["overdue"] += amount
                            elif days_diff <= 90:
                                receivables_aging["buckets"]["61-90"].append(amount)
                                receivables_aging["overdue"] += amount
                            else:
                                receivables_aging["buckets"]["90+"].append(amount)
                                receivables_aging["overdue"] += amount

            # Calculate bucket sums
            for aging_dict in [payables_aging, receivables_aging]:
                aging_dict["buckets"] = {
                    bucket: sum(amounts)
                    for bucket, amounts in aging_dict["buckets"].items()
                }

            return {
                "analysis_date": today.isoformat(),
                "analysis_jalali_date": self._to_jalali(today),
                "payables": payables_aging,
                "receivables": receivables_aging,
                "net_position": receivables_aging["total"] - payables_aging["total"],
                "total_overdue_payables": payables_aging["overdue"],
                "total_overdue_receivables": receivables_aging["overdue"],
            }
        except Exception as e:
            logger.error(f"Error in accounts aging analysis: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return None

    def _analyze_profitability(self, **kwargs) -> Optional[Dict]:
        """Analyze profitability: revenue, costs, margins."""
        try:
            df_invoices = self.data_manager.get_dataframe(FileType.INVOICES)
            df_payable = self.data_manager.get_dataframe(FileType.PAYABLE)

            # Calculate revenue from invoices
            total_revenue = 0
            total_revenue_pre_tax = 0
            total_tax = 0

            if df_invoices is not None and not df_invoices.empty:
                total_revenue = float(
                    pd.to_numeric(df_invoices["total_amount"], errors="coerce").sum()
                )
                total_revenue_pre_tax = float(
                    pd.to_numeric(df_invoices["subtotal"], errors="coerce").sum()
                )
                total_tax = float(
                    pd.to_numeric(df_invoices["tax"], errors="coerce").sum()
                )

            # Calculate costs from payables (operational costs)
            total_costs = 0
            if df_payable is not None and not df_payable.empty:
                total_costs = float(
                    pd.to_numeric(df_payable["amount"], errors="coerce").sum()
                )

            # Calculate profitability metrics
            gross_profit = total_revenue_pre_tax - total_costs
            net_profit = total_revenue - total_costs
            gross_margin = (
                (gross_profit / total_revenue_pre_tax * 100)
                if total_revenue_pre_tax > 0
                else 0
            )
            net_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0

            # Revenue by customer
            customer_revenue = []
            if df_invoices is not None and not df_invoices.empty:
                customer_data = (
                    df_invoices.groupby("customer_name")["total_amount"]
                    .agg(["sum", "count"])
                    .reset_index()
                )
                customer_data.columns = ["customer", "revenue", "invoice_count"]
                customer_data = customer_data.sort_values("revenue", ascending=False)
                customer_revenue = customer_data.head(10).to_dict("records")

            # Monthly revenue trend
            monthly_revenue = []
            if df_invoices is not None and not df_invoices.empty:
                df_inv = df_invoices.copy()
                df_inv["date"] = df_inv["invoice_date"].apply(self._jalali_to_gregorian)
                df_inv["date"] = pd.to_datetime(df_inv["date"], errors="coerce")
                df_inv["amount"] = pd.to_numeric(
                    df_inv["total_amount"], errors="coerce"
                )
                df_inv = df_inv.dropna(subset=["date", "amount"])

                if len(df_inv) > 0:
                    df_inv["month"] = df_inv["date"].dt.to_period("M")
                    monthly = (
                        df_inv.groupby("month")["amount"]
                        .agg(["sum", "count"])
                        .reset_index()
                    )
                    monthly["month"] = monthly["month"].astype(str)
                    monthly_revenue = monthly.to_dict("records")

            return {
                "total_revenue": total_revenue,
                "total_revenue_pre_tax": total_revenue_pre_tax,
                "total_tax": total_tax,
                "total_costs": total_costs,
                "gross_profit": gross_profit,
                "net_profit": net_profit,
                "gross_margin": gross_margin,
                "net_margin": net_margin,
                "customer_revenue": customer_revenue,
                "monthly_revenue": monthly_revenue,
            }
        except Exception as e:
            logger.error(f"Error in profitability analysis: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return None

    def _analyze_integrated_trend(self, **kwargs) -> Optional[Dict]:
        """Analyze integrated business trend: Sales vs Performa vs Net Cash Flow."""
        try:
            df_invoices = self.data_manager.get_dataframe(FileType.INVOICES)
            df_performa = self.data_manager.get_dataframe(FileType.PERFORMA)
            df_payable = self.data_manager.get_dataframe(FileType.PAYABLE)
            df_receivable = self.data_manager.get_dataframe(FileType.RECEIVABLE)

            all_monthly_data = []

            # 1. Monthly Invoices
            if df_invoices is not None and not df_invoices.empty:
                df = df_invoices.copy()
                df["date"] = df["invoice_date"].apply(self._jalali_to_gregorian)
                df["date"] = pd.to_datetime(df["date"], errors="coerce")
                df = df.dropna(subset=["date"])
                if not df.empty:
                    df["month"] = df["date"].dt.to_period("M")
                    # Use total_amount instead of the Persian name
                    monthly_inv = (
                        df.groupby("month")["total_amount"].sum().reset_index()
                    )
                    monthly_inv["type"] = "فروش (فاکتور)"
                    all_monthly_data.append(monthly_inv)

            # 2. Monthly Performa
            if df_performa is not None and not df_performa.empty:
                df = df_performa.copy()
                df["date"] = df["performa_date"].apply(self._jalali_to_gregorian)
                df["date"] = pd.to_datetime(df["date"], errors="coerce")
                df = df.dropna(subset=["date"])
                if not df.empty:
                    df["month"] = df["date"].dt.to_period("M")
                    monthly_perf = df.groupby("month")["amount"].sum().reset_index()
                    monthly_perf["type"] = "پیش‌فاکتور"
                    all_monthly_data.append(monthly_perf)

            # 3. Monthly Cash Flows (Incoming vs Outgoing)
            cash_txs = []
            if df_payable is not None and not df_payable.empty:
                df = df_payable.copy()
                df["date"] = df["due_date"].apply(self._jalali_to_gregorian)
                df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
                df["type_name"] = "پرداختی (چک)"
                cash_txs.append(
                    df[["date", "amount", "type_name"]].dropna(subset=["date"])
                )

            if df_receivable is not None and not df_receivable.empty:
                df = df_receivable.copy()
                df["date"] = df["due_date"].apply(self._jalali_to_gregorian)
                df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
                df["type_name"] = "دریافتی (چک)"
                cash_txs.append(
                    df[["date", "amount", "type_name"]].dropna(subset=["date"])
                )

            if cash_txs:
                df_cash_detail = pd.concat(cash_txs)
                # ...
                # Use sub-blocks to avoid huge replace

            if cash_txs:
                df_cash_detail = pd.concat(cash_txs)
                df_cash_detail["date"] = pd.to_datetime(
                    df_cash_detail["date"], errors="coerce"
                )
                df_cash_detail = df_cash_detail.dropna(subset=["date"])
                if not df_cash_detail.empty:
                    # Sort for cumulative
                    df_cash_detail = df_cash_detail.sort_values("date")
                    df_cash_detail["net_amount"] = df_cash_detail.apply(
                        lambda x: (
                            x["amount"]
                            if x["type_name"] == "دریافتی (چک)"
                            else -x["amount"]
                        ),
                        axis=1,
                    )

                    df_cash_detail["month"] = df_cash_detail["date"].dt.to_period("M")

                    # Group by month and type
                    monthly_cash = (
                        df_cash_detail.groupby(["month", "type_name"])["amount"]
                        .sum()
                        .reset_index()
                    )
                    monthly_cash.columns = ["month", "type", "value"]
                    all_monthly_data.append(monthly_cash)

                    # Add Net Cash Flow line
                    monthly_net = (
                        df_cash_detail.groupby("month")["net_amount"]
                        .sum()
                        .reset_index()
                    )
                    monthly_net.columns = ["month", "value"]
                    monthly_net["type"] = "جریان نقد خالص"
                    all_monthly_data.append(monthly_net)

            if not all_monthly_data:
                return {"error": "Lack of data for trend"}

            df_combined = pd.concat(all_monthly_data)
            df_combined["month_str"] = df_combined["month"].astype(str)

            # Pivot for easier charting
            df_pivot = (
                df_combined.pivot(index="month_str", columns="type", values="value")
                .fillna(0)
                .reset_index()
            )

            # Add cumulative cash position if Net flow exists
            if "جریان نقد خالص" in df_pivot.columns:
                df_pivot["موقعیت نقدی انباشته"] = df_pivot["جریان نقد خالص"].cumsum()

            return {
                "trend_data": df_pivot.to_dict("records"),
                "types": [
                    c
                    for c in df_pivot.columns
                    if c != "month_str" and c != "موقعیت نقدی انباشته"
                ],
                "cumulative_col": (
                    "موقعیت نقدی انباشته"
                    if "موقعیت نقدی انباشته" in df_pivot.columns
                    else None
                ),
            }
        except Exception as e:
            logger.error(f"Error in integrated trend analysis: {e}")
            return None

    def _analyze_forecast(self, forecast_days: int = 90, **kwargs) -> Optional[Dict]:
        """Forecast future cash position based on due dates."""
        try:
            from datetime import date, timedelta

            today = date.today()

            df_payable = self.data_manager.get_dataframe(FileType.PAYABLE)
            df_receivable = self.data_manager.get_dataframe(FileType.RECEIVABLE)

            # Collect future transactions
            future_transactions = []

            # Future payables
            if df_payable is not None and not df_payable.empty:
                for _, row in df_payable.iterrows():
                    due_date = self._jalali_to_gregorian(row["due_date"])
                    if due_date and due_date >= today:
                        amount = pd.to_numeric(row["amount"], errors="coerce")
                        if pd.notna(amount):
                            future_transactions.append(
                                {
                                    "date": due_date,
                                    "amount": -amount,
                                    "type": "پرداختی",
                                    "description": row.get("beneficiary", "N/A"),
                                }
                            )

            # Future receivables
            if df_receivable is not None and not df_receivable.empty:
                for _, row in df_receivable.iterrows():
                    due_date = self._jalali_to_gregorian(row["due_date"])
                    if due_date and due_date >= today:
                        amount = pd.to_numeric(row["amount"], errors="coerce")
                        if pd.notna(amount):
                            future_transactions.append(
                                {
                                    "date": due_date,
                                    "amount": amount,
                                    "type": "دریافتی",
                                    "description": row.get("company_name", "N/A"),
                                }
                            )

            if not future_transactions:
                return {"error": "No future transactions to forecast"}

            # Sort by date
            df_future = pd.DataFrame(future_transactions)
            df_future = df_future.sort_values("date")

            # Calculate cumulative position
            # Assume current position is 0 (you can adjust this)
            current_position = 0
            df_future["cumulative"] = current_position + df_future["amount"].cumsum()
            df_future["jalali_date"] = df_future["date"].apply(self._to_jalali)

            # Daily forecast
            daily_forecast = (
                df_future.groupby("date")
                .agg({"amount": "sum", "cumulative": "last"})
                .reset_index()
            )
            daily_forecast["jalali_date"] = daily_forecast["date"].apply(
                self._to_jalali
            )

            # Find minimum and maximum cash positions
            min_position = float(df_future["cumulative"].min())
            max_position = float(df_future["cumulative"].max())
            min_date = df_future.loc[df_future["cumulative"].idxmin(), "date"]
            max_date = df_future.loc[df_future["cumulative"].idxmax(), "date"]

            # Weekly summary
            df_future["week"] = pd.to_datetime(df_future["date"]).dt.to_period("W")
            weekly_forecast = (
                df_future.groupby("week")
                .agg({"amount": "sum", "cumulative": "last"})
                .reset_index()
            )
            weekly_forecast["week"] = weekly_forecast["week"].astype(str)

            return {
                "forecast_days": forecast_days,
                "current_date": today.isoformat(),
                "current_jalali_date": self._to_jalali(today),
                "forecast_date": (today + timedelta(days=forecast_days)).isoformat(),
                "forecast_jalali_date": self._to_jalali(
                    today + timedelta(days=forecast_days)
                ),
                "total_incoming": float(
                    df_future[df_future["amount"] > 0]["amount"].sum()
                ),
                "total_outgoing": float(
                    abs(df_future[df_future["amount"] < 0]["amount"].sum())
                ),
                "net_forecast": float(df_future["amount"].sum()),
                "min_position": min_position,
                "max_position": max_position,
                "min_position_date": min_date.isoformat(),
                "min_position_jalali_date": self._to_jalali(min_date),
                "max_position_date": max_date.isoformat(),
                "max_position_jalali_date": self._to_jalali(max_date),
                "daily_forecast": daily_forecast.to_dict("records"),
                "weekly_forecast": weekly_forecast.to_dict("records"),
                "detailed_transactions": df_future.to_dict("records"),
            }
        except Exception as e:
            logger.error(f"Error in forecast analysis: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return None
