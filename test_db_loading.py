import sys
import os
from pathlib import Path
import pandas as pd

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parent / "backend"))

from app.data_manager import DataManager
from app.models import FileType

dm = DataManager()
for f_type in FileType:
    print(f"Loading {f_type.id}...")
    df = dm.load_file(f_type, force_reload=True)
    if df is not None:
        print(f"Success: {len(df)} rows")
    else:
        print(f"Failed to load {f_type.id}")
