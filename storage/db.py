import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "transactions.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    # print("Initializing DB...")
    # print("DB PATH:", DB_PATH)
    # print("SCHEMA PATH:", SCHEMA_PATH)

    conn = get_connection()
    cursor = conn.cursor()

    with open(SCHEMA_PATH, "r") as f:
        schema = f.read()
        # print("SCHEMA LOADED:\n", schema)
        cursor.executescript(schema)

    conn.commit()
    conn.close()

def insert_transaction(tx):
    """
    Inserts a transaction.
    Automatically ignores duplicates via PRIMARY KEY.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
            INSERT OR IGNORE INTO transactions (
                id, bank, merchant, amount, currency, date, type, category
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tx["id"],
            tx["bank"],
            tx["merchant"],
            tx["amount"],
            tx["currency"],
            tx["date"],
            tx["type"],
            tx.get("category")
        ))

    conn.commit()
    conn.close()

def insert_transactions(transactions):
    for tx in transactions:
        insert_transaction(tx)