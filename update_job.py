import logging
from datetime import datetime
import sqlite3
from alerts import send_failure_email
from data_fetcher import fetch_stock_data
from processor import add_indicators
from database import init_db, save_to_db, get_latest_date
from alerts import send_failure_email


# -----------------------------
# Logging Setup 
# -----------------------------
logging.basicConfig(
    filename="pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# -----------------------------
# Pipeline Status Update
# -----------------------------
def update_status(status):
    conn = sqlite3.connect(DB_NAME)

    conn.execute("""
        INSERT OR REPLACE INTO pipeline_status
        VALUES (?, ?, ?)
    """, (
        "stock_update",
        datetime.now().isoformat(),
        status
    ))

    conn.commit()
    conn.close()


# -----------------------------
# Core ETL Logic
# -----------------------------
def run_update_logic():

    ticker = "AAPL"

    init_db()

    latest_db_date = get_latest_date(ticker)

    # lightweight API check
    latest_api_data = fetch_stock_data(ticker, period="1d")
    latest_api_date = str(latest_api_data.index.max())

    if latest_db_date == latest_api_date:
        print("No new data available. Skipping update.")
        return

    print("New data detected. Updating...")

    # fetch real update window
    data = fetch_stock_data(ticker, period="5d")

    data = add_indicators(data)

    save_to_db(data, ticker)


# -----------------------------
# Monitored Execution Wrapper
# -----------------------------
def run_update():

    if not market_is_open():
        logging.info("Market closed. Skipping update.")
        return

    try:
        run_update_logic()
        update_status("SUCCESS")

    except Exception as e:
        update_status("FAILED")
        send_failure_email(str(e))
        raise e


# -----------------------------
# Entry Point
# -----------------------------
if __name__ == "__main__":
    run_update()