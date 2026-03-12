"""
📄 Export Report — MiMo Hub
Generate and download beautiful analysis reports.
"""

import streamlit as st

from utils.shared_ui import load_css, render_sidebar, get_current_df, show_no_data_message
from utils.report_generator import generate_html_report
from utils.excel_processor import get_basic_stats

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Export Report — MiMo Hub",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()
render_sidebar()

# ─── Page Header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header" style="padding:1.2rem 1rem 0.8rem;">
    <h1 style="font-size:1.8rem;">📄 Export Report</h1>
    <p>Generate a beautiful, self-contained HTML report — download or print as PDF</p>
</div>
""", unsafe_allow_html=True)

# ─── Load Data ──────────────────────────────────────────────────────────────────
df, error = get_current_df()

if df is None:
    if error == "no_file":
        show_no_data_message()
    else:
        st.error(f"❌ Failed to load file: {error}")
    st.stop()

stats = get_basic_stats(df)
file_name = st.session_state.get("file_name", "dataset")

# ─── Report Configuration ───────────────────────────────────────────────────────
st.markdown("### ⚙️ Report Settings")

config_col1, config_col2 = st.columns(2)

with config_col1:
    report_title = st.text_input(
        "📝 Report Title",
        value=f"Analysis Report — {file_name}",
        placeholder="Enter report title",
        key="report_title",
    )
    report_author = st.text_input(
        "👤 Author",
        value="MiMo Hub",
        placeholder="Your name or company",
        key="report_author",
    )

with config_col2:
    st.markdown("**📋 Include Sections:**")
    sec_overview = st.checkbox("📊 Dataset Overview", value=True, key="sec_overview")
    sec_quality = st.checkbox("🛡️ Data Quality Report", value=True, key="sec_quality")
    sec_columns = st.checkbox("🔬 Column Analysis", value=True, key="sec_columns")
    sec_distributions = st.checkbox("📈 Distribution Charts", value=True, key="sec_dist")
    sec_correlations = st.checkbox("🔥 Correlation Heatmap", value=True, key="sec_corr")
    sec_sample = st.checkbox("📋 Data Sample", value=True, key="sec_sample")

sections = {
    "overview": sec_overview,
    "quality": sec_quality,
    "columns": sec_columns,
    "distributions": sec_distributions,
    "correlations": sec_correlations,
    "sample": sec_sample,
}

enabled_count = sum(sections.values())

# ─── Preview ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 👁️ Report Preview")

if enabled_count == 0:
    st.warning("⚠️ Select at least one section to include in the report.")
    st.stop()

# Preview summary cards
preview_cols = st.columns(4)
with preview_cols[0]:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{enabled_count}</div>
        <div class="metric-label">Sections</div>
    </div>""", unsafe_allow_html=True)
with preview_cols[1]:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{stats['rows']:,}</div>
        <div class="metric-label">Rows</div>
    </div>""", unsafe_allow_html=True)
with preview_cols[2]:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{stats['columns']}</div>
        <div class="metric-label">Columns</div>
    </div>""", unsafe_allow_html=True)
with preview_cols[3]:
    has_charts = sections.get("distributions") or sections.get("correlations")
    chart_count = (1 if sections.get("correlations") else 0) + (min(6, len(df.select_dtypes(include=["number", "object", "category"]).columns)) if sections.get("distributions") else 0)
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{chart_count}</div>
        <div class="metric-label">Charts</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Section preview list
section_names = {
    "overview": "📊 Dataset Overview — KPI metrics and statistics",
    "quality": "🛡️ Data Quality — Missing values, duplicates, warnings",
    "columns": "🔬 Column Analysis — Type, nulls, unique counts, statistics",
    "distributions": "📈 Distributions — Histograms and bar charts",
    "correlations": "🔥 Correlations — Heatmap of numeric column relationships",
    "sample": "📋 Data Sample — First 15 rows of the dataset",
}

for key, name in section_names.items():
    status = "✅" if sections.get(key) else "⬜"
    st.markdown(f"&nbsp;&nbsp;{status}&nbsp;&nbsp;{name}")

# ─── Generate & Download ────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📥 Download Report")

download_col1, download_col2, download_col3 = st.columns(3)

with download_col1:
    # HTML Report
    with st.spinner("🔄 Generating HTML report..."):
        html_report = generate_html_report(
            df=df,
            title=report_title,
            author=report_author,
            sections=sections,
            file_name=file_name,
        )

    st.download_button(
        label="📥 Download HTML Report",
        data=html_report,
        file_name=f"{file_name.rsplit('.', 1)[0]}_report.html",
        mime="text/html",
        use_container_width=True,
        type="primary",
    )
    st.caption("Self-contained HTML with interactive Plotly charts")

with download_col2:
    # CSV Data Export
    csv_data = df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV Data",
        data=csv_data,
        file_name=f"{file_name.rsplit('.', 1)[0]}_data.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.caption("Raw data exported as CSV file")

with download_col3:
    # Print to PDF instructions
    st.markdown("""
    <div class="metric-card" style="padding:1rem;">
        <div class="metric-value" style="font-size:1.5rem;">🖨️</div>
        <div class="metric-label" style="margin-top:0.3rem;">Save as PDF</div>
        <p style="color:#64748B;font-size:0.78rem;margin-top:0.5rem;">
            Open the HTML report in your browser, then click the <strong>"🖨️ Print / Save as PDF"</strong> button at the top.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ─── Tip ────────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.info(
    "💡 **Tip:** The HTML report includes a built-in **Print / Save as PDF** button. "
    "Open the downloaded HTML in your browser and click it to get a clean PDF version."
)
