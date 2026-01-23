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
    
    .stMetric {
        direction: ltr;
        text-align: left;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 0.75rem;
        color: white;
        margin: 0.5rem 0;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
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


def main():
    """Main application entry point."""

    # Initialize managers
    data_manager, analyzer, cache_manager = initialize_managers()

    # Sidebar configuration
    with st.sidebar:
        st.title("⚙️ تنظیمات")

        st.markdown("---")
        st.subheader("عملیات")

        # File operations
        if st.button("🔄 بارگذاری مجدد فایل‌ها"):
            data_manager.load_all_files(force_reload=True)
            st.success("فایل‌ها مجدداً بارگذاری شدند")

        if st.button("🗑️ حذف حافظه موقت"):
            cache_manager.clear()
            st.success("حافظه موقت پاک شد")

        st.markdown("---")
        render_cache_info(cache_manager)

        st.markdown("---")
        st.subheader("درباره سیستم")
        st.info(
            f"""
            **سیستم تحلیل داده‌های مالی {PROJECT_NAME}**
            
            - تحلیل خودکار پیش‌فاکتور و فاکتور
            - محاسبه نرخ خوش‌قولی مشتریان
            - مدیریت اسناد پرداختنی (چک)
            - نمایش مبالغ به **تومان**
        """
        )

    # Main header
    st.title(f"📊 سیستم مدیریت و تحلیل داده‌های مالی {PROJECT_NAME}")
    st.markdown("گزارشات پیشرفته مدیریتی و تحلیل هوشمند داده‌های فروش و پرداخت")

    # Load all files first
    with st.spinner("در حال بارگذاری داده‌ها..."):
        files = data_manager.load_all_files()
        if not files:
            st.error("❌ فایلی یافت نشد!")
            st.stop()

    st.success(f"✅ {len(files)} فایل با موفقیت بارگذاری شد")
    st.markdown("---")

    # App sections: Reports vs File Analysis
    app_mode = st.radio("انتخاب بخش:", ["گزارش مدیریتی", "تحلیل تفصیلی فایل‌ها"])

    if app_mode == "گزارش مدیریتی":
        render_advanced_report(analyzer)
        st.markdown("---")
        render_on_time_payment(analyzer)
    else:
        # Create tabs for each file type
        tabs = st.tabs([f.label for f in FileType if f in files])

        for idx, file_type in enumerate([f for f in FileType if f in files]):
            with tabs[idx]:
                st.header(f"📈 تحلیل {file_type.label}")

                # Metrics
                render_metrics(analyzer, file_type)
                st.markdown("---")

                # Analysis tabs
                analysis_tabs = st.tabs(
                    [
                        "تجزیه کالبدی",
                        "روند انباشته",
                        "ذینفعان برتر",
                        "وفاداری مشتریان",
                        "اطلاعات فایل",
                    ]
                )

                with analysis_tabs[0]:
                    render_daily_breakdown(analyzer, file_type)

                with analysis_tabs[1]:
                    render_cumulative_analysis(analyzer, file_type)

                with analysis_tabs[2]:
                    render_top_beneficiaries(analyzer, file_type)

                with analysis_tabs[3]:
                    render_customer_loyalty(analyzer, file_type)

                with analysis_tabs[4]:
                    render_file_info(data_manager, file_type)


if __name__ == "__main__":
    main()
