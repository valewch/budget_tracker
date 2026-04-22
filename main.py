from gmail.client import get_service
from gmail.fetch import fetch_bac_messages, get_email_details
from parsers.bac import BACParser
from services.processor import process_emails
from storage.db import init_db, insert_transactions, DB_PATH
import sqlite3

def main():

    init_db()
    conn = sqlite3.connect(DB_PATH)
    service = get_service()

    messages = fetch_bac_messages(service)

    emails = []
    for msg in messages:
        subject, body = get_email_details(service, msg["id"])

        emails.append({
            "id": msg["id"],
            "subject": subject,
            "body": body
        })

    parser = BACParser()

    transactions = process_emails(parser, emails, conn)

    insert_transactions(transactions)
    conn.close()

    # print(f"Processed {len(transactions)} transactions")

    # for t in transactions:
    #     print(t)


if __name__ == "__main__":
    main()