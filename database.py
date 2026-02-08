"""Database module for NekoBudget application."""

import sqlite3
import os
from datetime import datetime
from typing import Optional


class Database:
    """Handle all database operations for the budget app."""

    def __init__(self, db_path: str = "nekobudget.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        """Create all necessary tables."""
        cursor = self.conn.cursor()

        # Monthly recurring bills
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monthly_bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                amount REAL NOT NULL,
                due_day INTEGER,
                category TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Paychecks
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS paychecks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                date TEXT NOT NULL,
                source TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Purchases
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                amount REAL NOT NULL,
                date TEXT NOT NULL,
                category TEXT,
                receipt_path TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Savings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS savings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                current_amount REAL DEFAULT 0,
                goal_amount REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Savings transactions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS savings_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                savings_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                transaction_type TEXT NOT NULL,
                date TEXT NOT NULL,
                notes TEXT,
                FOREIGN KEY (savings_id) REFERENCES savings(id)
            )
        """)

        # Monthly pages/budgets
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monthly_pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(year, month)
            )
        """)

        # Paid bills tracking (per month)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS paid_bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_id INTEGER NOT NULL,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                paid_date TEXT NOT NULL,
                FOREIGN KEY (bill_id) REFERENCES monthly_bills(id),
                UNIQUE(bill_id, year, month)
            )
        """)

        # Bill Account (separate from savings, for bill money)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bill_account (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                balance REAL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Bill Account transactions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bill_account_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                transaction_type TEXT NOT NULL,
                date TEXT NOT NULL,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Ensure bill account exists (single row)
        cursor.execute("SELECT COUNT(*) FROM bill_account")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO bill_account (balance) VALUES (0)")

        self.conn.commit()

    # Monthly Bills Methods
    def add_monthly_bill(self, name: str, amount: float, due_day: Optional[int] = None,
                         category: Optional[str] = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO monthly_bills (name, amount, due_day, category)
            VALUES (?, ?, ?, ?)
        """, (name, amount, due_day, category))
        self.conn.commit()
        return cursor.lastrowid

    def get_monthly_bills(self, active_only: bool = True) -> list:
        cursor = self.conn.cursor()
        if active_only:
            cursor.execute("SELECT * FROM monthly_bills WHERE is_active = 1 ORDER BY due_day")
        else:
            cursor.execute("SELECT * FROM monthly_bills ORDER BY due_day")
        return [dict(row) for row in cursor.fetchall()]

    def update_monthly_bill(self, bill_id: int, name: str, amount: float,
                            due_day: Optional[int] = None, category: Optional[str] = None):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE monthly_bills SET name = ?, amount = ?, due_day = ?, category = ?
            WHERE id = ?
        """, (name, amount, due_day, category, bill_id))
        self.conn.commit()

    def delete_monthly_bill(self, bill_id: int):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE monthly_bills SET is_active = 0 WHERE id = ?", (bill_id,))
        self.conn.commit()

    def get_total_monthly_bills(self) -> float:
        cursor = self.conn.cursor()
        cursor.execute("SELECT SUM(amount) FROM monthly_bills WHERE is_active = 1")
        result = cursor.fetchone()[0]
        return result if result else 0.0

    # Paid Bills Methods
    def mark_bill_paid(self, bill_id: int, year: int, month: int, paid_date: str):
        """Mark a bill as paid for a specific month."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO paid_bills (bill_id, year, month, paid_date)
            VALUES (?, ?, ?, ?)
        """, (bill_id, year, month, paid_date))
        self.conn.commit()

    def mark_bill_unpaid(self, bill_id: int, year: int, month: int):
        """Mark a bill as unpaid for a specific month."""
        cursor = self.conn.cursor()
        cursor.execute("""
            DELETE FROM paid_bills WHERE bill_id = ? AND year = ? AND month = ?
        """, (bill_id, year, month))
        self.conn.commit()

    def is_bill_paid(self, bill_id: int, year: int, month: int) -> bool:
        """Check if a bill is paid for a specific month."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 1 FROM paid_bills WHERE bill_id = ? AND year = ? AND month = ?
        """, (bill_id, year, month))
        return cursor.fetchone() is not None

    def get_paid_bill_ids(self, year: int, month: int) -> set:
        """Get set of bill IDs that are paid for a specific month."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT bill_id FROM paid_bills WHERE year = ? AND month = ?
        """, (year, month))
        return {row[0] for row in cursor.fetchall()}

    def get_unpaid_bills_total(self, year: int, month: int) -> float:
        """Get total amount of unpaid bills for a specific month."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT SUM(amount) FROM monthly_bills
            WHERE is_active = 1 AND id NOT IN (
                SELECT bill_id FROM paid_bills WHERE year = ? AND month = ?
            )
        """, (year, month))
        result = cursor.fetchone()[0]
        return result if result else 0.0

    # Bill Account Methods
    def get_bill_account_balance(self) -> float:
        """Get the current bill account balance."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT balance FROM bill_account LIMIT 1")
        result = cursor.fetchone()
        return result[0] if result else 0.0

    def add_bill_account_transaction(self, amount: float, transaction_type: str,
                                      date: str, notes: Optional[str] = None) -> int:
        """Add a transaction to the bill account."""
        cursor = self.conn.cursor()

        # Add transaction record
        cursor.execute("""
            INSERT INTO bill_account_transactions (amount, transaction_type, date, notes)
            VALUES (?, ?, ?, ?)
        """, (amount, transaction_type, date, notes))

        # Update balance
        if transaction_type == "deposit":
            cursor.execute("UPDATE bill_account SET balance = balance + ?", (amount,))
        else:  # withdraw
            cursor.execute("UPDATE bill_account SET balance = balance - ?", (amount,))

        self.conn.commit()
        return cursor.lastrowid

    def get_bill_account_transactions(self, limit: int = 50) -> list:
        """Get bill account transaction history."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM bill_account_transactions
            ORDER BY date DESC, id DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def set_bill_account_balance(self, balance: float):
        """Set the bill account balance directly (for corrections)."""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE bill_account SET balance = ?", (balance,))
        self.conn.commit()

    # Paycheck Methods
    def add_paycheck(self, amount: float, date: str, source: Optional[str] = None,
                     notes: Optional[str] = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO paychecks (amount, date, source, notes)
            VALUES (?, ?, ?, ?)
        """, (amount, date, source, notes))
        self.conn.commit()
        return cursor.lastrowid

    def get_paychecks(self, year: Optional[int] = None, month: Optional[int] = None) -> list:
        cursor = self.conn.cursor()
        if year and month:
            cursor.execute("""
                SELECT * FROM paychecks
                WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
                ORDER BY date DESC
            """, (str(year), f"{month:02d}"))
        else:
            cursor.execute("SELECT * FROM paychecks ORDER BY date DESC")
        return [dict(row) for row in cursor.fetchall()]

    def delete_paycheck(self, paycheck_id: int):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM paychecks WHERE id = ?", (paycheck_id,))
        self.conn.commit()

    # Purchase Methods
    def add_purchase(self, name: str, amount: float, date: str, category: Optional[str] = None,
                     receipt_path: Optional[str] = None, notes: Optional[str] = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO purchases (name, amount, date, category, receipt_path, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, amount, date, category, receipt_path, notes))
        self.conn.commit()
        return cursor.lastrowid

    def get_purchases(self, year: Optional[int] = None, month: Optional[int] = None) -> list:
        cursor = self.conn.cursor()
        if year and month:
            cursor.execute("""
                SELECT * FROM purchases
                WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
                ORDER BY date DESC
            """, (str(year), f"{month:02d}"))
        else:
            cursor.execute("SELECT * FROM purchases ORDER BY date DESC")
        return [dict(row) for row in cursor.fetchall()]

    def delete_purchase(self, purchase_id: int):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM purchases WHERE id = ?", (purchase_id,))
        self.conn.commit()

    # Savings Methods
    def add_savings_account(self, name: str, current_amount: float = 0,
                            goal_amount: Optional[float] = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO savings (name, current_amount, goal_amount)
            VALUES (?, ?, ?)
        """, (name, current_amount, goal_amount))
        self.conn.commit()
        return cursor.lastrowid

    def get_savings_accounts(self) -> list:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM savings ORDER BY name")
        return [dict(row) for row in cursor.fetchall()]

    def update_savings_account(self, savings_id: int, name: str,
                               goal_amount: Optional[float] = None):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE savings SET name = ?, goal_amount = ? WHERE id = ?
        """, (name, goal_amount, savings_id))
        self.conn.commit()

    def add_savings_transaction(self, savings_id: int, amount: float,
                                transaction_type: str, date: str,
                                notes: Optional[str] = None) -> int:
        cursor = self.conn.cursor()
        # Add transaction
        cursor.execute("""
            INSERT INTO savings_transactions (savings_id, amount, transaction_type, date, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (savings_id, amount, transaction_type, date, notes))

        # Update current amount
        if transaction_type == "deposit":
            cursor.execute("""
                UPDATE savings SET current_amount = current_amount + ? WHERE id = ?
            """, (amount, savings_id))
        else:
            cursor.execute("""
                UPDATE savings SET current_amount = current_amount - ? WHERE id = ?
            """, (amount, savings_id))

        self.conn.commit()
        return cursor.lastrowid

    def get_savings_transactions(self, savings_id: int) -> list:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM savings_transactions WHERE savings_id = ? ORDER BY date DESC
        """, (savings_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_total_savings(self) -> float:
        cursor = self.conn.cursor()
        cursor.execute("SELECT SUM(current_amount) FROM savings")
        result = cursor.fetchone()[0]
        return result if result else 0.0

    def delete_savings_account(self, savings_id: int):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM savings_transactions WHERE savings_id = ?", (savings_id,))
        cursor.execute("DELETE FROM savings WHERE id = ?", (savings_id,))
        self.conn.commit()

    # Monthly Page Methods
    def get_or_create_monthly_page(self, year: int, month: int) -> dict:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM monthly_pages WHERE year = ? AND month = ?
        """, (year, month))
        row = cursor.fetchone()
        if row:
            return dict(row)
        else:
            cursor.execute("""
                INSERT INTO monthly_pages (year, month) VALUES (?, ?)
            """, (year, month))
            self.conn.commit()
            return {"id": cursor.lastrowid, "year": year, "month": month, "notes": None}

    def get_monthly_summary(self, year: int, month: int) -> dict:
        """Get a summary for a specific month."""
        # Get paychecks for month
        paychecks = self.get_paychecks(year, month)
        total_income = sum(p["amount"] for p in paychecks)

        # Get purchases for month
        purchases = self.get_purchases(year, month)
        total_purchases = sum(p["amount"] for p in purchases)

        # Get monthly bills
        total_bills = self.get_total_monthly_bills()

        return {
            "total_income": total_income,
            "total_purchases": total_purchases,
            "total_bills": total_bills,
            "remaining": total_income - total_purchases - total_bills,
            "paycheck_count": len(paychecks),
            "purchase_count": len(purchases)
        }

    def close(self):
        self.conn.close()
