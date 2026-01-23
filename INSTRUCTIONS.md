# 📊 Cheque Analysis System - Instructions

## Overview
This is a **Streamlit-based dashboard** for analyzing and visualizing upcoming cheques from an Excel file. It provides comprehensive analysis including daily breakdowns, cumulative trends, beneficiary analysis, and data export capabilities.

---

## 📋 Prerequisites

- **Python 3.9+** installed
- **Pip** or package manager installed
- An Excel file named `cheque.xlsx` in the `data/` directory

---

## 🚀 Quick Start

### 1. **Set Up the Environment**

#### Option A: Using Virtual Environment (Recommended)

```bash
# Navigate to project directory
cd /Users/hamed/Documents/myprojects/JEC

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Option B: Using pip directly

```bash
pip install streamlit pandas matplotlib openpyxl jdatetime
```

---

## 📂 Project Structure

```
JEC/
├── streamlit_app.py          # Main Streamlit application
├── main.py                   # Original analysis script (legacy)
├── pyproject.toml            # Project configuration & dependencies
├── requirements.txt          # Pip requirements file
├── INSTRUCTIONS.md           # This file
├── README.md                 # Project overview
└── data/
    └── cheque.xlsx           # Input data file
```

---

## 💻 Running the Application

### Start Streamlit App

```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Run the Streamlit app
streamlit run streamlit_app.py
```

The app will start and typically open at: **http://localhost:8501**

### Run Legacy Script (Optional)

If you want to use the original analysis script instead:

```bash
source .venv/bin/activate
python main.py
```

---

## 🎨 Dashboard Features

### 📊 Key Metrics
- **Total Amount**: Sum of all upcoming cheques
- **Number of Cheques**: Count of upcoming cheques
- **Average Amount**: Average cheque value
- **Beneficiaries**: Number of unique payees

### 📈 Analysis Tabs

#### 1. **Daily Analysis**
   - Bar chart showing total amount by due date
   - Daily breakdown table with amounts

#### 2. **Cumulative**
   - Line chart showing cumulative amounts over time
   - Helps track total obligations as dates progress

#### 3. **Beneficiaries**
   - Top 10 beneficiaries by total amount
   - Horizontal bar chart for easy comparison

#### 4. **Data Table**
   - Detailed table of all cheques
   - Sortable by any column
   - Shows: Cheque #, Due Date, Amount, Beneficiary

#### 5. **Export**
   - Download data as Excel (.xlsx)
   - Download data as CSV (.csv)

### ⚙️ Configuration Panel
- **Lookahead Days**: Adjust how many days ahead to analyze (default: 90 days)
- Real-time recalculation when adjusted

---

## 📥 Input Data Requirements

Your `data/cheque.xlsx` file must contain columns with Persian headers:

| Required Column | Persian Header | Description |
|---|---|---|
| Amount | `بستانکار` | Cheque amount |
| Due Date | `تاریخ سررسید` | Due date in Jalali format (YYYY/MM/DD) |
| Cheque # | `شماره موکد` | Cheque number (optional) |
| Beneficiary | `نام تفصیلی 2` | Payee name (optional) |

### Date Format
- **Format**: Jalali calendar (YYYY/MM/DD)
- **Example**: 1404/11/03 (Persian/Islamic calendar)

---

## 🔧 Configuration

### Lookahead Days
- **Default**: 90 days
- **Range**: 1-365 days
- **Use case**: Adjust to show different time windows of upcoming cheques

### File Path
To change the input file:

Edit line in `streamlit_app.py`:
```python
FILE_PATH = "data/cheque.xlsx"  # Change this path
```

### Date Settings
For manual date specification (if jdatetime not available):

Edit line in `streamlit_app.py`:
```python
TODAY_JALALI = "1404/11/03"  # Set to today's date in Jalali format
```

---

## ✅ Testing & Verification

### 1. **Verify Installation**
```bash
source .venv/bin/activate
python -c "import streamlit, pandas, matplotlib; print('All packages installed!')"
```

### 2. **Check Data File**
```bash
ls -la data/cheque.xlsx
```

### 3. **Run the Dashboard**
```bash
streamlit run streamlit_app.py
```

### 4. **Verify Functionality**
- [ ] Dashboard loads without errors
- [ ] Key metrics display correctly
- [ ] Daily analysis chart renders
- [ ] Cumulative chart displays
- [ ] Beneficiary chart shows data
- [ ] Data table is populated
- [ ] Export buttons work
- [ ] Configuration slider functions

---

## 🐛 Troubleshooting

### Issue: "No module named 'streamlit'"
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "Data file not found"
**Solution**: Ensure `data/cheque.xlsx` exists in the project directory
```bash
ls data/cheque.xlsx
```

### Issue: "Could not find column 'بستانکار'"
**Solution**: Verify Excel file has the required Persian column headers

### Issue: "No upcoming cheques found"
**Solution**: 
- Check if dates in Excel are in Jalali format (YYYY/MM/DD)
- Increase lookahead days using the sidebar slider
- Verify dates are in the future

### Issue: Date-related errors
**Solution**: Ensure `jdatetime` is installed
```bash
pip install jdatetime
```

---

## 📝 Usage Examples

### Example 1: Analyze Next 60 Days
1. Open the app: `streamlit run streamlit_app.py`
2. In sidebar, set "Lookahead Days" to 60
3. View updated charts and metrics

### Example 2: Export Data
1. Go to "Export" tab
2. Click "Download Excel File" or "Download CSV File"
3. File saves to your downloads folder

### Example 3: Find Top Beneficiaries
1. Go to "Beneficiaries" tab
2. View top 10 payees by total amount
3. Use data table to drill down into details

---

## 📊 Output Files

When running the legacy `main.py` script, files are created in `output_charts/`:
- `01_amount_by_due_date.png` - Daily breakdown chart
- `02_cumulative_amount.png` - Cumulative trend chart
- `03_top_beneficiaries.png` - Top beneficiaries chart
- `upcoming_cheques.xlsx` - Exported data

---

## 🔄 Workflow

### Standard Usage
1. Place your cheque data in `data/cheque.xlsx`
2. Run: `streamlit run streamlit_app.py`
3. View dashboard and interact with widgets
4. Export data if needed

### Batch Analysis (Legacy)
1. Place cheque data in `data/cheque.xlsx`
2. Run: `python main.py`
3. Charts generated in `output_charts/` directory

---

## 📚 Dependencies

| Package | Version | Purpose |
|---|---|---|
| streamlit | ≥1.28.0 | Interactive web dashboard |
| pandas | ≥2.0.0 | Data manipulation |
| matplotlib | ≥3.7.0 | Chart generation |
| openpyxl | ≥3.1.0 | Excel file handling |
| jdatetime | ≥5.0.0 | Jalali date calculations |

---

## 🛠️ Development

### Adding Features
- Edit `streamlit_app.py` to add new tabs or metrics
- Run `streamlit run streamlit_app.py` to test changes
- Streamlit hot-reloads on file save

### Creating Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Generating Requirements File
```bash
pip freeze > requirements.txt
```

---

## 📞 Support

### Common Issues
- **Import errors**: Run `pip install -r requirements.txt`
- **File not found**: Verify `data/cheque.xlsx` exists
- **Chart issues**: Ensure matplotlib backend is set to 'Agg'

### Debug Mode
Set environment variable for verbose output:
```bash
export STREAMLIT_LOGGER_LEVEL=debug
streamlit run streamlit_app.py
```

---

## 📄 License

This project is provided as-is for cheque analysis and financial planning.

---

## ✨ Features Checklist

- ✅ Interactive Streamlit dashboard
- ✅ Daily amount breakdown
- ✅ Cumulative trend analysis
- ✅ Top beneficiaries identification
- ✅ Data table with sorting
- ✅ Excel & CSV export
- ✅ Configurable lookahead period
- ✅ Real-time calculations
- ✅ Responsive UI
- ✅ Error handling
- ✅ Jalali date support

---

**Version**: 1.0.0  
**Last Updated**: January 2026  
**Status**: Ready for Production ✨
