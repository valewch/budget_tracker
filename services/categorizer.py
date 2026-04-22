
class Categorizer:

    def __init__(self, db):
        self.db = db

        self.rules = {
            "food": ["pasty", "restaurante", "soda", "cafe"],
            "groceries": ["walmart", "automercado", "mas x menos", "fresh market", "am pm", "tierra bendita"],
            "transport": ["gasolinera", "shell"],
            "delivery": ['uber eats'],
            "subscriptions": ["netflix", "spotify", "apple", "seguro"],
        }

    def get_override(self, merchant):
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT category FROM category_overrides WHERE merchant = ?",
            (merchant,)
        )
        row = cursor.fetchone()
        return row[0] if row else None

    def categorize(self, tx):
        merchant = (tx.get("merchant") or "").lower().strip()

        # 1. Check overrides
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT category FROM category_overrides WHERE merchant = ?",
            (merchant,)
        )
        row = cursor.fetchone()

        if row:
            return row["category"]

        # 2. Simple rules (starter rules)
        if any(word in merchant for word in ["walmart", "automercado", "mas x menos"]):
            return "groceries"

        if any(word in merchant for word in ["uber", "didi"]):
            return "transport"

        if any(word in merchant for word in ["netflix", "spotify"]):
            return "subscriptions"

        if any(word in merchant for word in ["pasty", "sukha", "tierra bendita"]):
            return "food"

        # 3. Fallback (IMPORTANT)
        return "other"