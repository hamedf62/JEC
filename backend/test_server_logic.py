import json
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.data_manager import DataManager
from app.analyzer import DataAnalyzer
from app.models import FileType, AnalysisType

dm = DataManager()
analyzer = DataAnalyzer(dm)


def test():
    f_type = FileType.RECEIVABLE
    a_type = AnalysisType.DAILY_BREAKDOWN

    result = analyzer.analyze(f_type, a_type)
    if not result:
        print("Analysis failed")
        return

    d = result.to_dict()
    print("Dict generated")

    try:
        # FastAPI uses complex encoders, but let's test basic first
        j = json.dumps(d)
        print("Simple JSON dumps worked")
    except Exception as e:
        print(f"Simple JSON dumps failed: {e}")


if __name__ == "__main__":
    test()
