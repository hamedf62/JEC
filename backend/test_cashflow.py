from app.analyzer import DataAnalyzer
from app.data_manager import DataManager
from app.models import AnalysisType, FileType
import json


def test_cash_flow():
    dm = DataManager()
    da = DataAnalyzer(dm)

    result = da.analyze(FileType.PAYABLE, AnalysisType.CASH_FLOW)
    if result:
        print("Cash Flow Analysis Success!")
        print(f"Current Position: {result.data.get('current_position')}")
        print(f"Today: {result.data.get('today')}")
        print(f"Daily Flow Count: {len(result.data.get('daily_flow', []))}")
    else:
        print("Cash Flow Analysis Failed!")


if __name__ == "__main__":
    test_cash_flow()
