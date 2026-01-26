# 🚀 Quick Start Guide - Professional Accounting Dashboard

## System Overview
The JEC Professional Accounting Analysis System provides comprehensive financial analysis for factory management, including cash flow tracking, accounts aging, profitability analysis, and future forecasting.

---

## 📂 Required Data Files

Ensure these files exist in the `data/` directory:

1. **payable.xlsx** - Accounts payable (چک‌های پرداختنی)
   - Columns: تاریخ سررسید, بستانکار, نام تفصیلی 1, شرح عملیات

2. **receivable.xlsx** - Accounts receivable (چک‌های دریافتنی)
   - Columns: تاریخ سررسید, بدهکار, نام شرکت

3. **invoices.xlsx** - Sales invoices (فاکتورهای فروش)
   - Columns: تاریخ, نام مشتری, جمع بهای نهایی, جمع بها پس از کسر تخفیف

4. **performa.xlsx** - Proforma invoices (پیش‌فاکتورها)
   - Columns: تاریخ, OC, نام مشتری, جمع بهای برگه

---

## 🏃‍♂️ Running the Application

### Option 1: Local Development

```bash
# Navigate to project
cd /Users/hamed/Documents/myprojects/JEC

# Activate virtual environment
source .venv/bin/activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Run Streamlit dashboard
streamlit run app/streamlit_dashboard.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`

### Option 2: Docker Deployment

```bash
# Build and start containers
docker-compose up --build

# Access dashboard
# Open browser to http://localhost:8501
```

To stop:
```bash
docker-compose down
```

---

## 📊 Dashboard Sections

### 1. **خلاصه اجرایی (Executive Summary)** 🎯
**Purpose**: Quick overview for managers

**Features**:
- Top 5 KPIs at a glance
- Intelligent alerts and warnings
- Quick charts for cash flow and profitability

**When to use**: 
- Daily morning review
- Before management meetings
- Quick health check

**Key Metrics**:
- Current cash position
- Total revenue and profit
- Profit margin
- Overdue payments

---

### 2. **جریان نقدی (Cash Flow Analysis)** 💵
**Purpose**: Track money in and out

**Features**:
- Current cash position
- Total incoming vs outgoing
- Net cash flow
- Daily flow trends
- Transaction type breakdown

**When to use**:
- Planning payments
- Checking liquidity
- Monthly financial review

**Charts**:
- Cumulative cash position line chart
- Transaction type summary table

---

### 3. **سنجش سررسید (Accounts Aging)** ⏰
**Purpose**: Monitor overdue accounts

**Features**:
- Payables aging (what we owe)
- Receivables aging (what they owe us)
- Aging buckets: Current, 1-30, 31-60, 61-90, 90+ days
- Net position

**When to use**:
- Collections planning
- Payment prioritization
- Credit risk assessment

**Charts**:
- Side-by-side aging distribution bars
- Color-coded by severity

---

### 4. **سودآوری (Profitability Analysis)** 📈
**Purpose**: Understand business profitability

**Features**:
- Revenue, costs, profit metrics
- Gross and net profit margins
- Top 10 customers by revenue
- Monthly revenue trends

**When to use**:
- Monthly/quarterly reviews
- Pricing decisions
- Customer profitability analysis

**Charts**:
- Customer revenue bar chart
- Monthly revenue trend line
- Profit margin indicators

---

### 5. **پیش‌بینی (Financial Forecast)** 🔮
**Purpose**: Predict future cash needs

**Features**:
- Configurable forecast period (30-180 days)
- Future incoming and outgoing
- Minimum/maximum cash positions
- Weekly summary
- Critical date warnings

**When to use**:
- Cash planning
- Loan decisions
- Payment scheduling

**Charts**:
- Dual-axis: Daily net flow + cumulative position
- Weekly forecast table

---

### 6. **گزارش مدیریتی (Management Report)** 🏢
**Purpose**: Comprehensive management overview

**Features**:
- Sales totals
- Payables summary
- Conversion rates (performa to invoice)
- Customer payment performance

**When to use**:
- Board presentations
- Quarterly reviews
- Strategic planning

---

### 7. **تحلیل تفصیلی فایل‌ها (Detailed File Analysis)** 📁
**Purpose**: Deep dive into specific data files

**Features**:
- Daily breakdown by file
- Cumulative trends
- Top beneficiaries/customers
- Customer loyalty analysis
- File-specific metrics

**When to use**:
- Investigating specific transactions
- Customer analysis
- Data verification

---

## 🎨 UI Features

### Sidebar Controls

**Reload Files** (🔄):
- Refreshes all data from Excel files
- Use after updating source files

**Clear Cache** (🗑️):
- Clears analysis cache
- Forces recalculation
- Use if data seems stale

**Cache Info** (💾):
- Shows cache backend (Redis or Memory)
- Cache status information

---

## ⚠️ Understanding Alerts

The system provides intelligent alerts in the Executive Summary:

### 🔴 Danger (خطر)
- **Overdue Payables**: Immediate payment required
- **Critical Cash Shortage**: Urgent attention needed

**Action**: Review immediately and take corrective action

### 🟡 Warning (هشدار)
- **Negative Cash Flow**: More outgoing than incoming
- **Forecast Shortage**: Future cash problems predicted

**Action**: Plan ahead, arrange financing if needed

### 🔵 Info (توجه)
- **Low Profit Margin**: Below 10%
- **Customer Payment Delays**: Collection needed

**Action**: Review processes, consider improvements

### ✅ Success
- All metrics healthy
- No immediate concerns

---

## 💡 Pro Tips

### For Daily Use:
1. Start with **Executive Summary** every morning
2. Check **Alerts** section for urgent issues
3. Review **Cash Flow** before making payments
4. Use **Forecast** for weekly planning

### For Monthly Reviews:
1. **Profitability Analysis** - compare to previous months
2. **Accounts Aging** - review overdue items
3. **Customer Loyalty** - identify top customers
4. **Management Report** - prepare board presentation

### For Decision Making:
1. **Cash Flow** - before large purchases
2. **Forecast** - before taking loans
3. **Profitability** - for pricing changes
4. **Aging Report** - for credit decisions

---

## 🔧 Troubleshooting

### Dashboard won't load
```bash
# Check if all packages installed
pip install -r requirements.txt

# Check for Python errors
streamlit run app/streamlit_dashboard.py
```

### No data showing
1. Verify Excel files exist in `data/` folder
2. Check file names match exactly
3. Use **Reload Files** button in sidebar

### Wrong amounts
1. All amounts should be in **Rials** in Excel
2. System automatically converts to **Toman** (÷ 10)
3. Check column names match Persian text

### Date errors
1. Dates must be in Jalali format: `1404/08/26`
2. Format: `YYYY/MM/DD`
3. Check for typos in date columns

---

## 📝 Data Entry Guidelines

### Date Format
```
Correct: 1404/08/26
Wrong: 1404-08-26, 1404/8/26, 04/08/26
```

### Amount Format
```
Correct: 13126564 (Rials)
Display: 1,312,656.4 (Toman)

Wrong: 1,312,656 (with commas in Excel)
```

### Column Names
- Must match exactly (including Persian characters)
- No extra spaces
- Case-sensitive

---

## 🎓 Training Guide

### For Managers (10 minutes):
1. Open **Executive Summary**
2. Review 5 main KPIs
3. Check alerts section
4. Look at quick charts
5. Done - you have the overview!

### For Accounting Staff (30 minutes):
1. Review all 7 sections
2. Practice with **Reload Files**
3. Explore detailed file analysis
4. Test forecast scenarios
5. Export/print reports

### For IT Staff (1 hour):
1. Review code structure in `app/`
2. Understand data pipeline
3. Test Docker deployment
4. Configure Redis cache
5. Set up monitoring

---

## 📊 Report Generation

### Monthly Report Checklist:
- [ ] Executive Summary screenshot
- [ ] Cash Flow chart
- [ ] Profitability metrics
- [ ] Aging report (both payables and receivables)
- [ ] Top 10 customers
- [ ] Monthly revenue trend
- [ ] Next month forecast

### How to Export:
1. Take screenshots of each section
2. Use browser print function (Ctrl+P / Cmd+P)
3. Save as PDF
4. Or use built-in Streamlit download buttons (where available)

---

## 🔐 Security Notes

### Data Protection:
- All data stays on your server
- No external API calls
- Redis cache is local
- Excel files not shared

### Access Control:
- Deploy behind authentication (nginx, Apache)
- Use VPN for remote access
- Regular backups of Excel files

---

## 📞 Support

### Common Questions:

**Q: Can I add custom analyses?**
A: Yes, extend `DataAnalyzer` class in `app/analyzer.py`

**Q: Can I export to Excel?**
A: Currently screenshots/PDF. Excel export can be added.

**Q: Can I connect to accounting software?**
A: Yes, modify data loaders to read from database instead of Excel

**Q: Can I customize KPIs?**
A: Yes, edit `render_executive_summary()` in dashboard file

---

## 🚀 Next Steps

1. ✅ Review this guide
2. ✅ Check all Excel files in place
3. ✅ Run the dashboard
4. ✅ Explore each section
5. ✅ Set up daily review routine
6. ✅ Train team members
7. ✅ Integrate into workflow

---

## 📚 Additional Resources

- **ARCHITECTURE.md** - Technical architecture details
- **ACCOUNTING_FEATURES.md** - Detailed feature documentation
- **README.md** - General project information
- **INSTRUCTIONS.md** - Setup and installation

---

**Version**: 3.0.0
**Last Updated**: January 25, 2026
**Status**: ✅ Production Ready

**Happy Analyzing! 📊📈💰**
