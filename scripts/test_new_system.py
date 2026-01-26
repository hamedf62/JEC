import os
import sys
import logging

# Add project root to sys.path
sys.path.append(os.getcwd())

from app.models import FileType, AnalysisType
from app.data_manager import DataManager
from app.analyzer import DataAnalyzer

# Set up logging to see errors
logging.basicConfig(level=logging.INFO)


def test_analysis():
    data_manager = DataManager()
    analyzer = DataAnalyzer(data_manager=data_manager)

    for file_type in FileType:
        print(f"\n--- Testing {file_type.id} ---")
        df = data_manager.get_dataframe(file_type)
        if df is not None:
            print(f"Loaded {len(df)} rows. Columns: {list(df.columns)}")

            # Test Summary Stats
            result = analyzer.analyze(file_type, AnalysisType.SUMMARY_STATS)
            if result:
                print(f"Summary Stats OK: {result.data.get('total_rows')} rows")
            else:
                print("Summary Stats Failed")

            # Test Daily Breakdown
            result = analyzer.analyze(file_type, AnalysisType.DAILY_BREAKDOWN)
            if result and "daily_breakdown" in result.data:
                print(
                    f"Daily Breakdown OK: {len(result.data['daily_breakdown'])} entries"
                )
            else:
                print("Daily Breakdown Failed")
        else:
            print(f"Failed to load {file_type.id}")

    # Test Cross-file Analysis
    print("\n--- Testing Cross-file Analyses ---")
    result = analyzer.analyze(FileType.PAYABLE, AnalysisType.CASH_FLOW)
    if result and "detailed_transactions" in result.data:
        print(f"Cash Flow OK: {len(result.data['detailed_transactions'])} transactions")
    else:
        print("Cash Flow Failed")


if __name__ == "__main__":
    test_analysis()
