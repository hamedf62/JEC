from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from app.data_manager import DataManager
from app.analyzer import DataAnalyzer
from app.models import FileType, AnalysisType
import uvicorn
from datetime import datetime

app = FastAPI(title="JEC Financial Analysis API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
data_manager = DataManager()
analyzer = DataAnalyzer(data_manager)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "JEC API is running"}


@app.get("/api/analysis/{file_type}/{analysis_type}")
def get_analysis_data(file_type: str, analysis_type: str):
    # Map string IDs to Enum
    f_type = None
    for t in FileType:
        if t.id.lower() == file_type.lower():
            f_type = t
            break

    a_type = None
    for t in AnalysisType:
        # Try matching by id or name
        if (
            t.id.lower().replace(" ", "_") == analysis_type.lower()
            or t.name.lower() == analysis_type.lower()
        ):
            a_type = t
            break

    if not f_type or not a_type:
        raise HTTPException(
            status_code=400, detail=f"Invalid type: {file_type} or {analysis_type}"
        )

    try:
        result = analyzer.analyze(f_type, a_type)
        if not result:
            raise HTTPException(status_code=500, detail="Analysis failed")
        return result.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/summary")
def get_dashboard_summary():
    summary = {}
    for f_type in [
        FileType.PAYABLE,
        FileType.RECEIVABLE,
        FileType.INVOICES,
        FileType.PERFORMA,
    ]:
        try:
            result = analyzer.analyze(f_type, AnalysisType.SUMMARY_STATS)
            if result:
                summary[f_type.id] = result.data
        except Exception:
            continue
    return summary


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
