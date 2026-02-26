import sqlite3
import pandas as pd

DB_NAME = "stocks.db"


# ---------------------------------------------------
# Initialize Main Stock Table
# ---------------------------------------------------
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS stock_data (
                ticker TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL,
                ma20 REAL,
                PRIMARY KEY (ticker, date)
            )
        """)


# ---------------------------------------------------
# Initialize Pipeline Status Table
# ---------------------------------------------------
def init_pipeline_status():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_status (
                job_name TEXT PRIMARY KEY,
                last_success_time TEXT,
                last_status TEXT
            )
        """)


# ---------------------------------------------------
# Save Data (UPSERT SAFE + BULK)
# ---------------------------------------------------
def save_to_db(data, ticker):

    if data is None or data.empty:
        return

    required_columns = ["Open", "High", "Low", "Close", "Volume", "MA20"]

    for col in required_columns:
        if col not in data.columns:
            raise ValueError(f"Missing required column: {col}")

    data_to_store = data[required_columns].copy()

    data_to_store.columns = [
        "open", "high", "low",
        "close", "volume", "ma20"
    ]

    # Clean datetime format
    data_to_store["date"] = pd.to_datetime(data.index).strftime("%Y-%m-%d %H:%M:%S")
    data_to_store["ticker"] = ticker

    rows = list(
        data_to_store[
            ["ticker", "date", "open", "high",
             "low", "close", "volume", "ma20"]
        ].itertuples(index=False, name=None)
    )

    if not rows:
        return

    with sqlite3.connect(DB_NAME) as conn:
        conn.executemany("""
            INSERT OR REPLACE INTO stock_data
            (ticker, date, open, high, low, close, volume, ma20)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, rows)


# ---------------------------------------------------
# Load Data For Dashboard
# ---------------------------------------------------
def load_from_db(ticker):
    with sqlite3.connect(DB_NAME) as conn:
        df = pd.read_sql("""
            SELECT *
            FROM stock_data
            WHERE ticker=?
            ORDER BY date
        """, conn, params=(ticker,))

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)

    return df


# ---------------------------------------------------
# Get Latest Stored Market Date
# ---------------------------------------------------
def get_latest_date(ticker):

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT MAX(date)
            FROM stock_data
            WHERE ticker=?
        """, (ticker,))
        result = cursor.fetchone()[0]

    return result