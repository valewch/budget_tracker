from abc import ABC, abstractmethod


class BaseParser(ABC):
    """
    Abstract base class for all bank parsers.
    Ensures consistent interface across banks.
    """

    @abstractmethod
    def parse(self, subject, body, message_id=None):
        """
        Must return a standardized transaction dictionary:

        {
            "id": str,
            "bank": str,
            "merchant": str,
            "amount": float,
            "currency": str,
            "date": str,
            "time": str,
            "type": str,
            "valid": bool
        }
        """
        pass

    # ---------- OPTIONAL SHARED HELPERS ----------

    def clean_merchant(self, name):
        """
        Common normalization for merchant names.
        Can be reused by all banks.
        """
        if not name:
            return None

        name = name.lower()
        name = name.replace("*", "")
        return name.strip()