from services.categorizer import Categorizer

def process_emails(parser, emails, db):
    """
    Takes:
        - parser (BACParser, DaviBankParser, etc.)
        - emails: list of {subject, body, id}

    Returns:
        - list of parsed transactions
    """
    categorizer = Categorizer(db)
    transactions = []

    results = []

    for email in emails:
        parsed = parser.parse(
            email["subject"], 
            email["body"], 
            email["id"]
            )
        
        if parsed and parsed.get("valid"):
            parsed["category"] = categorizer.categorize(parsed)
            transactions.append(parsed)


        # print("\n--- PARSED OUTPUT ---")
        # print(parsed)
        try:
            parsed = parser.parse(
                subject=email["subject"],
                body=email["body"],
                message_id=email.get("id")
            )

            # Optional: skip invalid transactions
            if parsed and parsed.get("valid", True):
                results.append(parsed)

        except Exception as e:
            # Don't crash pipeline if one email fails
            print(f"[ERROR] Failed to parse email {email.get('id')}: {e}")

    return results