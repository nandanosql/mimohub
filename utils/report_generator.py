"""
Report Generator — Create beautiful self-contained HTML reports from DataFrames.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime

from utils.excel_processor import (
    get_basic_stats,
    get_column_analysis,
    get_correlation_matrix,
    detect_data_quality,
)


def generate_html_report(
    df: pd.DataFrame,
    title: str = "Data Analysis Report",
    author: str = "MiMo Hub",
    sections: dict = None,
    file_name: str = "dataset",
) -> str:
    """
    Generate a self-contained HTML report.

    Args:
        df: The DataFrame to analyze.
        title: Report title.
        author: Report author.
        sections: Dict of section toggles, e.g. {"overview": True, "quality": True, ...}
        file_name: Original file name.

    Returns:
        Complete HTML string.
    """
    if sections is None:
        sections = {
            "overview": True,
            "quality": True,
            "columns": True,
            "distributions": True,
            "correlations": True,
            "sample": True,
        }

    stats = get_basic_stats(df)
    now = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    # ── Build sections ───────────────────────────────────────────────────────
    sections_html = []

    # Overview
    if sections.get("overview"):
        sections_html.append(_build_overview_section(stats, file_name))

    # Data Quality
    if sections.get("quality"):
        warnings = detect_data_quality(df)
        sections_html.append(_build_quality_section(warnings))

    # Column Analysis
    if sections.get("columns"):
        col_analysis = get_column_analysis(df)
        sections_html.append(_build_columns_section(col_analysis))

    # Distribution Charts
    if sections.get("distributions"):
        sections_html.append(_build_distribution_section(df))

    # Correlation Heatmap
    if sections.get("correlations"):
        corr = get_correlation_matrix(df)
        if corr is not None:
            sections_html.append(_build_correlation_section(corr))

    # Data Sample
    if sections.get("sample"):
        sections_html.append(_build_sample_section(df))

    body_content = "\n".join(sections_html)

    return _wrap_html(title, author, now, body_content, stats)


# ═══════════════════════════════════════════════════════════════════════════════
# Section Builders
# ═══════════════════════════════════════════════════════════════════════════════

def _build_overview_section(stats, file_name):
    return f"""
    <section class="section">
        <h2 class="section-title"><span class="icon">📊</span> Dataset Overview</h2>
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-value">{stats['rows']:,}</div>
                <div class="kpi-label">Total Rows</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value">{stats['columns']}</div>
                <div class="kpi-label">Columns</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value">{stats['missing_pct']}%</div>
                <div class="kpi-label">Missing Data</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value">{stats['duplicate_rows']:,}</div>
                <div class="kpi-label">Duplicate Rows</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value">{stats['memory_mb']} MB</div>
                <div class="kpi-label">Memory Usage</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value">{stats['numeric_cols']}</div>
                <div class="kpi-label">Numeric Cols</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value">{stats['text_cols']}</div>
                <div class="kpi-label">Text Cols</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value">{stats['date_cols']}</div>
                <div class="kpi-label">Date Cols</div>
            </div>
        </div>
        <p class="meta-note">Source: <strong>{file_name}</strong> &nbsp;|&nbsp; {stats['total_cells']:,} total cells</p>
    </section>"""


def _build_quality_section(warnings):
    cards = ""
    for w in warnings:
        cards += f"""
        <div class="quality-row">
            <span class="q-severity">{w['severity']}</span>
            <span class="q-type">{w['type']}</span>
            <span class="q-msg">{w['message']}</span>
        </div>"""
    return f"""
    <section class="section">
        <h2 class="section-title"><span class="icon">🛡️</span> Data Quality Report</h2>
        <div class="quality-list">{cards}</div>
    </section>"""


def _build_columns_section(col_analysis):
    rows = ""
    for c in col_analysis:
        mean_val = c.get("mean", "—")
        std_val = c.get("std", "—")
        rows += f"""
        <tr>
            <td><strong>{c['name']}</strong></td>
            <td><code>{c['dtype']}</code></td>
            <td>{c['non_null']}</td>
            <td>{c['null_pct']}%</td>
            <td>{c['unique']}</td>
            <td>{mean_val}</td>
            <td>{std_val}</td>
        </tr>"""
    return f"""
    <section class="section">
        <h2 class="section-title"><span class="icon">🔬</span> Column Analysis</h2>
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>Column</th><th>Type</th><th>Non-Null</th>
                        <th>Null %</th><th>Unique</th><th>Mean</th><th>Std</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    </section>"""


def _build_distribution_section(df):
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    charts_html = ""

    # Numeric distributions (top 4)
    for col in numeric_cols[:4]:
        fig = px.histogram(
            df, x=col, nbins=30,
            title=f"Distribution — {col}",
            color_discrete_sequence=["#FF6900"],
            template="plotly_white",
        )
        fig.update_layout(
            plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
            font=dict(family="Inter"), height=350,
            margin=dict(l=30, r=30, t=50, b=30),
        )
        chart_html = pio.to_html(fig, full_html=False, include_plotlyjs=False)
        charts_html += f'<div class="chart-item">{chart_html}</div>'

    # Categorical top values (top 2)
    for col in categorical_cols[:2]:
        vc = df[col].value_counts().head(10).reset_index()
        vc.columns = [col, "Count"]
        fig = px.bar(
            vc, x=col, y="Count",
            title=f"Top Values — {col}",
            color="Count",
            color_continuous_scale=["#FF6900", "#3B82F6", "#10B981"],
            template="plotly_white",
        )
        fig.update_layout(
            plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
            font=dict(family="Inter"), height=350,
            margin=dict(l=30, r=30, t=50, b=30),
            showlegend=False,
        )
        chart_html = pio.to_html(fig, full_html=False, include_plotlyjs=False)
        charts_html += f'<div class="chart-item">{chart_html}</div>'

    if not charts_html:
        return ""

    return f"""
    <section class="section">
        <h2 class="section-title"><span class="icon">📈</span> Distributions & Top Values</h2>
        <div class="chart-grid">{charts_html}</div>
    </section>"""


def _build_correlation_section(corr):
    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns.tolist(),
        y=corr.columns.tolist(),
        colorscale=[[0, "#FFF7ED"], [0.5, "#FF6900"], [1, "#10B981"]],
        zmin=-1, zmax=1,
        text=corr.round(2).values,
        texttemplate="%{text}",
        textfont=dict(size=10),
    ))
    fig.update_layout(
        template="plotly_white",
        plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
        font=dict(family="Inter"), height=500,
        margin=dict(l=20, r=20, t=30, b=20),
    )
    chart_html = pio.to_html(fig, full_html=False, include_plotlyjs=False)
    return f"""
    <section class="section">
        <h2 class="section-title"><span class="icon">🔥</span> Correlation Heatmap</h2>
        {chart_html}
    </section>"""


def _build_sample_section(df, n=15):
    sample_html = df.head(n).to_html(
        classes="data-table", index=False, border=0,
        na_rep="—", max_cols=20,
    )
    return f"""
    <section class="section">
        <h2 class="section-title"><span class="icon">📋</span> Data Sample (First {n} Rows)</h2>
        <div class="table-wrap">{sample_html}</div>
    </section>"""


# ═══════════════════════════════════════════════════════════════════════════════
# HTML Template Wrapper
# ═══════════════════════════════════════════════════════════════════════════════

def _wrap_html(title, author, generated_at, body, stats):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — MiMo Hub</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
        html {{ scroll-behavior: smooth; }}
        body {{
            font-family: 'Inter', -apple-system, sans-serif;
            background: #0B0F1A; color: #E2E8F0; line-height: 1.7;
        }}
        .container {{
            max-width: 1100px; margin: 0 auto;
            padding: 2rem 1.5rem 4rem;
        }}

        /* Hero */
        .hero {{
            text-align: center; padding: 3rem 1rem 2rem;
            margin-bottom: 2.5rem;
            background: linear-gradient(135deg, rgba(255,105,0,0.06) 0%, rgba(59,130,246,0.04) 50%, rgba(16,185,129,0.03) 100%);
            border: 1px solid rgba(255,105,0,0.12); border-radius: 24px;
            position: relative; overflow: hidden;
        }}
        .hero::before {{
            content: ''; position: absolute; top: -50%; left: -50%;
            width: 200%; height: 200%;
            background: conic-gradient(from 0deg, transparent, rgba(255,105,0,0.03), transparent);
            animation: spin 20s linear infinite;
        }}
        @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
        .hero-content {{ position: relative; z-index: 1; }}
        .hero h1 {{
            font-size: 2.4rem; font-weight: 900;
            background: linear-gradient(135deg, #FF6900, #FFB347);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .hero .sub {{ color: #64748B; font-size: 0.95rem; margin-top: 0.3rem; }}
        .hero .meta {{
            display: flex; justify-content: center; gap: 1.5rem;
            margin-top: 1rem; flex-wrap: wrap;
        }}
        .hero .meta span {{
            font-size: 0.78rem; color: #94A3B8; font-weight: 500;
        }}
        .hero .meta span strong {{ color: #CBD5E1; }}

        /* Sections */
        .section {{ margin-bottom: 2.5rem; }}
        .section-title {{
            font-size: 1.4rem; font-weight: 800; color: #F1F5F9;
            display: flex; align-items: center; gap: 0.5rem;
            margin-bottom: 1rem; padding-bottom: 0.5rem;
            border-bottom: 1px solid rgba(255,255,255,0.06);
        }}

        /* KPI Cards */
        .kpi-grid {{
            display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            gap: 0.8rem;
        }}
        .kpi-card {{
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 14px; padding: 1rem 0.6rem;
            text-align: center;
        }}
        .kpi-value {{
            font-size: 1.6rem; font-weight: 900; color: #FF6900;
        }}
        .kpi-label {{
            font-size: 0.68rem; color: #64748B; font-weight: 600;
            text-transform: uppercase; letter-spacing: 0.06em;
            margin-top: 0.3rem;
        }}
        .meta-note {{
            color: #475569; font-size: 0.8rem; margin-top: 0.8rem;
            text-align: center;
        }}

        /* Quality */
        .quality-row {{
            background: rgba(255,255,255,0.025);
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 10px; padding: 0.7rem 1rem;
            margin-bottom: 0.4rem; display: flex; align-items: center; gap: 0.6rem;
        }}
        .q-severity {{ font-size: 1.1rem; flex-shrink: 0; }}
        .q-type {{
            font-weight: 700; color: #CBD5E1; font-size: 0.85rem;
            white-space: nowrap;
        }}
        .q-msg {{ color: #94A3B8; font-size: 0.85rem; }}

        /* Tables */
        .table-wrap {{
            overflow-x: auto; border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.06);
        }}
        table, .data-table {{ width: 100%; border-collapse: collapse; }}
        th {{
            background: rgba(255,255,255,0.04);
            padding: 0.7rem 0.8rem; font-size: 0.75rem;
            font-weight: 700; text-transform: uppercase;
            letter-spacing: 0.05em; color: #94A3B8;
            text-align: left; border-bottom: 1px solid rgba(255,255,255,0.06);
        }}
        td {{
            padding: 0.6rem 0.8rem; font-size: 0.85rem;
            border-bottom: 1px solid rgba(255,255,255,0.03);
            color: #CBD5E1;
        }}
        tr:hover {{ background: rgba(255,255,255,0.02); }}
        code {{
            background: rgba(255,105,0,0.08); color: #FF6900;
            padding: 0.1rem 0.4rem; border-radius: 4px;
            font-size: 0.78rem;
        }}

        /* Charts */
        .chart-grid {{
            display: grid; grid-template-columns: repeat(auto-fill, minmax(450px, 1fr));
            gap: 1rem;
        }}
        .chart-item {{
            background: rgba(255,255,255,0.025);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 14px; padding: 0.8rem;
            overflow: hidden;
        }}

        /* Print button */
        .print-bar {{
            position: sticky; top: 0; z-index: 100;
            background: rgba(11,15,26,0.9); backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(255,255,255,0.06);
            padding: 0.6rem 1.5rem;
            display: flex; justify-content: flex-end; gap: 0.8rem;
            margin-bottom: 1rem;
        }}
        .print-btn {{
            background: linear-gradient(135deg, #FF6900, #E85D00);
            color: white; border: none; border-radius: 8px;
            padding: 0.5rem 1.2rem; font-size: 0.82rem;
            font-weight: 600; cursor: pointer;
            font-family: 'Inter', sans-serif;
            transition: all 0.3s ease;
        }}
        .print-btn:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 15px rgba(255,105,0,0.3);
        }}

        /* Footer */
        .footer {{
            text-align: center; padding: 2rem 0 1rem;
            color: #334155; font-size: 0.75rem;
            border-top: 1px solid rgba(255,255,255,0.04);
            margin-top: 2rem;
        }}

        /* Print styles */
        @media print {{
            body {{ background: white; color: #1E293B; }}
            .print-bar {{ display: none; }}
            .hero {{ border: 1px solid #E2E8F0; }}
            .hero h1 {{
                -webkit-text-fill-color: #FF6900;
                background: none;
            }}
            .kpi-card, .quality-row, .chart-item {{
                border: 1px solid #E2E8F0;
            }}
            .kpi-value {{ color: #FF6900; }}
            .section-title {{ color: #1E293B; }}
            td, th {{ color: #1E293B; }}
            .q-type {{ color: #1E293B; }}
            .q-msg {{ color: #475569; }}
            .hero .sub, .hero .meta span {{ color: #475569; }}
            .meta-note {{ color: #64748B; }}
            .footer {{ color: #94A3B8; }}
        }}

        @media (max-width: 768px) {{
            .hero h1 {{ font-size: 1.6rem; }}
            .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
            .chart-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>

    <div class="print-bar">
        <button class="print-btn" onclick="window.print()">🖨️ Print / Save as PDF</button>
    </div>

    <div class="container">
        <div class="hero">
            <div class="hero-content">
                <h1>{title}</h1>
                <p class="sub">Generated by MiMo Hub — AI-Powered Data Analysis</p>
                <div class="meta">
                    <span>📅 <strong>{generated_at}</strong></span>
                    <span>👤 <strong>{author}</strong></span>
                    <span>📊 <strong>{stats['rows']:,} rows × {stats['columns']} cols</strong></span>
                    <span>💾 <strong>{stats['memory_mb']} MB</strong></span>
                </div>
            </div>
        </div>

        {body}

        <div class="footer">
            <p>Generated by 🧠 MiMo Hub — AI-Powered Excel Analysis & Chat Tool</p>
            <p style="margin-top:0.2rem;">{generated_at} &nbsp;|&nbsp; {author}</p>
        </div>
    </div>

</body>
</html>"""
