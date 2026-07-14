"""
expense_tracker.py
------------------
Analyzes expenses and profitability from the database.
Generates category breakdowns, monthly P&L, and cash flow reports.

Usage:
    python expense_tracker.py
    python expense_tracker.py --month 2024-11
    python expense_tracker.py --export-excel
"""

import argparse
import os
import pandas as pd
import numpy as np
from datetime import datetime
import sqlalchemy
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/studio_iridescent")


def fetch_transactions(engine, month: str = None) -> pd.DataFrame:
    where_clause = ""
    if month:
        where_clause = f"WHERE DATE_TRUNC('month', transaction_date) = DATE '{month}-01'"

    query = f"""
        SELECT
            type,
            category,
            amount,
            description,
            transaction_date
        FROM transactions
        {where_clause}
        ORDER BY transaction_date DESC
    """
    df = pd.read_sql(query, engine)
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    return df


def calculate_pnl(df: pd.DataFrame) -> dict:
    revenue = df[df["type"] == "revenue"]["amount"].sum()
    expenses = df[df["type"] == "expense"]["amount"].sum()
    gross_profit = revenue - expenses
    margin = (gross_profit / revenue * 100) if revenue > 0 else 0

    return {
        "total_revenue": float(revenue),
        "total_expenses": float(expenses),
        "gross_profit": float(gross_profit),
        "profit_margin_pct": round(float(margin), 2),
    }


def expense_by_category(df: pd.DataFrame) -> pd.DataFrame:
    expenses = df[df["type"] == "expense"].copy()
    summary = (
        expenses.groupby("category")["amount"]
        .agg(["sum", "count", "mean"])
        .rename(columns={"sum": "total", "count": "transactions", "mean": "avg_transaction"})
        .sort_values("total", ascending=False)
        .reset_index()
    )
    total = summary["total"].sum()
    summary["pct_of_expenses"] = (summary["total"] / total * 100).round(2)
    return summary


def monthly_cashflow(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["month"] = df["transaction_date"].dt.to_period("M")

    monthly = df.groupby(["month", "type"])["amount"].sum().unstack(fill_value=0).reset_index()
    monthly.columns.name = None

    if "revenue" not in monthly.columns:
        monthly["revenue"] = 0
    if "expense" not in monthly.columns:
        monthly["expense"] = 0

    monthly["net"] = monthly["revenue"] - monthly["expense"]
    monthly["cumulative_net"] = monthly["net"].cumsum()
    monthly["margin_pct"] = (monthly["net"] / monthly["revenue"] * 100).round(2)
    return monthly


def print_report(df: pd.DataFrame, month: str = None):
    pnl = calculate_pnl(df)
    cat_df = expense_by_category(df)
    cashflow = monthly_cashflow(df)

    title = f"P&L Report — {month}" if month else "P&L Report — All Time"
    print("\n" + "=" * 60)
    print(f"  Studio Iridescent | {title}")
    print("=" * 60)
    print(f"  Total Revenue:      ${pnl['total_revenue']:>12,.2f}")
    print(f"  Total Expenses:     ${pnl['total_expenses']:>12,.2f}")
    print(f"  Gross Profit:       ${pnl['gross_profit']:>12,.2f}")
    print(f"  Profit Margin:       {pnl['profit_margin_pct']:>11.1f}%")
    print("-" * 60)
    print("  EXPENSE BREAKDOWN")
    print("-" * 60)
    for _, row in cat_df.iterrows():
        bar = "█" * int(row["pct_of_expenses"] / 5)
        print(f"  {row['category']:<22} ${row['total']:>8,.2f}  {row['pct_of_expenses']:5.1f}%  {bar}")
    print("-" * 60)
    print("  MONTHLY CASH FLOW")
    print("-" * 60)
    for _, row in cashflow.iterrows():
        trend = "▲" if row["net"] >= 0 else "▼"
        print(f"  {str(row['month']):<10}  Rev: ${row['revenue']:>8,.2f}  Exp: ${row['expense']:>8,.2f}  Net: {trend}${abs(row['net']):>8,.2f}")
    print("=" * 60 + "\n")


def export_to_excel(df: pd.DataFrame, output_path: str = "reports/financial_report.xlsx"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pnl = calculate_pnl(df)
    cat_df = expense_by_category(df)
    cashflow = monthly_cashflow(df)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        pd.DataFrame([pnl]).to_excel(writer, sheet_name="P&L Summary", index=False)
        cat_df.to_excel(writer, sheet_name="Expense Categories", index=False)
        cashflow.to_excel(writer, sheet_name="Monthly Cashflow", index=False)
        df.to_excel(writer, sheet_name="Raw Transactions", index=False)

    print(f"Excel report saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Studio Iridescent Expense & Profitability Analyzer")
    parser.add_argument("--month", help="Filter by month (YYYY-MM), e.g. 2024-11")
    parser.add_argument("--export-excel", action="store_true", help="Export Excel report")
    parser.add_argument("--output", default="reports/financial_report.xlsx")
    args = parser.parse_args()

    engine = sqlalchemy.create_engine(DB_URL)
    df = fetch_transactions(engine, month=args.month)

    if df.empty:
        print("No transactions found for the specified period.")
        return

    print_report(df, month=args.month)

    if args.export_excel:
        export_to_excel(df, output_path=args.output)


if __name__ == "__main__":
    main()