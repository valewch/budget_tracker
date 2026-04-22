import re
from bs4 import BeautifulSoup
from parsers.base import BaseParser
import unicodedata
from datetime import datetime


class BACParser(BaseParser):
    """
    Parser for BAC Credomatic transaction emails.
    Extracts structured transaction data from HTML emails.
    """

    def normalize_date(self, raw_date: str):
        if not raw_date:
            return None

        # Normalize spacing and commas
        cleaned = raw_date.lower()
        cleaned = cleaned.replace(",", " ")
        cleaned = " ".join(cleaned.split())

        # Map Spanish months → numbers
        months = {
            "ene": "01", "feb": "02", "mar": "03", "abr": "04",
            "may": "05", "jun": "06", "jul": "07", "ago": "08",
            "sep": "09", "oct": "10", "nov": "11", "dic": "12"
        }

        # Example cleaned: "abr 16 2026 18:49"
        match = re.search(r"(\w{3}) (\d{1,2}) (\d{4}) (\d{2}:\d{2})", cleaned)

        if not match:
            return None

        month_str, day, year, time = match.groups()

        month = months.get(month_str)

        if not month:
            return None

        # Build datetime
        try:
            dt = datetime.strptime(f"{year}-{month}-{day} {time}", "%Y-%m-%d %H:%M")
            return dt.strftime("%Y-%m-%d %H:%M")
        except:
            return None
        
    def normalize_key(self, key: str) -> str:
        key = key.lower()

        # remove accents (transacción → transaccion)
        key = unicodedata.normalize("NFKD", key).encode("ascii", "ignore").decode("utf-8")

        # remove ":" and extra spaces
        key = key.replace(":", "").strip()

        # collapse multiple spaces
        key = " ".join(key.split())

        return key
    # -----------------------------
    # MAIN ENTRY POINT
    # -----------------------------
    def parse(self, subject, body, message_id=None):

        html_data = self.parse_html_body(body)
        subject_data = self.parse_subject(subject)

        merchant = html_data.get("comercio")

        monto_raw = html_data.get("monto")

        raw_date = html_data.get("fecha")

        normalized_date = self.normalize_date(raw_date)

        parsed = {
            "id": message_id,
            "bank": "BAC",
            "merchant": self.clean_merchant(merchant),

            # FIXED HERE
            "amount": self.parse_amount(monto_raw),
            "currency": self.extract_currency(monto_raw),

            "date": normalized_date,
            "time": subject_data.get("time"),
            "type": html_data.get("tipo de transaccion"),
        }

        parsed["valid"] = all([
            parsed["merchant"],
            parsed["amount"],
            parsed["currency"]
        ])

        return parsed

    # -----------------------------
    # SUBJECT PARSER (light fallback)
    # -----------------------------
    def parse_subject(self, subject):
        """
        Example:
        Notificación de transacción PARQUEO MAGALY 18-04-2026 - 12:23
        """

        if not subject:
            return {}

        pattern = r"transaccion\s+(.+?)\s+(\d{2}-\d{2}-\d{4})\s*-\s*(\d{2}:\d{2})"
        match = re.search(pattern, subject.lower())

        if not match:
            return {}

        return {
            "merchant": match.group(1).strip(),
            "date": match.group(2),
            "time": match.group(3)
        }
    
    def parse_amount(self, text):
        if not text:
            return None

        match = re.search(r"([\d,]+\.\d{2})", text)
        if match:
            return float(match.group(1).replace(",", ""))

        return None
    
    def extract_currency(self, text):
        if not text:
            return None

        if "crc" in text.lower():
            return "CRC"
        if "usd" in text.lower():
            return "USD"

        return None

    # -----------------------------
    # HTML PARSER (MAIN LOGIC)
    # -----------------------------

    def parse_html_body(self, body):

        soup = BeautifulSoup(body, "html.parser")

        data = {}

        rows = soup.find_all("tr")

        for row in rows:
            cols = row.find_all("td")

            if len(cols) < 2:
                continue

            key = cols[0].get_text(" ", strip=True)
            value = cols[1].get_text(" ", strip=True)

            key = self.normalize_key(key)

            # ignore junk rows
            if not key or not value:
                continue

            data[key] = value

        # print("DEBUG KEYS:", data.keys())
        # print("DEBUG DATA:", data)

        return data
    