"""
revenue_forecast.py
-------------------
Pulls transaction history from PostgreSQL and generates a 90-day revenue
forecast using linear regression + seasonal decomposition.

Usage:
    python revenue_forecast.py --output reports/forecast.csv
"""

import argparse
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import sqlalchemy
from dotenv import load_dotenv
import json

load_dotenv()

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/studio_iridescent")


def fetch_revenue_history(engine) -> pd.DataFrame:
    query = """
        SELECT
            DATE_TRUNC('day', transaction_date) AS date,
            SUM(amount) AS daily_revenue
        FROM transactions
        WHERE type = 'revenue'
        GROUP BY DATE_TRUNC('day', transaction_date)
        ORDER BY date ASC
    """
    return pd.read_sql(query, engine)


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["day_of_week"] = df["date"].dt.dayofweek
    df["month"] = df["date"].dt.month
    df["day_of_year"] = df["date"].dt.dayofyear
    df["days_since_start"] = (df["date"] - df["date"].min()).dt.days
    return df


def train_forecast_model(df: pd.DataFrame):
    features = ["days_since_start", "day_of_week", "month"]
    X = df[features].values
    y = df["daily_revenue"].values

    poly = PolynomialFeatures(degree=2, include_bias=False)
    X_poly = poly.fit_transform(X)

    model = LinearRegression()
    model.fit(X_poly, y)

    return model, poly, features


def generate_forecast(model, poly, df: pd.DataFrame, days_ahead: int = 90) -> pd.DataFrame:
    last_date = df["date"].max()
    last_days = df["days_since_start"].max()

    future_dates = [last_date + timedelta(days=i + 1) for i in range(days_ahead)]
    future_df = pd.DataFrame({"date": future_dates})
    future_df["days_since_start"] = last_days + np.arange(1, days_ahead + 1)
    future_df["day_of_week"] = future_df["date"].dt.dayofweek
    future_df["month"] = future_df["date"].dt.month

    features = ["days_since_start", "day_of_week", "month"]
    X_future = poly.transform(future_df[features].values)
    future_df["forecasted_revenue"] = model.predict(X_future).clip(min=0)

    return future_df[["date", "forecasted_revenue"]]


def print_summary(forecast_df: pd.DataFrame, historical_df: pd.DataFrame):
    total_forecast = forecast_df["forecasted_revenue"].sum()
    avg_daily = forecast_df["forecasted_revenue"].mean()
    hist_avg = historical_df["daily_revenue"].mean()

    print("\n" + "=" * 50)
    print("  Studio Iridescent — Revenue Forecast")
    print("=" * 50)
    print(f"  Historical daily avg:    ${hist_avg:>10,.2f}")
    print(f"  Forecasted daily avg:    ${avg_daily:>10,.2f}")
    print(f"  90-Day revenue forecast: ${total_forecast:>10,.2f}")
    print(f"  Growth trend:            {((avg_daily - hist_avg) / hist_avg * 100):>+.1f}%")
    print("=" * 50 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Studio Iridescent Revenue Forecaster")
    parser.add_argument("--output", default="reports/forecast.csv", help="Output CSV path")
    parser.add_argument("--days", type=int, default=90, help="Days to forecast")
    parser.add_argument("--json", action="store_true", help="Also output JSON")
    args = parser.parse_args()

    print("Connecting to database...")
    engine = sqlalchemy.create_engine(DB_URL)

    print("Fetching revenue history...")
    df = fetch_revenue_history(engine)

    if len(df) < 14:
        print("WARNING: Less than 14 days of data. Forecast may be unreliable.")

    df = add_time_features(df)
    print(f"Training model on {len(df)} days of data...")
    model, poly, features = train_forecast_model(df)

    forecast_df = generate_forecast(model, poly, df, days_ahead=args.days)
    print_summary(forecast_df, df)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    forecast_df.to_csv(args.output, index=False)
    print(f"Forecast saved to {args.output}")

    if args.json:
        json_path = args.output.replace(".csv", ".json")
        forecast_df["date"] = forecast_df["date"].astype(str)
        forecast_df.to_json(json_path, orient="records", indent=2)
        print(f"JSON saved to {json_path}")


if __name__ == "__main__":
    main()