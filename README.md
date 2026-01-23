# 📊 Cheque Analysis System

A comprehensive **Streamlit dashboard** for analyzing and visualizing upcoming cheques. This tool helps you track financial obligations, identify trends, and export detailed reports.

## ✨ Features

- 📈 **Interactive Dashboard**: Real-time visualization of cheque data
- 📊 **Multiple Analysis Views**: Daily breakdown, cumulative trends, beneficiary analysis
- 💾 **Data Export**: Download as Excel or CSV formats
- ⚙️ **Configurable**: Adjust lookahead period and filter preferences
- 🔍 **Detailed Insights**: Key metrics, top beneficiaries, and trends
- 🌍 **Jalali Calendar Support**: Full support for Persian calendar dates

## 🚀 Quick Start

### Installation

```bash
# Clone/navigate to project directory
cd /Users/hamed/Documents/myprojects/JEC

# Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run the Dashboard

```bash
streamlit run streamlit_app.py
```

The application will open in your browser at `http://localhost:8501`

## 📋 Requirements

- Python 3.9+
- Excel file: `data/cheque.xlsx` with Persian column headers
- Required columns:
  - `بستانکار` (Amount)
  - `تاریخ سررسید` (Due Date - Jalali format YYYY/MM/DD)
  - `نام تفصیلی 2` (Beneficiary - optional)
  - `شماره موکد` (Cheque # - optional)

## 📚 For Detailed Instructions

See [INSTRUCTIONS.md](INSTRUCTIONS.md) for complete documentation including:
- Detailed setup guide
- Feature descriptions
- Configuration options
- Troubleshooting
- Usage examples

## 🏗️ Project Structure

```
JEC/
├── streamlit_app.py      # Main Streamlit application
├── main.py               # Legacy analysis script
├── requirements.txt      # Python dependencies
├── pyproject.toml        # Project configuration
├── INSTRUCTIONS.md       # Complete documentation
└── data/
    └── cheque.xlsx       # Input data file
```

## 🎯 Dashboard Views

1. **Daily Analysis**: Total amounts by due date
2. **Cumulative**: Cumulative trends over time
3. **Beneficiaries**: Top 10 payees analysis
4. **Data Table**: Complete cheque listing
5. **Export**: Download data in multiple formats

## 🔧 Configuration

Adjust the lookahead period using the sidebar slider (1-365 days).

To customize:
- Edit `FILE_PATH` for data file location
- Set `TODAY_JALALI` for manual date specification

## 📞 Support

For troubleshooting and help, see the [INSTRUCTIONS.md](INSTRUCTIONS.md) file.

---

**Version**: 1.0.0  
**Status**: Production Ready ✅
