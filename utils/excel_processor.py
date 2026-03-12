"""
Excel Processor — Load, parse, and analyze Excel files.
"""

import pandas as pd
import numpy as np
from io import BytesIO



def get_sheet_names(file):
    """Return list of sheet names from an Excel file."""
    try:
        xls = pd.ExcelFile(BytesIO(file.read()), engine="openpyxl")
        file.seek(0)
        return xls.sheet_names
    except Exception:
        file.seek(0)
        return []


def get_basic_stats(df: pd.DataFrame) -> dict:
    """Get high-level dataset statistics."""
    memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "memory_mb": round(memory_mb, 2),
        "total_cells": len(df) * len(df.columns),
        "missing_cells": int(df.isnull().sum().sum()),
        "missing_pct": round(df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100, 1) if len(df) > 0 else 0,
        "duplicate_rows": int(df.duplicated().sum()),
        "numeric_cols": len(df.select_dtypes(include=[np.number]).columns),
        "text_cols": len(df.select_dtypes(include=["object", "category"]).columns),
        "date_cols": len(df.select_dtypes(include=["datetime64"]).columns),
    }


def get_column_analysis(df: pd.DataFrame) -> list:
    """Per-column detailed analysis."""
    analysis = []
    for col in df.columns:
        info = {
            "name": col,
            "dtype": str(df[col].dtype),
            "non_null": int(df[col].notna().sum()),
            "null_count": int(df[col].isnull().sum()),
            "null_pct": round(df[col].isnull().sum() / len(df) * 100, 1) if len(df) > 0 else 0,
            "unique": int(df[col].nunique()),
        }

        if pd.api.types.is_numeric_dtype(df[col]):
            desc = df[col].describe()
            info.update({
                "mean": round(float(desc.get("mean", 0)), 2),
                "median": round(float(df[col].median()), 2) if df[col].notna().any() else 0,
                "std": round(float(desc.get("std", 0)), 2),
                "min": float(desc.get("min", 0)),
                "max": float(desc.get("max", 0)),
                "is_numeric": True,
            })
        else:
            top_values = df[col].value_counts().head(5).to_dict()
            info.update({
                "top_values": {str(k): int(v) for k, v in top_values.items()},
                "is_numeric": False,
            })

        analysis.append(info)
    return analysis


def get_correlation_matrix(df: pd.DataFrame):
    """Return correlation matrix for numeric columns."""
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.empty or len(numeric_df.columns) < 2:
        return None
    return numeric_df.corr()


def detect_data_quality(df: pd.DataFrame) -> list:
    """Return a list of data quality warnings."""
    warnings = []

    # Missing values
    missing = df.isnull().sum()
    cols_with_missing = missing[missing > 0]
    if not cols_with_missing.empty:
        for col, count in cols_with_missing.items():
            pct = round(count / len(df) * 100, 1)
            severity = "🔴" if pct > 50 else ("🟡" if pct > 10 else "🟢")
            warnings.append({
                "type": "Missing Values",
                "severity": severity,
                "message": f"**{col}** has {count} missing values ({pct}%)",
            })

    # Duplicates
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        warnings.append({
            "type": "Duplicates",
            "severity": "🟡",
            "message": f"Dataset has **{dup_count}** duplicate rows ({round(dup_count/len(df)*100,1)}%)",
        })

    # Constant columns
    for col in df.columns:
        if df[col].nunique() <= 1:
            warnings.append({
                "type": "Low Variance",
                "severity": "🟡",
                "message": f"**{col}** has only {df[col].nunique()} unique value(s) — consider removing",
            })

    # High cardinality text columns
    for col in df.select_dtypes(include=["object", "category"]).columns:
        if df[col].nunique() > 0.9 * len(df) and len(df) > 20:
            warnings.append({
                "type": "High Cardinality",
                "severity": "🟡",
                "message": f"**{col}** has very high cardinality ({df[col].nunique()} unique values) — might be an ID column",
            })

    if not warnings:
        warnings.append({
            "type": "All Clear",
            "severity": "✅",
            "message": "No significant data quality issues detected!",
        })

    return warnings


def generate_summary_text(df: pd.DataFrame, max_rows_sample: int = 5) -> str:
    """Generate a concise text summary of the dataset for AI context."""
    stats = get_basic_stats(df)
    lines = [
        f"Dataset Overview: {stats['rows']} rows × {stats['columns']} columns.",
        f"Memory: {stats['memory_mb']} MB. Missing: {stats['missing_pct']}%. Duplicates: {stats['duplicate_rows']}.",
        f"Column types: {stats['numeric_cols']} numeric, {stats['text_cols']} text, {stats['date_cols']} datetime.",
        "",
        "Columns:",
    ]

    for col in df.columns:
        dtype = str(df[col].dtype)
        nulls = df[col].isnull().sum()
        uniques = df[col].nunique()
        line = f"  - {col} ({dtype}): {uniques} unique, {nulls} nulls"

        if pd.api.types.is_numeric_dtype(df[col]) and df[col].notna().any():
            line += f", range [{df[col].min():.2f} – {df[col].max():.2f}], mean={df[col].mean():.2f}"
        elif df[col].dtype == "object":
            top = df[col].value_counts().head(3).index.tolist()
            line += f", top values: {top}"

        lines.append(line)

    lines.append("")
    lines.append(f"Sample data (first {max_rows_sample} rows):")
    lines.append(df.head(max_rows_sample).to_string(index=False))

    return "\n".join(lines)
