"""
quickbooks_sync.py
------------------
Syncs revenue and expense data between Studio Iridescent's PostgreSQL
database and QuickBooks Online using the QuickBooks Python SDK.

Setup:
    1. Create a QuickBooks Developer account at developer.intuit.com
    2. Create an app and get CLIENT_ID + CLIENT_SECRET
    3. Add credentials to .env
    4. Run: python quickbooks_sync.py --auth   (first time only)
    5. Run: python quickbooks_sync.py --sync

Dependencies:
    pip install python-quickbooks intuit-oauth
"""

import os
import json
import argparse
from datetime import datetime, timedelta
from dotenv import load_dotenv
import sqlalchemy
import pandas as pd

load_dotenv()

QB_CLIENT_ID = os.getenv("QB_CLIENT_ID")
QB_CLIENT_SECRET = os.getenv("QB_CLIENT_SECRET")
QB_REDIRECT_URI = os.getenv("QB_REDIRECT_URI", "http://localhost:8080/callback")
QB_ENVIRONMENT = os.getenv("QB_ENVIRONMENT", "sandbox")
QB_COMPANY_ID = os.getenv("QB_COMPANY_ID")
QB_REFRESH_TOKEN = os.getenv("QB_REFRESH_TOKEN")

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/studio_iridescent")

TOKEN_FILE = ".qb_tokens.json"


def load_tokens() -> dict:
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            return json.load(f)
    return {}


def save_tokens(tokens: dict):
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f, indent=2)
    print(f"Tokens saved to {TOKEN_FILE}")


def get_qb_client():
    try:
        from quickbooks import QuickBooks
        from intuitlib.client import AuthClient

        auth_client = AuthClient(
            client_id=QB_CLIENT_ID,
            client_secret=QB_CLIENT_SECRET,
            redirect_uri=QB_REDIRECT_URI,
            environment=QB_ENVIRONMENT,
        )

        tokens = load_tokens()
        auth_client.refresh_token = tokens.get("refresh_token", QB_REFRESH_TOKEN)
        auth_client.refresh(auth_client.refresh_token)

        save_tokens({
            "access_token": auth_client.access_token,
            "refresh_token": auth_client.refresh_token,
            "expires_in": auth_client.expires_in,
        })

        return QuickBooks(
            auth_client=auth_client,
            refresh_token=auth_client.refresh_token,
            company_id=QB_COMPANY_ID,
        )
    except ImportError:
        print("QuickBooks SDK not installed. Run: pip install python-quickbooks intuit-oauth")
        return None


def fetch_qb_income(client, days_back: int = 30) -> list:
    try:
        from quickbooks.objects.invoice import Invoice
        start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        invoices = Invoice.filter(
            start_position=1,
            max_results=100,
            qb=client,
            TxnDate=f">= {start_date}"
        )
        return [
            {
                "qb_id": inv.Id,
                "amount": float(inv.TotalAmt),
                "date": inv.TxnDate,
                "customer": inv.CustomerRef.name if inv.CustomerRef else "Unknown",
                "status": inv.Balance == 0 and "paid" or "unpaid",
            }
            for inv in invoices
        ]
    except Exception as e:
        print(f"Error fetching QB income: {e}")
        return []


def fetch_qb_expenses(client, days_back: int = 30) -> list:
    try:
        from quickbooks.objects.purchase import Purchase
        purchases = Purchase.filter(start_position=1, max_results=100, qb=client)
        return [
            {
                "qb_id": p.Id,
                "amount": float(p.TotalAmt),
                "date": p.TxnDate,
                "category": p.AccountRef.name if p.AccountRef else "Uncategorized",
                "memo": p.PrivateNote or "",
            }
            for p in purchases
        ]
    except Exception as e:
        print(f"Error fetching QB expenses: {e}")
        return []


def sync_to_database(income: list, expenses: list, engine):
    conn = engine.connect()
    revenue_inserted = 0
    expense_inserted = 0

    for item in income:
        result = conn.execute(
            sqlalchemy.text(
                "SELECT id FROM transactions WHERE description LIKE :qb_id"
            ),
            {"qb_id": f"%QB-{item['qb_id']}%"}
        ).fetchone()

        if not result:
            conn.execute(
                sqlalchemy.text("""
                    INSERT INTO transactions (type, category, amount, description, transaction_date)
                    VALUES ('revenue', 'service', :amount, :desc, :date)
                """),
                {
                    "amount": item["amount"],
                    "desc": f"QuickBooks Invoice QB-{item['qb_id']} — {item['customer']}",
                    "date": item["date"],
                }
            )
            revenue_inserted += 1

    for item in expenses:
        result = conn.execute(
            sqlalchemy.text("SELECT id FROM transactions WHERE description LIKE :qb_id"),
            {"qb_id": f"%QB-{item['qb_id']}%"}
        ).fetchone()

        if not result:
            conn.execute(
                sqlalchemy.text("""
                    INSERT INTO transactions (type, category, amount, description, transaction_date)
                    VALUES ('expense', :category, :amount, :desc, :date)
                """),
                {
                    "category": item["category"],
                    "amount": item["amount"],
                    "desc": f"QB-{item['qb_id']}: {item['memo']}",
                    "date": item["date"],
                }
            )
            expense_inserted += 1

    conn.commit()
    conn.close()
    print(f"Synced: {revenue_inserted} revenue entries, {expense_inserted} expense entries")


def run_auth_flow():
    try:
        from intuitlib.client import AuthClient
        from intuitlib.enums import Scopes

        auth_client = AuthClient(
            client_id=QB_CLIENT_ID,
            client_secret=QB_CLIENT_SECRET,
            redirect_uri=QB_REDIRECT_URI,
            environment=QB_ENVIRONMENT,
        )
        url = auth_client.get_authorization_url([Scopes.ACCOUNTING])
        print(f"\nOpen this URL in your browser:\n{url}\n")
        redirect_response = input("Paste the full redirect URL here: ").strip()

        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(redirect_response)
        params = parse_qs(parsed.query)
        auth_code = params["code"][0]
        realm_id = params["realmId"][0]

        auth_client.get_bearer_token(auth_code, realm_id=realm_id)
        save_tokens({
            "access_token": auth_client.access_token,
            "refresh_token": auth_client.refresh_token,
            "company_id": realm_id,
        })
        print(f"\nAuthorization successful! Company ID: {realm_id}")
        print(f"Add QB_COMPANY_ID={realm_id} to your .env file\n")
    except ImportError:
        print("Run: pip install python-quickbooks intuit-oauth")


def main():
    parser = argparse.ArgumentParser(description="QuickBooks Sync for Studio Iridescent")
    parser.add_argument("--auth", action="store_true", help="Run OAuth2 auth flow (first-time setup)")
    parser.add_argument("--sync", action="store_true", help="Sync QuickBooks data to local DB")
    parser.add_argument("--days", type=int, default=30, help="Days of history to sync")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be synced without writing")
    args = parser.parse_args()

    if args.auth:
        run_auth_flow()
        return

    if args.sync:
        print("Connecting to QuickBooks...")
        client = get_qb_client()
        if not client:
            return

        print(f"Fetching last {args.days} days from QuickBooks...")
        income = fetch_qb_income(client, days_back=args.days)
        expenses = fetch_qb_expenses(client, days_back=args.days)

        print(f"Found {len(income)} income entries, {len(expenses)} expense entries")

        if args.dry_run:
            print("\n--- DRY RUN: Would insert ---")
            for i in income:
                print(f"  [REVENUE] ${i['amount']:.2f} on {i['date']} — {i['customer']}")
            for e in expenses:
                print(f"  [EXPENSE] ${e['amount']:.2f} on {e['date']} — {e['category']}")
            return

        engine = sqlalchemy.create_engine(DB_URL)
        sync_to_database(income, expenses, engine)
        print("QuickBooks sync complete!")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()