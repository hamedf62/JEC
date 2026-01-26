"""
Professional Streamlit Dashboard for Multi-File Analysis.
Demonstrates enterprise-level architecture with classes, caching, and modular design.
"""

import logging
import os
import sys
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to sys.path to allow absolute imports from 'app'
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from app.models import FileType, AnalysisType
from app.data_manager import DataManager
from app.analyzer import DataAnalyzer
from app.cache import CacheManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get configuration from env
PROJECT_NAME = os.getenv("PROJECT_NAME", "سیستم تحلیل داده")
PROJECT_COMPANY = os.getenv("PROJECT_COMPANY", "JEC")

# Configure Streamlit
st.set_page_config(
    page_title=f"داشبورد {PROJECT_NAME} (تومان)",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for RTL and styling
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn&display=swap');
    
    html, body, [data-testid="stSidebar"], .stMarkdown, .main, div, span, p, h1, h2, h3, h4, h5, h6 {
        font-family: 'Vazirmatn', sans-serif !important;
        direction: rtl;
        text-align: right;
    }
    
    /* Fix for sidebar and metric alignment */
    [data-testid="stSidebar"] {
        direction: rtl;
    }
    
    .stMetric {
        direction: rtl;
        text-align: right;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        direction: ltr;
        text-align: left;
    }
    
    /* Fix for overlapping text in expanders */
    div[data-testid="stExpander"] svg {
        order: 1;
        margin-left: 10px;
    }
    
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-right: 5px solid #4e73df;
        box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
        margin: 0.5rem 0;
        color: #3a3b45;
    }
    .metric-card h3 {
        font-size: 0.9rem;
        color: #4e73df;
        margin-bottom: 0.5rem;
    }
    .metric-card h2 {
        font-size: 1.4rem;
        margin: 0;
    }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource
def initialize_managers() -> tuple[DataManager, DataAnalyzer, CacheManager]:
    """Initialize application managers (cached as resource)."""
    # Try to connect to Redis
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    redis_db = int(os.getenv("REDIS_DB", 0))

    redis_client = None
    try:
        import redis

        client = redis.Redis(
            host=redis_host, port=redis_port, db=redis_db, socket_timeout=2
        )
        if client.ping():
            redis_client = client
            logger.info(f"Connected to Redis at {redis_host}:{redis_port}")
        else:
            logger.warning("Redis ping failed, using in-memory cache")
    except Exception as e:
        logger.warning(
            f"Could not connect to Redis: {e}. Falling back to in-memory cache"
        )

    cache_manager = CacheManager(redis_client=redis_client, ttl_seconds=3600)
    data_manager = DataManager(cache_manager=cache_manager)
    analyzer = DataAnalyzer(data_manager=data_manager, cache_manager=cache_manager)
    logger.info("Initialized managers: CacheManager, DataManager, DataAnalyzer")
    return data_manager, analyzer, cache_manager


def render_file_selector_tabs():
    """Render tabs for different file types."""
    return st.tabs([f.label for f in FileType])


def render_metrics(analyzer: DataAnalyzer, file_type: FileType):
    """Render key metrics for a file."""
    with st.spinner(f"در حال بارگذاری شاخص‌های {file_type.label}..."):
        result = analyzer.analyze(file_type, AnalysisType.SUMMARY_STATS)
        if result and result.data:
            data = result.data

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "تعداد ردیف‌ها",
                    f"{data.get('total_rows', 0):,}",
                    delta=None,
                    label_visibility="visible",
                )

            with col2:
                st.metric("تعداد ستون‌ها", data.get("total_columns", 0))

            with col3:
                st.metric("مقادیر خالی", len(data.get("null_values", {})))


def render_daily_breakdown(analyzer: DataAnalyzer, file_type: FileType):
    """Render daily breakdown analysis."""
    with st.spinner(f"تجزیه‌و‌تحلیل روزانه {file_type.label}..."):
        result = analyzer.analyze(file_type, AnalysisType.DAILY_BREAKDOWN)
        if result and result.data:
            data = result.data
            st.write("#### تجزیه و تحلیل روزانه")

            if "daily_breakdown" in data and data["daily_breakdown"]:
                df_daily = pd.DataFrame(data["daily_breakdown"])

                # Chart
                x_col = (
                    "jalali_date"
                    if "jalali_date" in df_daily.columns
                    else df_daily.columns[0]
                )
                if (
                    "date" in df_daily.columns
                    or df_daily.columns[0] == "date"
                    or "jalali_date" in df_daily.columns
                ):
                    fig = px.bar(
                        df_daily,
                        x=x_col,
                        y="sum",
                        title=f"مجموع روزانه - {file_type.label} (تومان)",
                        labels={"sum": "مجموع مبلغ", x_col: "تاریخ"},
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # Table
                with st.expander("مشاهده جدول داده‌ها"):
                    st.dataframe(df_daily, use_container_width=True)
            else:
                st.info("داده‌های تاریخی برای این فایل موجود نیست")


def render_cumulative_analysis(analyzer: DataAnalyzer, file_type: FileType):
    """Render cumulative analysis."""
    with st.spinner(f"تحلیل روند انباشته {file_type.label}..."):
        result = analyzer.analyze(file_type, AnalysisType.CUMULATIVE)
        if result and result.data:
            data = result.data
            st.write("#### تحلیل انباشته")

            col1, col2 = st.columns(2)
            with col1:
                st.metric("مجموع کل (تومان)", f"{data.get('total_sum', 0):,.0f}")
            with col2:
                st.metric("میانگین (تومان)", f"{data.get('total_mean', 0):,.0f}")

            if "cumulative_data" in data and data["cumulative_data"]:
                df_cum = pd.DataFrame(data["cumulative_data"])

                # Get column names dynamically
                cols = df_cum.columns.tolist()
                if "cumulative" in df_cum.columns:
                    x_col = (
                        "jalali_date"
                        if "jalali_date" in df_cum.columns
                        else (cols[0] if cols else "date")
                    )
                    cum_col = "cumulative"

                    fig = px.line(
                        df_cum,
                        x=x_col,
                        y=cum_col,
                        title=f"روند انباشته - {file_type.label} (تومان)",
                        markers=True,
                        labels={cum_col: "مبلغ انباشته", x_col: "تاریخ"},
                    )
                    st.plotly_chart(fig, use_container_width=True)


def render_top_beneficiaries(analyzer: DataAnalyzer, file_type: FileType):
    """Render top beneficiaries/categories."""
    with st.spinner(f"تحلیل دسته‌بندی‌های برتر {file_type.label}..."):
        top_n = st.slider("تعداد موارد برتر", 5, 20, 10, key=f"top_n_{file_type.id}")

        result = analyzer.analyze(
            file_type, AnalysisType.TOP_BENEFICIARIES, top_n=top_n
        )
        if result and result.data:
            data = result.data
            st.write("#### دسته‌بندی‌های برتر")

            if data.get("beneficiaries"):
                df_top = pd.DataFrame(data["beneficiaries"])

                # Chart
                if len(df_top) > 0:
                    col_names = df_top.columns.tolist()
                    if len(col_names) >= 2:
                        fig = px.bar(
                            df_top,
                            x="sum",
                            y=col_names[0],
                            orientation="h",
                            title=f"{top_n} ردیف برتر (تومان)",
                            labels={"sum": "مجموع مبلغ"},
                        )
                        st.plotly_chart(fig, use_container_width=True)

                # Table
                with st.expander("مشاهده جزئیات داده‌ها"):
                    st.dataframe(df_top, use_container_width=True)
            else:
                st.info("داده‌ای برای دسته‌بندی یافت نشد")


def render_file_info(data_manager: DataManager, file_type: FileType):
    """Render file information."""
    with st.expander("📋 اطلاعات فایل"):
        info = data_manager.get_file_info(file_type)
        if info:
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**نوع فایل:** {info['file_type']}")
                st.write(f"**مسیر:** {info['filepath']}")
            with col2:
                st.write(f"**تعداد ردیف:** {info['rows']:,}")
                st.write(f"**تعداد ستون:** {info['columns']}")

            with st.expander("نام ستون‌ها"):
                cols_df = pd.DataFrame({"نام ستون": info["column_names"]})
                st.dataframe(cols_df, use_container_width=True)


def render_customer_loyalty(analyzer: DataAnalyzer, file_type: FileType):
    """Render customer loyalty analysis."""
    with st.spinner(f"در حال تحلیل وفاداری مشتریان..."):
        result = analyzer.analyze(file_type, AnalysisType.CUSTOMER_LOYALTY)
        if result and result.data:
            data = result.data
            st.write("#### وفاداری مشتریان")

            if "loyalty_data" in data:
                df_loyalty = pd.DataFrame(data["loyalty_data"])

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("تعداد کل مشتریان", data.get("total_customers", 0))

                # Chart: Frequency vs Value
                fig = px.scatter(
                    df_loyalty,
                    x="order_count",
                    y="total_value",
                    size="average_value",
                    hover_name="customer_name",
                    title="فراوانی خرید در مقابل ارزش کل (تومان)",
                    labels={
                        "order_count": "تعداد سفارش",
                        "total_value": "ارزش کل خرید",
                    },
                )
                st.plotly_chart(fig, use_container_width=True)

                with st.expander("مشاهده لیست وفاداری"):
                    st.dataframe(df_loyalty, use_container_width=True)


def render_on_time_payment(analyzer: DataAnalyzer):
    """Render on-time payment analysis."""
    with st.spinner("تحلیل پرداخت‌های به موقع..."):
        result = analyzer.analyze(FileType.PERFORMA, AnalysisType.ON_TIME_PAYMENT)
        if result and result.data:
            data = result.data
            st.header("⏱️ تحلیل پرداخت‌های به موقع")

            col1, col2, col3 = st.columns(3)
            col1.metric("کل پیش‌فاکتورها", data["total_performa"])
            col2.metric("تبدیل شده به فاکتور", data["total_paid"])
            col3.metric("نرخ خوش‌قولی", f"{data['on_time_rate']*100:.1f}%")

            if "payment_details" in data:
                df_details = pd.DataFrame(data["payment_details"])

                # Pie chart for paid vs unpaid
                fig = px.pie(
                    values=[
                        data["total_paid"],
                        data["total_performa"] - data["total_paid"],
                    ],
                    names=["پرداخت شده", "پرداخت نشده"],
                    title="وضعیت پرداخت پیش‌فاکتورها",
                )
                st.plotly_chart(fig, use_container_width=True)

                with st.expander("مشاهده جزئیات تاخیرات"):
                    st.dataframe(df_details, use_container_width=True)


def render_advanced_report(analyzer: DataAnalyzer):
    """Render advanced management report."""
    with st.spinner("در حال تهیه گزارش مدیریتی..."):
        result = analyzer.analyze(FileType.INVOICES, AnalysisType.ADVANCED_REPORT)
        if result and result.data:
            data = result.data
            st.header("🏢 گزارش مدیریتی پیشرفته")

            # KPI Cards
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(
                    f"""<div class="metric-card"><h3>فروش کل</h3><h2>{data['total_sales']:,.0f} تومان</h2></div>""",
                    unsafe_allow_html=True,
                )
            with c2:
                st.markdown(
                    f"""<div class="metric-card"><h3>مجموع بدهی (چک)</h3><h2>{data['total_payable']:,.0f} تومان</h2></div>""",
                    unsafe_allow_html=True,
                )
            with c3:
                st.markdown(
                    f"""<div class="metric-card"><h3>وضعیت خالص</h3><h2>{data['net_position']:,.0f} تومان</h2></div>""",
                    unsafe_allow_html=True,
                )

            st.markdown("---")

            col_a, col_b = st.columns(2)
            with col_a:
                st.write("#### قیف فروش (Conversion)")
                fig = go.Figure(
                    go.Funnel(
                        y=["پیش‌فاکتور", "فاکتور نهایی"],
                        x=[data["performa_count"], data["invoice_count"]],
                    )
                )
                st.plotly_chart(fig, use_container_width=True)

            with col_b:
                st.write("#### آمار کلی")
                st.write(f"- تعداد پیش‌فاکتورها: {data['performa_count']}")
                st.write(f"- تعداد فاکتورها: {data['invoice_count']}")
                st.write(f"- نرخ تبدیل: {data['conversion_rate']*100:.1f}%")


def render_cache_info(cache_manager: CacheManager):
    """Render cache information."""
    with st.sidebar.expander("💾 وضعیت حافظه موقت"):
        info = cache_manager.get_cache_info()
        for key, value in info.items():
            st.write(f"**{key}:** {value}")


def render_cash_flow(analyzer: DataAnalyzer):
    """Render comprehensive cash flow analysis."""
    with st.spinner("تحلیل جریان وجوه نقد..."):
        result = analyzer.analyze(FileType.INVOICES, AnalysisType.CASH_FLOW)
        if result and result.data:
            data = result.data
            st.header("💵 تحلیل جریان وجوه نقد")

            # KPI Cards
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(
                    "موقعیت فعلی وجه نقد",
                    f"{data.get('current_position', 0):,.0f} تومان",
                    delta=None,
                    delta_color="normal",
                )
            with col2:
                st.metric("کل دریافتی‌ها", f"{data.get('total_income', 0):,.0f} تومان")
            with col3:
                st.metric("کل پرداختی‌ها", f"{data.get('total_outcome', 0):,.0f} تومان")
            with col4:
                net_flow = data.get("net_cash_flow", 0)
                st.metric(
                    "جریان خالص",
                    f"{net_flow:,.0f} تومان",
                    delta=None,
                    delta_color="normal" if net_flow >= 0 else "inverse",
                )

            st.markdown("---")

            # Cash flow chart
            if "daily_flow" in data and data["daily_flow"]:
                df_flow = pd.DataFrame(data["daily_flow"])

                col_a, col_b = st.columns(2)

                with col_a:
                    st.write("#### روند جریان نقدی روزانه")
                    fig = go.Figure()
                    fig.add_trace(
                        go.Scatter(
                            x=df_flow["jalali_date"],
                            y=df_flow["cumulative"],
                            mode="lines+markers",
                            name="موقعیت انباشته",
                            line=dict(color="blue", width=3),
                        )
                    )
                    fig.update_layout(
                        xaxis_title="تاریخ",
                        yaxis_title="مبلغ (تومان)",
                        hovermode="x unified",
                    )
                    st.plotly_chart(fig, use_container_width=True)

                with col_b:
                    st.write("#### خلاصه بر اساس نوع تراکنش")
                    if "type_summary" in data:
                        df_summary = pd.DataFrame(data["type_summary"])
                        st.dataframe(df_summary, use_container_width=True)

            # Detailed transactions
            with st.expander("مشاهده تراکنش‌های تفصیلی"):
                if "detailed_transactions" in data:
                    df_details = pd.DataFrame(data["detailed_transactions"])
                    st.dataframe(df_details, use_container_width=True)


def render_accounts_aging(analyzer: DataAnalyzer):
    """Render accounts aging analysis."""
    with st.spinner("تحلیل سنجش سررسید حساب‌ها..."):
        result = analyzer.analyze(FileType.PAYABLE, AnalysisType.ACCOUNTS_AGING)
        if result and result.data:
            data = result.data
            st.header("⏰ سنجش سررسید حساب‌ها (Aging Report)")

            st.info(
                f"📅 تاریخ تحلیل: {data.get('analysis_jalali_date', data.get('analysis_date', 'N/A'))}"
            )

            # Payables vs Receivables
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("🔴 بدهی‌ها (پرداختی)")
                payables = data.get("payables", {})
                st.metric("کل بدهی", f"{payables.get('total', 0):,.0f} تومان")
                st.metric(
                    "معوقه",
                    f"{payables.get('overdue', 0):,.0f} تومان",
                    delta=None,
                    delta_color="inverse",
                )

                # Aging buckets chart
                buckets = payables.get("buckets", {})
                df_buckets = pd.DataFrame(
                    {"دوره": list(buckets.keys()), "مبلغ": list(buckets.values())}
                )
                fig = px.bar(
                    df_buckets,
                    x="دوره",
                    y="مبلغ",
                    title="توزیع سنی بدهی‌ها",
                    color="مبلغ",
                    color_continuous_scale="Reds",
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("🟢 طلب‌ها (دریافتی)")
                receivables = data.get("receivables", {})
                st.metric("کل طلب", f"{receivables.get('total', 0):,.0f} تومان")
                st.metric(
                    "معوقه",
                    f"{receivables.get('overdue', 0):,.0f} تومان",
                    delta=None,
                    delta_color="inverse",
                )

                # Aging buckets chart
                buckets = receivables.get("buckets", {})
                df_buckets = pd.DataFrame(
                    {"دوره": list(buckets.keys()), "مبلغ": list(buckets.values())}
                )
                fig = px.bar(
                    df_buckets,
                    x="دوره",
                    y="مبلغ",
                    title="توزیع سنی طلب‌ها",
                    color="مبلغ",
                    color_continuous_scale="Greens",
                )
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")

            # Net position
            net_pos = data.get("net_position", 0)
            st.metric(
                "موقعیت خالص (طلب - بدهی)",
                f"{net_pos:,.0f} تومان",
                delta=None,
                delta_color="normal" if net_pos >= 0 else "inverse",
            )


def render_profitability(analyzer: DataAnalyzer):
    """Render profitability analysis."""
    with st.spinner("تحلیل سودآوری..."):
        result = analyzer.analyze(
            FileType.INVOICES, AnalysisType.PROFITABILITY_ANALYSIS
        )
        if result and result.data:
            data = result.data
            st.header("📈 تحلیل سودآوری و درآمد")

            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("درآمد کل", f"{data.get('total_revenue', 0):,.0f} تومان")
            with col2:
                st.metric("هزینه‌ها", f"{data.get('total_costs', 0):,.0f} تومان")
            with col3:
                gross_profit = data.get("gross_profit", 0)
                st.metric(
                    "سود ناخالص",
                    f"{gross_profit:,.0f} تومان",
                    delta=None,
                    delta_color="normal" if gross_profit >= 0 else "inverse",
                )
            with col4:
                net_profit = data.get("net_profit", 0)
                st.metric(
                    "سود خالص",
                    f"{net_profit:,.0f} تومان",
                    delta=None,
                    delta_color="normal" if net_profit >= 0 else "inverse",
                )

            # Margins
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("حاشیه سود ناخالص", f"{data.get('gross_margin', 0):.2f}%")
            with col_b:
                st.metric("حاشیه سود خالص", f"{data.get('net_margin', 0):.2f}%")

            st.markdown("---")

            # Charts
            col_chart1, col_chart2 = st.columns(2)

            with col_chart1:
                st.write("#### ده مشتری برتر بر اساس درآمد")
                if "customer_revenue" in data and data["customer_revenue"]:
                    df_customers = pd.DataFrame(data["customer_revenue"])
                    fig = px.bar(
                        df_customers,
                        x="revenue",
                        y="customer",
                        orientation="h",
                        title="درآمد به تفکیک مشتری",
                        labels={"revenue": "درآمد", "customer": "مشتری"},
                    )
                    st.plotly_chart(fig, use_container_width=True)

            with col_chart2:
                st.write("#### روند درآمد ماهانه")
                if "monthly_revenue" in data and data["monthly_revenue"]:
                    df_monthly = pd.DataFrame(data["monthly_revenue"])
                    fig = px.line(
                        df_monthly,
                        x="month",
                        y="sum",
                        title="روند درآمد ماهانه",
                        markers=True,
                        labels={"sum": "درآمد", "month": "ماه"},
                    )
                    st.plotly_chart(fig, use_container_width=True)


def render_forecast(analyzer: DataAnalyzer):
    """Render cash flow forecast."""
    with st.spinner("پیش‌بینی وضعیت مالی..."):
        forecast_days = st.slider("دوره پیش‌بینی (روز)", 30, 180, 90, step=30)

        result = analyzer.analyze(
            FileType.PAYABLE, AnalysisType.FORECAST, forecast_days=forecast_days
        )
        if result and result.data:
            data = result.data
            st.header("🔮 پیش‌بینی جریان نقدی")

            if "error" not in data:
                st.info(
                    f"📅 از تاریخ {data.get('current_jalali_date', data.get('current_date'))} تا {data.get('forecast_jalali_date', data.get('forecast_date'))}"
                )

                # Summary metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        "کل دریافتی‌های آینده",
                        f"{data.get('total_incoming', 0):,.0f} تومان",
                    )
                with col2:
                    st.metric(
                        "کل پرداختی‌های آینده",
                        f"{data.get('total_outgoing', 0):,.0f} تومان",
                    )
                with col3:
                    net = data.get("net_forecast", 0)
                    st.metric(
                        "خالص پیش‌بینی",
                        f"{net:,.0f} تومان",
                        delta=None,
                        delta_color="normal" if net >= 0 else "inverse",
                    )

                # Min/Max positions
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric(
                        "حداقل موقعیت نقدی",
                        f"{data.get('min_position', 0):,.0f} تومان",
                        help=f"در تاریخ {data.get('min_position_date', 'N/A')}",
                    )
                with col_b:
                    st.metric(
                        "حداکثر موقعیت نقدی",
                        f"{data.get('max_position', 0):,.0f} تومان",
                        help=f"در تاریخ {data.get('max_position_date', 'N/A')}",
                    )

                st.markdown("---")

                # Forecast chart
                if "daily_forecast" in data and data["daily_forecast"]:
                    df_forecast = pd.DataFrame(data["daily_forecast"])

                    fig = go.Figure()

                    # Daily net flow
                    fig.add_trace(
                        go.Bar(
                            x=df_forecast["jalali_date"],
                            y=df_forecast["amount"],
                            name="جریان خالص روزانه",
                            marker_color="lightblue",
                        )
                    )

                    # Cumulative position
                    fig.add_trace(
                        go.Scatter(
                            x=df_forecast["jalali_date"],
                            y=df_forecast["cumulative"],
                            name="موقعیت انباشته",
                            mode="lines+markers",
                            line=dict(color="red", width=3),
                            yaxis="y2",
                        )
                    )

                    fig.update_layout(
                        title="پیش‌بینی جریان نقدی روزانه",
                        xaxis_title="تاریخ",
                        yaxis_title="جریان خالص (تومان)",
                        yaxis2=dict(
                            title="موقعیت انباشته (تومان)", overlaying="y", side="right"
                        ),
                        hovermode="x unified",
                        height=500,
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # Weekly forecast
                with st.expander("پیش‌بینی هفتگی"):
                    if "weekly_forecast" in data:
                        df_weekly = pd.DataFrame(data["weekly_forecast"])
                        st.dataframe(df_weekly, use_container_width=True)

                # Detailed transactions
                with st.expander("تراکنش‌های آینده"):
                    if "detailed_transactions" in data:
                        df_trans = pd.DataFrame(data["detailed_transactions"])
                        st.dataframe(df_trans, use_container_width=True)
            else:
                st.warning(data["error"])


def render_executive_summary(analyzer: DataAnalyzer):
    """Render executive summary dashboard with key KPIs and alerts."""
    st.header("🎯 داشبورد مدیریتی - خلاصه اجرایی")

    # Top KPI Row
    with st.spinner("در حال تهیه گزارش مدیریتی..."):
        # Get all required analyses
        cash_flow = analyzer.analyze(FileType.INVOICES, AnalysisType.CASH_FLOW)
        aging = analyzer.analyze(FileType.PAYABLE, AnalysisType.ACCOUNTS_AGING)
        profitability = analyzer.analyze(
            FileType.INVOICES, AnalysisType.PROFITABILITY_ANALYSIS
        )
        integrated = analyzer.analyze(FileType.INVOICES, AnalysisType.INTEGRATED_TREND)

        # 1. High Level Metrics
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)

        with kpi1:
            revenue = profitability.data.get("total_revenue", 0) if profitability else 0
            st.metric(
                "فروش کل نهایی", f"{revenue:,.0f}", help="مجموع فاکتورهای فروش صادر شده"
            )

        with kpi2:
            current_pos = cash_flow.data.get("current_position", 0) if cash_flow else 0
            st.metric("موقعیت نقدینگی", f"{current_pos:,.0f}", delta=None)

        with kpi3:
            net_profit = profitability.data.get("net_profit", 0) if profitability else 0
            st.metric(
                "سود خالص تخمینی",
                f"{net_profit:,.0f}",
                help="فروش نهایی منهای مجموع اسناد پرداختنی",
            )

        with kpi4:
            overdue = aging.data.get("total_overdue_payables", 0) if aging else 0
            st.metric(
                "بدهی معوقه", f"{overdue:,.0f}", delta=None, delta_color="inverse"
            )

        st.markdown("---")

        # 2. Main Trend Graph (Integrated Past & Future)
        st.subheader("📈 روند جامع عملکرد مالی (گذشته و آینده)")
        if integrated and "trend_data" in integrated.data:
            df_trend = pd.DataFrame(integrated.data["trend_data"])

            fig = go.Figure()

            # Add bars for different categories
            for col in integrated.data["types"]:
                color = (
                    "#00cc96"
                    if "دریافتی" in col or "فروش" in col
                    else ("#ef553b" if "پرداختی" in col else "#636efa")
                )
                fig.add_trace(
                    go.Bar(
                        x=df_trend["month_str"],
                        y=df_trend[col],
                        name=col,
                        marker_color=color,
                        opacity=0.7,
                    )
                )

            # Add Cumulative Cash Line
            if integrated.data.get("cumulative_col"):
                cum_col = integrated.data["cumulative_col"]
                fig.add_trace(
                    go.Scatter(
                        x=df_trend["month_str"],
                        y=df_trend[cum_col],
                        name="موقعیت نقدینگی نهایی",
                        line=dict(color="black", width=4, dash="dot"),
                        yaxis="y2",
                    )
                )

            # Add Zero Line for y2
            fig.add_shape(
                type="line",
                line=dict(color="red", width=2, dash="solid"),
                x0=0,
                x1=1,
                xref="paper",
                y0=0,
                y1=0,
                yref="y2",
            )

            fig.update_layout(
                title="تراکنش‌های ماهانه و پیش‌بینی نقدینگی",
                xaxis_title="ماه",
                yaxis_title="مبلغ هر تراکنش (تومان)",
                yaxis2=dict(
                    title="موقعیت نقدینگی انباشته (تومان)",
                    overlaying="y",
                    side="right",
                    showgrid=False,
                ),
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
                ),
                barmode="group",
                hovermode="x unified",
                height=550,
            )
            st.plotly_chart(fig, use_container_width=True)
            st.info(
                "💡 خط هشداری قرمز نشان‌دهنده نقطه صفر نقدینگی است. قرارگیری خط مشکی در زیر آن به معنای پیش‌بینی زمان کمبود نقدینگی است."
            )

        st.markdown("---")

        # 3. Alerts and Summaries
        col_alert, col_summary = st.columns([1, 1])

        with col_alert:
            st.subheader("⚠️ وضعیت ریسک و هشدارها")
            alerts = []
            if overdue > 0:
                alerts.append(
                    (
                        "error",
                        f"بدهی معوقه به مبلغ {overdue:,.0f} تومان نیازمند تسویه است.",
                    )
                )

            # Check for future negative positions in the integrated trend
            if integrated and "trend_data" in integrated.data:
                df_trend = pd.DataFrame(integrated.data["trend_data"])
                if "موقعیت نقدی انباشته" in df_trend.columns:
                    negative_months = df_trend[df_trend["موقعیت نقدی انباشته"] < 0][
                        "month_str"
                    ].tolist()
                    if negative_months:
                        alerts.append(
                            (
                                "error",
                                f"هشدار نقدینگی: در ماه‌های {', '.join(negative_months)} پیش‌بینی کمبود وجه نقد وجود دارد.",
                            )
                        )

            if cash_flow and cash_flow.data.get("net_cash_flow", 0) < 0:
                alerts.append(
                    ("warning", "جریان نقد عملیاتی در دوره اخیر منفی بوده است.")
                )

            if profitability and profitability.data.get("net_margin", 0) < 15:
                alerts.append(
                    (
                        "info",
                        f"حاشیه سود خالص {profitability.data.get('net_margin', 0):.1f}% است.",
                    )
                )

            if not alerts:
                st.success("✅ تمامی شاخص‌های کلیدی در وضعیت سبز قرار دارند.")
            else:
                for level, msg in alerts:
                    if level == "error":
                        st.error(msg)
                    elif level == "warning":
                        st.warning(msg)
                    else:
                        st.info(msg)

        with col_summary:
            st.subheader("📋 خلاصه وضعیت")
            if profitability and "customer_revenue" in profitability.data:
                df_cust = pd.DataFrame(profitability.data["customer_revenue"]).head(5)
                st.write("**مشتریان استراتژیک (بر اساس درآمد):**")
                for _, row in df_cust.iterrows():
                    st.write(f"- {row['customer']}: {row['revenue']:,.0f} تومان")


def render_cache_info(cache_manager: CacheManager):
    """Render cache information."""
    with st.sidebar.expander("💾 وضعیت حافظه موقت"):
        info = cache_manager.get_cache_info()
        for key, value in info.items():
            st.write(f"**{key}:** {value}")


def render_accounts_aging_single(analyzer: DataAnalyzer, file_type: FileType):
    """Render aging analysis for a single file type (Receivable or Payable)."""
    with st.spinner(f"تحلیل سررسید {file_type.label}..."):
        result = analyzer.analyze(file_type, AnalysisType.ACCOUNTS_AGING)
        if result and result.data:
            data = result.data
            key = "payables" if file_type == FileType.PAYABLE else "receivables"
            aging_data = data.get(key, {})

            col1, col2 = st.columns(2)
            with col1:
                st.metric("کل مبلغ", f"{aging_data.get('total', 0):,.0f} تومان")
            with col2:
                st.metric(
                    "مبلغ معوقه (گذشته)",
                    f"{aging_data.get('overdue', 0):,.0f} تومان",
                    delta_color="inverse",
                )

            # Buckets
            buckets = aging_data.get("buckets", {})
            if buckets:
                df_buckets = pd.DataFrame(
                    {"بازه زمانی": list(buckets.keys()), "مبلغ": list(buckets.values())}
                )
                fig = px.bar(
                    df_buckets,
                    x="بازه زمانی",
                    y="مبلغ",
                    title=f"توزیع سررسید {file_type.label}",
                    color="مبلغ",
                    color_continuous_scale="Reds" if key == "payables" else "Greens",
                )
                st.plotly_chart(fig, use_container_width=True)


def render_sales_tab(analyzer: DataAnalyzer):
    """Render the Sales tab combining Invoices and Performas."""
    st.header("📈 مدیریت فروش و پیش‌فاکتورها")
    
    tab_inv, tab_perf = st.tabs(["فاکتورهای نهایی (Income)", "پیش‌فاکتورها (Pipeline)"])
    
    with tab_inv:
        st.subheader("📊 فاکتورهای فروش (درآینده محقق شده)")
        render_metrics(analyzer, FileType.INVOICES)
        
        col1, col2 = st.columns(2)
        with col1:
            render_profitability(analyzer)
        with col2:
            render_customer_loyalty(analyzer, FileType.INVOICES)
            
        st.markdown("---")
        render_daily_breakdown(analyzer, FileType.INVOICES)
        
    with tab_perf:
        st.subheader("📝 پیش‌فاکتورهای صادر شده")
        render_metrics(analyzer, FileType.PERFORMA)
        
        col1, col2 = st.columns(2)
        with col1:
            render_on_time_payment(analyzer)
        with col2:
            render_top_beneficiaries(analyzer, FileType.PERFORMA)
            
        st.markdown("---")
        render_daily_breakdown(analyzer, FileType.PERFORMA)


def render_debts_tab(analyzer: DataAnalyzer):
    """Render the Debts (Payables) tab."""
    st.header("📤 مدیریت بدهی‌ها و اسناد پرداختنی")
    
    render_metrics(analyzer, FileType.PAYABLE)
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        render_accounts_aging_single(analyzer, FileType.PAYABLE)
    with col2:
        st.subheader("⚠️ چک‌های معوقه")
        # Custom logic for overdue payables
        result = analyzer.analyze(FileType.PAYABLE, AnalysisType.ACCOUNTS_AGING)
        if result and result.data:
            overdue = result.data.get("payables", {}).get("overdue", 0)
            if overdue > 0:
                st.error(f"مبلغ {overdue:,.0f} تومان از تعهدات شما معوق شده است.")
            else:
                st.success("تمامی تعهدات در جریان یا آینده هستند.")
                
    st.markdown("---")
    render_daily_breakdown(analyzer, FileType.PAYABLE)
    render_top_beneficiaries(analyzer, FileType.PAYABLE)


def render_receivables_tab(analyzer: DataAnalyzer):
    """Render the Receivables tab."""
    st.header("📥 مدیریت مطالبات و اسناد دریافتی")
    
    render_metrics(analyzer, FileType.RECEIVABLE)
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        render_accounts_aging_single(analyzer, FileType.RECEIVABLE)
    with col2:
        st.subheader("⚠️ مطالبات معوقه")
        result = analyzer.analyze(FileType.RECEIVABLE, AnalysisType.ACCOUNTS_AGING)
        if result and result.data:
            overdue = result.data.get("receivables", {}).get("overdue", 0)
            if overdue > 0:
                st.warning(f"مبلغ {overdue:,.0f} تومان از وصولی‌ها معوق شده است.")
            else:
                st.success("تمامی وصولی‌ها در جریان یا تایید شده‌اند.")

    st.markdown("---")
    render_daily_breakdown(analyzer, FileType.RECEIVABLE)
    render_top_beneficiaries(analyzer, FileType.RECEIVABLE)


def main():
    """Main application entry point."""

    # Initialize managers
    data_manager, analyzer, cache_manager = initialize_managers()

    # Sidebar configuration
    with st.sidebar:
        st.title("⚙️ تنظیمات")
        st.markdown("---")
        
        # File operations
        if st.button("🔄 بارگذاری مجدد فایل‌ها", use_container_width=True):
            data_manager.load_all_files(force_reload=True)
            st.success("فایل‌ها مجدداً بارگذاری شدند")

        if st.button("🗑️ حذف حافظه موقت", use_container_width=True):
            cache_manager.clear()
            st.success("حافظه موقت پاک شد")

        st.markdown("---")
        render_cache_info(cache_manager)
        
        st.markdown("---")
        st.info("📊 داشبورد نقدینگی JEC")

    # Main header
    st.title(f"📊 سامانه تحلیل مالی و نقدینگی {PROJECT_COMPANY}")
    
    # Load data
    with st.spinner("در حال بارگذاری..."):
        data_manager.load_all_files()

    # Main Tabs
    main_tabs = st.tabs([
        "🏠 داشبورد جامع (نقدینگی)",
        "📈 گزارش فروش",
        "📤 بدهی‌ها (پرداختنی)",
        "📥 مطالبات (دریافتی)",
        "🔍 کاوش داده"
    ])
    
    with main_tabs[0]:
        render_executive_summary(analyzer)
        st.markdown("---")
        render_cash_flow(analyzer)
        
    with main_tabs[1]:
        render_sales_tab(analyzer)
        
    with main_tabs[2]:
        render_debts_tab(analyzer)
        
    with main_tabs[3]:
        render_receivables_tab(analyzer)
        
    with main_tabs[4]:
        st.subheader("🔍 جستجو و فیلتر پیشرفته داده‌ها")
        file_choice = st.selectbox("انتخاب نوع داده:", [f.label for f in FileType])
        target_file = next(f for f in FileType if f.label == file_choice)
        
        df = data_manager.get_dataframe(target_file)
        if df is not None:
            st.dataframe(df, use_container_width=True)
            render_file_info(data_manager, target_file)


if __name__ == "__main__":
    main()
