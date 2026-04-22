import base64


# -------------------------------------------------
# 1. FETCH MESSAGE IDS (BAC emails only)
# -------------------------------------------------
def fetch_bac_messages(service, max_results=10000):
    """
    Returns Gmail message IDs filtered for BAC emails.
    """

    query = (
        'from:notificacion@notificacionesbaccr.com '
        'subject:"Notificación de transacción"'
        'after:2026/04/01'
    )

    messages = []
    page_token = None
    
    while True:
        response = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results,
            pageToken=page_token
        ).execute()

        messages.extend(response.get("messages", []))

        page_token = response.get("nextPageToken")

        if not page_token:
            break

        if len(messages) >= max_results:
            break

    return messages[:max_results]


# -------------------------------------------------
# 2. EXTRACT BODY (robust for BAC + Gmail formats)
# -------------------------------------------------
def extract_body(payload):
    """
    Robust Gmail body extractor.
    Handles:
    - text/plain
    - text/html
    - deeply nested MIME structures
    """

    def decode(data):
        return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

    # -----------------------------
    # 1. Direct body (rare but possible)
    # -----------------------------
    body_data = payload.get("body", {}).get("data")
    if body_data:
        return decode(body_data)

    # -----------------------------
    # 2. Recursive search in parts
    # -----------------------------
    def walk(parts):
        for part in parts:
            mime = part.get("mimeType", "")

            # Prefer plain text
            if mime == "text/plain":
                data = part.get("body", {}).get("data")
                if data:
                    return decode(data)

            # Fallback to HTML if no plain text
            if mime == "text/html":
                data = part.get("body", {}).get("data")
                if data:
                    return decode(data)

            # Recurse deeper (VERY important for BAC emails)
            if "parts" in part:
                result = walk(part["parts"])
                if result:
                    return result

        return None

    parts = payload.get("parts", [])
    result = walk(parts)

    return result or ""


# -------------------------------------------------
# 3. GET FULL EMAIL (subject + body)
# -------------------------------------------------
def get_email_details(service, msg_id):
    """
    Returns subject + body for a Gmail message.
    """

    msg = service.users().messages().get(
        userId='me',
        id=msg_id,
        format='full'
    ).execute()

    payload = msg.get("payload", {})
    headers = payload.get("headers", [])

    subject = None

    for h in headers:
        if h["name"] == "Subject":
            subject = h["value"]
            break

    body = extract_body(payload)

    return subject, body