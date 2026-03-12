"""
📊 Data Analysis — MiMo Hub
Automated stats, visualizations, and data quality analysis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.shared_ui import load_css, render_sidebar, get_current_df, show_no_data_message
from utils.excel_processor import (
    get_basic_stats,
    get_column_analysis,
    get_correlation_matrix,
    detect_data_quality,
)

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Data Analysis — MiMo Hub",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()
render_sidebar()

# ─── Page Header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header" style="padding:1.2rem 1rem 0.8rem;">
    <h1 style="font-size:1.8rem;">📊 Data Analysis</h1>
    <p>Automated statistics, visualizations, and data quality insights</p>
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

# ─── Cached Analysis ────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def cached_stats(_hash, df):
    return get_basic_stats(df)

@st.cache_data(show_spinner=False)
def cached_columns(_hash, df):
    return get_column_analysis(df)

@st.cache_data(show_spinner=False)
def cached_quality(_hash, df):
    return detect_data_quality(df)

@st.cache_data(show_spinner=False)
def cached_corr(_hash, df):
    return get_correlation_matrix(df)

_hash = hash(st.session_state.get("file_bytes", b""))
stats = cached_stats(_hash, df)
col_analysis = cached_columns(_hash, df)
quality_warnings = cached_quality(_hash, df)

# ─── KPI Metrics ────────────────────────────────────────────────────────────────
m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{stats['rows']:,}</div>
        <div class="metric-label">Total Rows</div>
    </div>""", unsafe_allow_html=True)
with m2:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{stats['columns']}</div>
        <div class="metric-label">Columns</div>
    </div>""", unsafe_allow_html=True)
with m3:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{stats['missing_pct']}%</div>
        <div class="metric-label">Missing Data</div>
    </div>""", unsafe_allow_html=True)
with m4:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{stats['duplicate_rows']:,}</div>
        <div class="metric-label">Duplicate Rows</div>
    </div>""", unsafe_allow_html=True)
with m5:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{stats['memory_mb']} MB</div>
        <div class="metric-label">Memory Usage</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Data Preview ───────────────────────────────────────────────────────────────
with st.expander("📋 Data Preview", expanded=True):
    rows_to_show = st.slider("Rows to display", 5, min(100, len(df)), 10, key="preview_slider")
    st.dataframe(df.head(rows_to_show), use_container_width=True, height=400)

# ─── Visualizations ─────────────────────────────────────────────────────────────
st.markdown("### 📈 Visualizations")

numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    if numeric_cols:
        selected_num_col = st.selectbox("Distribution of", numeric_cols, key="hist_col")
        fig_hist = px.histogram(
            df, x=selected_num_col, nbins=30,
            title=f"Distribution — {selected_num_col}",
            color_discrete_sequence=["#FF6900"],
            template="plotly_white",
        )
        fig_hist.update_layout(
            plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
            font=dict(family="Inter"),
            margin=dict(l=20, r=20, t=50, b=20),
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("No numeric columns for distribution chart.")

with chart_col2:
    if categorical_cols:
        selected_cat_col = st.selectbox("Top values of", categorical_cols, key="bar_col")
        value_counts = df[selected_cat_col].value_counts().head(10).reset_index()
        value_counts.columns = [selected_cat_col, "Count"]
        fig_bar = px.bar(
            value_counts, x=selected_cat_col, y="Count",
            title=f"Top Values — {selected_cat_col}",
            color="Count",
            color_continuous_scale=["#FF6900", "#3B82F6", "#10B981"],
            template="plotly_white",
        )
        fig_bar.update_layout(
            plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
            font=dict(family="Inter"),
            margin=dict(l=20, r=20, t=50, b=20),
            showlegend=False,
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No categorical columns for bar chart.")

# ─── Correlation Heatmap ────────────────────────────────────────────────────────
corr = cached_corr(_hash, df)
if corr is not None:
    st.markdown("### 🔥 Correlation Heatmap")
    fig_corr = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns.tolist(),
        y=corr.columns.tolist(),
        colorscale=[[0, "#FFF7ED"], [0.5, "#FF6900"], [1, "#10B981"]],
        zmin=-1, zmax=1,
        text=corr.round(2).values,
        texttemplate="%{text}",
        textfont=dict(size=10),
    ))
    fig_corr.update_layout(
        template="plotly_white",
        plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
        font=dict(family="Inter"), height=500,
        margin=dict(l=20, r=20, t=30, b=20),
    )
    st.plotly_chart(fig_corr, use_container_width=True)

# ─── Data Quality ───────────────────────────────────────────────────────────────
st.markdown("### 🛡️ Data Quality Report")
for w in quality_warnings:
    st.markdown(
        f'<div class="quality-card">{w["severity"]} &nbsp; '
        f'<b>{w["type"]}</b> — {w["message"]}</div>',
        unsafe_allow_html=True,
    )

# ─── Column Details ─────────────────────────────────────────────────────────────
with st.expander("🔬 Column Details"):
    col_df = pd.DataFrame([
        {
            "Column": c["name"],
            "Type": c["dtype"],
            "Non-Null": c["non_null"],
            "Null %": c["null_pct"],
            "Unique": c["unique"],
            "Mean": c.get("mean", "—"),
            "Std": c.get("std", "—"),
        }
        for c in col_analysis
    ])
    st.dataframe(col_df, use_container_width=True, hide_index=True)
