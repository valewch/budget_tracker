-- Transaction table
CREATE TABLE IF NOT EXISTS transactions (
    id TEXT PRIMARY KEY,              -- Gmail message_id (deduplication key)
    bank TEXT NOT NULL,               -- BAC, DaviBank, etc.
    merchant TEXT,
    amount REAL,
    currency TEXT,
    date TEXT,
    type TEXT,
    category TEXT,                        -- expense / income / payment
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Category overrides (manual corrections)
CREATE TABLE IF NOT EXISTS category_overrides (
    merchant TEXT PRIMARY KEY,
    category TEXT
);