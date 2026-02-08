"""NekoBudget - A monthly budget tracking application."""

import sys
import os
import shutil
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QLineEdit, QDoubleSpinBox,
    QSpinBox, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QDateEdit, QTextEdit, QFileDialog, QMessageBox, QGroupBox,
    QFormLayout, QFrame, QScrollArea, QDialog, QDialogButtonBox,
    QProgressBar, QSplitter, QCheckBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPalette, QColor

from database import Database


# Cute color palette
COLORS = {
    "pink": "#FFB6C1",           # Light pink
    "pink_dark": "#FF69B4",      # Hot pink
    "lavender": "#E6E6FA",       # Lavender
    "mint": "#98FB98",           # Pale green/mint
    "peach": "#FFDAB9",          # Peach puff
    "cream": "#FFFAF0",          # Floral white/cream
    "coral": "#FF7F7F",          # Light coral for warnings
    "sky": "#87CEEB",            # Sky blue
    "lilac": "#DDA0DD",          # Plum/lilac
    "gold": "#FFD700",           # Gold for savings
    "text_dark": "#5D4E6D",      # Dark purple-gray for text
    "text_light": "#8B7B96",     # Lighter purple-gray
}

# Cute stylesheet for the entire app
CUTE_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #FFF5F8;
}

QGroupBox {
    background-color: #FFFFFF;
    border: 2px solid #FFB6C1;
    border-radius: 12px;
    margin-top: 12px;
    padding-top: 10px;
    font-weight: bold;
    color: #5D4E6D;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 8px;
    background-color: #FFFFFF;
    color: #FF69B4;
}

QPushButton {
    background-color: #FFB6C1;
    color: #5D4E6D;
    border: none;
    border-radius: 15px;
    padding: 8px 16px;
    font-weight: bold;
    min-height: 25px;
}

QPushButton:hover {
    background-color: #FF69B4;
    color: white;
}

QPushButton:pressed {
    background-color: #FF1493;
}

QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox, QDateEdit {
    background-color: #FFFFFF;
    border: 2px solid #E6E6FA;
    border-radius: 10px;
    padding: 6px 10px;
    color: #5D4E6D;
}

QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus, QComboBox:focus, QDateEdit:focus {
    border: 2px solid #FF69B4;
}

QTableWidget {
    background-color: #FFFFFF;
    border: 2px solid #E6E6FA;
    border-radius: 10px;
    gridline-color: #FFE4E9;
}

QTableWidget::item {
    padding: 5px;
    color: #5D4E6D;
}

QTableWidget::item:alternate {
    background-color: #FFF0F5;
}

QHeaderView::section {
    background-color: #FFB6C1;
    color: #5D4E6D;
    padding: 8px;
    border: none;
    font-weight: bold;
}

QTabWidget::pane {
    border: 2px solid #FFB6C1;
    border-radius: 10px;
    background-color: #FFFFFF;
}

QTabBar::tab {
    background-color: #E6E6FA;
    color: #5D4E6D;
    padding: 10px 15px;
    margin-right: 3px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    font-weight: bold;
}

QTabBar::tab:selected {
    background-color: #FF69B4;
    color: white;
}

QTabBar::tab:hover:!selected {
    background-color: #FFB6C1;
}

QProgressBar {
    border: 2px solid #E6E6FA;
    border-radius: 10px;
    background-color: #FFFFFF;
    text-align: center;
    color: #5D4E6D;
}

QProgressBar::chunk {
    background-color: qlineargradient(x1:0, y1:0.5, x2:1, y2:0.5, stop:0 #FFB6C1, stop:1 #FF69B4);
    border-radius: 8px;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QFrame {
    background-color: #FFFFFF;
    border-radius: 10px;
}

QLabel {
    color: #5D4E6D;
}

QCheckBox {
    color: #5D4E6D;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 2px solid #FFB6C1;
    background-color: #FFFFFF;
}

QCheckBox::indicator:checked {
    background-color: #FF69B4;
    border: 2px solid #FF69B4;
}

QMessageBox {
    background-color: #FFF5F8;
}

QMessageBox QLabel {
    color: #5D4E6D;
}

QMessageBox QPushButton {
    min-width: 80px;
}
"""

# Cute cat kaomoji and phrases
CAT_HAPPY = "(=^・ω・^=)"
CAT_LOVE = "(=^-ω-^=)"
CAT_EXCITED = "ヽ(=^・ω・^=)丿"
CAT_SAD = "(=;ω;=)"
CAT_SPARKLE = "✧(=^・ω・^=)✧"
PAW = "🐾"
SPARKLE = "✨"
HEART = "💕"
STAR = "⭐"
MONEY_CAT = "💰🐱"
PIGGY = "🐷"
COIN = "🪙"


class MonthlyBillsTab(QWidget):
    """Tab for managing monthly recurring bills."""

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.setup_ui()
        self.load_bills()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Add bill form
        form_group = QGroupBox(f"{PAW} Add New Monthly Bill {PAW}")
        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Rent, Electric, Insurance~")
        form_layout.addRow(f"{SPARKLE} Name:", self.name_input)

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 999999.99)
        self.amount_input.setPrefix("$")
        self.amount_input.setDecimals(2)
        form_layout.addRow(f"{COIN} Amount:", self.amount_input)

        self.due_day_input = QSpinBox()
        self.due_day_input.setRange(0, 31)
        self.due_day_input.setSpecialValueText("Not set~")
        self.due_day_input.setValue(0)  # Start with "Not set"
        form_layout.addRow("📅 Due Day:", self.due_day_input)

        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        self.category_input.addItems([
            "🏠 Housing", "💡 Utilities", "🛡️ Insurance", "🚗 Transportation",
            "📺 Subscriptions", "💳 Loans", "📦 Other"
        ])
        form_layout.addRow("📂 Category:", self.category_input)

        self.add_btn = QPushButton(f"Add Bill {CAT_HAPPY}")
        self.add_btn.clicked.connect(self.add_bill)
        form_layout.addRow(self.add_btn)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Bills table
        table_group = QGroupBox(f"{SPARKLE} Your Monthly Bills {SPARKLE}")
        table_layout = QVBoxLayout()

        self.bills_table = QTableWidget()
        self.bills_table.setColumnCount(5)
        self.bills_table.setHorizontalHeaderLabels([
            "Name", "Amount", "Due Day", "Category", "Actions"
        ])
        self.bills_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.bills_table.setAlternatingRowColors(True)
        table_layout.addWidget(self.bills_table)

        # Total
        self.total_label = QLabel(f"Total Monthly Bills: $0.00 {CAT_HAPPY}")
        self.total_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.total_label.setStyleSheet(f"color: {COLORS['pink_dark']};")
        table_layout.addWidget(self.total_label)

        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

    def add_bill(self):
        name = self.name_input.text().strip()
        amount = self.amount_input.value()
        due_day = self.due_day_input.value() if self.due_day_input.value() > 0 else None
        category = self.category_input.currentText()

        if not name:
            QMessageBox.warning(self, f"Oopsie! {CAT_SAD}", "Please enter a bill name, nya~")
            return

        if amount <= 0:
            QMessageBox.warning(self, f"Oopsie! {CAT_SAD}", "Please enter a valid amount, nya~")
            return

        self.db.add_monthly_bill(name, amount, due_day, category)
        self.load_bills()

        # Clear form
        self.name_input.clear()
        self.amount_input.setValue(0)
        self.due_day_input.setValue(0)  # Reset to "Not set"

    def load_bills(self):
        bills = self.db.get_monthly_bills()
        self.bills_table.setRowCount(len(bills))

        total = 0
        for row, bill in enumerate(bills):
            self.bills_table.setItem(row, 0, QTableWidgetItem(bill["name"]))
            self.bills_table.setItem(row, 1, QTableWidgetItem(f"${bill['amount']:.2f}"))
            self.bills_table.setItem(row, 2, QTableWidgetItem(
                str(bill["due_day"]) if bill["due_day"] else "~"
            ))
            self.bills_table.setItem(row, 3, QTableWidgetItem(bill["category"] or ""))

            # Delete button
            delete_btn = QPushButton("Remove 🗑️")
            delete_btn.setStyleSheet(f"background-color: {COLORS['coral']}; color: white;")
            delete_btn.clicked.connect(lambda checked, b=bill: self.delete_bill(b["id"]))
            self.bills_table.setCellWidget(row, 4, delete_btn)

            total += bill["amount"]

        self.total_label.setText(f"{SPARKLE} Total Monthly Bills: ${total:.2f} {CAT_HAPPY}")

    def delete_bill(self, bill_id):
        reply = QMessageBox.question(
            self, f"Wait! {CAT_SAD}",
            f"Are you sure you want to delete this bill?\n\n{CAT_LOVE} It's okay if you do~",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_monthly_bill(bill_id)
            self.load_bills()


class PaycheckTab(QWidget):
    """Tab for managing paychecks."""

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.setup_ui()
        self.load_paychecks()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Add paycheck form
        form_group = QGroupBox(f"{MONEY_CAT} Add Paycheck - Cha-ching! {MONEY_CAT}")
        form_layout = QFormLayout()

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 999999.99)
        self.amount_input.setPrefix("$")
        self.amount_input.setDecimals(2)
        form_layout.addRow(f"{COIN} Amount:", self.amount_input)

        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form_layout.addRow("📅 Date:", self.date_input)

        self.source_input = QLineEdit()
        self.source_input.setPlaceholderText("e.g., Main Job, Side Gig, Treats~")
        form_layout.addRow("💼 Source:", self.source_input)

        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("Any notes? (optional)")
        form_layout.addRow("📝 Notes:", self.notes_input)

        self.add_btn = QPushButton(f"Add Paycheck {CAT_EXCITED}")
        self.add_btn.setStyleSheet(f"background-color: {COLORS['mint']}; color: {COLORS['text_dark']};")
        self.add_btn.clicked.connect(self.add_paycheck)
        form_layout.addRow(self.add_btn)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Paychecks table
        table_group = QGroupBox(f"{SPARKLE} Your Hard-Earned Income {SPARKLE}")
        table_layout = QVBoxLayout()

        # Month filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("🔍 Filter by Month:"))

        self.month_filter = QComboBox()
        self.month_filter.addItem("✨ All", None)
        current_year = datetime.now().year
        for year in range(current_year, current_year - 3, -1):
            for month in range(12, 0, -1):
                month_name = datetime(year, month, 1).strftime("%B %Y")
                self.month_filter.addItem(month_name, (year, month))
        self.month_filter.currentIndexChanged.connect(self.load_paychecks)
        filter_layout.addWidget(self.month_filter)
        filter_layout.addStretch()
        table_layout.addLayout(filter_layout)

        self.paychecks_table = QTableWidget()
        self.paychecks_table.setColumnCount(5)
        self.paychecks_table.setHorizontalHeaderLabels([
            "📅 Date", "💰 Amount", "💼 Source", "📝 Notes", "Actions"
        ])
        self.paychecks_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.paychecks_table.setAlternatingRowColors(True)
        table_layout.addWidget(self.paychecks_table)

        self.total_label = QLabel(f"Total: $0.00 {CAT_HAPPY}")
        self.total_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.total_label.setStyleSheet(f"color: {COLORS['mint']};")
        table_layout.addWidget(self.total_label)

        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

    def add_paycheck(self):
        amount = self.amount_input.value()
        date = self.date_input.date().toString("yyyy-MM-dd")
        source = self.source_input.text().strip()
        notes = self.notes_input.text().strip()

        if amount <= 0:
            QMessageBox.warning(self, f"Oopsie! {CAT_SAD}", "Please enter a valid amount, nya~")
            return

        self.db.add_paycheck(amount, date, source or None, notes or None)
        self.load_paychecks()

        # Clear form
        self.amount_input.setValue(0)
        self.source_input.clear()
        self.notes_input.clear()

    def load_paychecks(self):
        filter_data = self.month_filter.currentData()
        if filter_data:
            year, month = filter_data
            paychecks = self.db.get_paychecks(year, month)
        else:
            paychecks = self.db.get_paychecks()

        self.paychecks_table.setRowCount(len(paychecks))

        total = 0
        for row, paycheck in enumerate(paychecks):
            self.paychecks_table.setItem(row, 0, QTableWidgetItem(paycheck["date"]))
            self.paychecks_table.setItem(row, 1, QTableWidgetItem(f"${paycheck['amount']:.2f}"))
            self.paychecks_table.setItem(row, 2, QTableWidgetItem(paycheck["source"] or ""))
            self.paychecks_table.setItem(row, 3, QTableWidgetItem(paycheck["notes"] or ""))

            delete_btn = QPushButton("Remove 🗑️")
            delete_btn.setStyleSheet(f"background-color: {COLORS['coral']}; color: white;")
            delete_btn.clicked.connect(lambda checked, p=paycheck: self.delete_paycheck(p["id"]))
            self.paychecks_table.setCellWidget(row, 4, delete_btn)

            total += paycheck["amount"]

        self.total_label.setText(f"{SPARKLE} Total Earned: ${total:.2f} {CAT_EXCITED}")

    def delete_paycheck(self, paycheck_id):
        reply = QMessageBox.question(
            self, f"Wait! {CAT_SAD}",
            f"Are you sure you want to delete this paycheck?\n\n{CAT_LOVE} Your money history is precious~",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_paycheck(paycheck_id)
            self.load_paychecks()


class PurchasesTab(QWidget):
    """Tab for tracking purchases with receipt upload."""

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.receipt_path = None
        self.receipts_dir = "receipts"
        os.makedirs(self.receipts_dir, exist_ok=True)
        self.setup_ui()
        self.load_purchases()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Add purchase form
        form_group = QGroupBox(f"🛍️ Add Purchase - Treat Yourself! 🛍️")
        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Groceries, Gas, Yummy Food~")
        form_layout.addRow(f"{SPARKLE} Name:", self.name_input)

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 999999.99)
        self.amount_input.setPrefix("$")
        self.amount_input.setDecimals(2)
        form_layout.addRow(f"{COIN} Amount:", self.amount_input)

        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form_layout.addRow("📅 Date:", self.date_input)

        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        self.category_input.addItems([
            "🛒 Groceries", "🍽️ Dining", "🚗 Transportation", "🎮 Entertainment",
            "🛍️ Shopping", "💊 Healthcare", "💅 Personal Care", "📦 Other"
        ])
        form_layout.addRow("📂 Category:", self.category_input)

        # Receipt upload
        receipt_layout = QHBoxLayout()
        self.receipt_label = QLabel("No receipt attached~")
        receipt_layout.addWidget(self.receipt_label)
        self.attach_btn = QPushButton("📎 Attach Receipt")
        self.attach_btn.setStyleSheet(f"background-color: {COLORS['lavender']};")
        self.attach_btn.clicked.connect(self.attach_receipt)
        receipt_layout.addWidget(self.attach_btn)
        self.clear_receipt_btn = QPushButton("Clear")
        self.clear_receipt_btn.clicked.connect(self.clear_receipt)
        receipt_layout.addWidget(self.clear_receipt_btn)
        form_layout.addRow("🧾 Receipt:", receipt_layout)

        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("Any notes? (optional)")
        form_layout.addRow("📝 Notes:", self.notes_input)

        self.add_btn = QPushButton(f"Add Purchase {CAT_HAPPY}")
        self.add_btn.setStyleSheet(f"background-color: {COLORS['lilac']}; color: white;")
        self.add_btn.clicked.connect(self.add_purchase)
        form_layout.addRow(self.add_btn)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Purchases table
        table_group = QGroupBox(f"{SPARKLE} Your Purchases {SPARKLE}")
        table_layout = QVBoxLayout()

        # Month filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("🔍 Filter by Month:"))

        self.month_filter = QComboBox()
        self.month_filter.addItem("✨ All", None)
        current_year = datetime.now().year
        for year in range(current_year, current_year - 3, -1):
            for month in range(12, 0, -1):
                month_name = datetime(year, month, 1).strftime("%B %Y")
                self.month_filter.addItem(month_name, (year, month))
        self.month_filter.currentIndexChanged.connect(self.load_purchases)
        filter_layout.addWidget(self.month_filter)
        filter_layout.addStretch()
        table_layout.addLayout(filter_layout)

        self.purchases_table = QTableWidget()
        self.purchases_table.setColumnCount(7)
        self.purchases_table.setHorizontalHeaderLabels([
            "📅 Date", "🏷️ Name", "💰 Amount", "📂 Category", "📝 Notes", "🧾 Receipt", "Actions"
        ])
        self.purchases_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.purchases_table.setAlternatingRowColors(True)
        table_layout.addWidget(self.purchases_table)

        self.total_label = QLabel(f"Total: $0.00 {CAT_HAPPY}")
        self.total_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.total_label.setStyleSheet(f"color: {COLORS['lilac']};")
        table_layout.addWidget(self.total_label)

        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

    def attach_receipt(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, f"Select Receipt {CAT_HAPPY}",
            "", "Images (*.png *.jpg *.jpeg *.bmp);;PDF (*.pdf);;All Files (*)"
        )
        if file_path:
            self.receipt_path = file_path
            self.receipt_label.setText(f"📎 {os.path.basename(file_path)}")

    def clear_receipt(self):
        self.receipt_path = None
        self.receipt_label.setText("No receipt attached~")

    def add_purchase(self):
        name = self.name_input.text().strip()
        amount = self.amount_input.value()
        date = self.date_input.date().toString("yyyy-MM-dd")
        category = self.category_input.currentText()
        notes = self.notes_input.text().strip()

        if not name:
            QMessageBox.warning(self, f"Oopsie! {CAT_SAD}", "Please enter a purchase name, nya~")
            return

        if amount <= 0:
            QMessageBox.warning(self, f"Oopsie! {CAT_SAD}", "Please enter a valid amount, nya~")
            return

        # Copy receipt to receipts directory
        saved_receipt_path = None
        if self.receipt_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ext = os.path.splitext(self.receipt_path)[1]
            new_filename = f"receipt_{timestamp}{ext}"
            saved_receipt_path = os.path.join(self.receipts_dir, new_filename)
            shutil.copy2(self.receipt_path, saved_receipt_path)

        self.db.add_purchase(name, amount, date, category, saved_receipt_path, notes or None)
        self.load_purchases()

        # Clear form
        self.name_input.clear()
        self.amount_input.setValue(0)
        self.notes_input.clear()
        self.clear_receipt()

    def load_purchases(self):
        filter_data = self.month_filter.currentData()
        if filter_data:
            year, month = filter_data
            purchases = self.db.get_purchases(year, month)
        else:
            purchases = self.db.get_purchases()

        self.purchases_table.setRowCount(len(purchases))

        total = 0
        for row, purchase in enumerate(purchases):
            self.purchases_table.setItem(row, 0, QTableWidgetItem(purchase["date"]))
            self.purchases_table.setItem(row, 1, QTableWidgetItem(purchase["name"]))
            self.purchases_table.setItem(row, 2, QTableWidgetItem(f"${purchase['amount']:.2f}"))
            self.purchases_table.setItem(row, 3, QTableWidgetItem(purchase["category"] or ""))
            self.purchases_table.setItem(row, 4, QTableWidgetItem(purchase["notes"] or ""))

            # Receipt view button
            if purchase["receipt_path"]:
                view_btn = QPushButton("👀 View")
                view_btn.setStyleSheet(f"background-color: {COLORS['sky']}; color: white;")
                view_btn.clicked.connect(lambda checked, p=purchase: self.view_receipt(p["receipt_path"]))
                self.purchases_table.setCellWidget(row, 5, view_btn)
            else:
                self.purchases_table.setItem(row, 5, QTableWidgetItem("~"))

            delete_btn = QPushButton("Remove 🗑️")
            delete_btn.setStyleSheet(f"background-color: {COLORS['coral']}; color: white;")
            delete_btn.clicked.connect(lambda checked, p=purchase: self.delete_purchase(p["id"]))
            self.purchases_table.setCellWidget(row, 6, delete_btn)

            total += purchase["amount"]

        self.total_label.setText(f"{SPARKLE} Total Spent: ${total:.2f} {CAT_LOVE}")

    def view_receipt(self, receipt_path):
        if os.path.exists(receipt_path):
            os.startfile(receipt_path)
        else:
            QMessageBox.warning(self, f"Oopsie! {CAT_SAD}", "Receipt file not found, nya~")

    def delete_purchase(self, purchase_id):
        reply = QMessageBox.question(
            self, f"Wait! {CAT_SAD}",
            f"Are you sure you want to delete this purchase?\n\n{CAT_LOVE} It's okay if you do~",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_purchase(purchase_id)
            self.load_purchases()


class SavingsTab(QWidget):
    """Tab for managing savings accounts."""

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.setup_ui()
        self.load_savings()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Add savings account form
        form_group = QGroupBox(f"{PIGGY} Create Savings Goal - Dream Big! {PIGGY}")
        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Vacation, New Phone, Rainy Day Fund~")
        form_layout.addRow(f"{SPARKLE} Name:", self.name_input)

        self.initial_amount_input = QDoubleSpinBox()
        self.initial_amount_input.setRange(0, 999999.99)
        self.initial_amount_input.setPrefix("$")
        self.initial_amount_input.setDecimals(2)
        form_layout.addRow(f"{COIN} Starting Amount:", self.initial_amount_input)

        self.goal_input = QDoubleSpinBox()
        self.goal_input.setRange(0, 999999.99)
        self.goal_input.setPrefix("$")
        self.goal_input.setDecimals(2)
        self.goal_input.setSpecialValueText("No goal~")
        form_layout.addRow(f"{STAR} Goal (optional):", self.goal_input)

        self.add_btn = QPushButton(f"Create Savings Goal {CAT_SPARKLE}")
        self.add_btn.setStyleSheet(f"background-color: {COLORS['gold']}; color: {COLORS['text_dark']};")
        self.add_btn.clicked.connect(self.add_savings_account)
        form_layout.addRow(self.add_btn)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Savings accounts display
        self.accounts_group = QGroupBox(f"{SPARKLE} Your Savings Goals {SPARKLE}")
        self.accounts_layout = QVBoxLayout()
        self.accounts_group.setLayout(self.accounts_layout)

        scroll = QScrollArea()
        scroll.setWidget(self.accounts_group)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        # Total savings
        self.total_label = QLabel(f"Total Savings: $0.00 {CAT_HAPPY}")
        self.total_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.total_label.setStyleSheet(f"color: {COLORS['gold']};")
        layout.addWidget(self.total_label)

    def add_savings_account(self):
        name = self.name_input.text().strip()
        initial_amount = self.initial_amount_input.value()
        goal = self.goal_input.value() if self.goal_input.value() > 0 else None

        if not name:
            QMessageBox.warning(self, f"Oopsie! {CAT_SAD}", "Please enter an account name, nya~")
            return

        self.db.add_savings_account(name, initial_amount, goal)
        self.load_savings()

        # Clear form
        self.name_input.clear()
        self.initial_amount_input.setValue(0)
        self.goal_input.setValue(0)

    def load_savings(self):
        # Clear existing widgets
        while self.accounts_layout.count():
            child = self.accounts_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        accounts = self.db.get_savings_accounts()

        for account in accounts:
            account_widget = self.create_account_widget(account)
            self.accounts_layout.addWidget(account_widget)

        self.accounts_layout.addStretch()

        total = self.db.get_total_savings()
        self.total_label.setText(f"{SPARKLE} Total Savings: ${total:.2f} {CAT_SPARKLE}")

    def create_account_widget(self, account):
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        frame.setStyleSheet(f"QFrame {{ background-color: white; border: 2px solid {COLORS['gold']}; border-radius: 12px; padding: 8px; }}")
        layout = QVBoxLayout(frame)

        # Header
        header_layout = QHBoxLayout()
        name_label = QLabel(f"{STAR} {account['name']}")
        name_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        name_label.setStyleSheet(f"color: {COLORS['text_dark']};")
        header_layout.addWidget(name_label)

        amount_label = QLabel(f"${account['current_amount']:.2f}")
        amount_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        amount_label.setStyleSheet(f"color: {COLORS['gold']};")
        header_layout.addWidget(amount_label)

        delete_btn = QPushButton("Remove 🗑️")
        delete_btn.setStyleSheet(f"background-color: {COLORS['coral']}; color: white;")
        delete_btn.clicked.connect(lambda: self.delete_account(account["id"]))
        header_layout.addWidget(delete_btn)

        layout.addLayout(header_layout)

        # Progress bar if goal exists
        if account["goal_amount"]:
            progress = int((account["current_amount"] / account["goal_amount"]) * 100)
            progress = min(progress, 100)

            progress_layout = QHBoxLayout()
            progress_bar = QProgressBar()
            progress_bar.setValue(progress)
            progress_bar.setFormat(f"{progress}% {CAT_EXCITED}" if progress >= 100 else f"{progress}%")
            progress_layout.addWidget(progress_bar)

            goal_label = QLabel(f"🎯 Goal: ${account['goal_amount']:.2f}")
            goal_label.setStyleSheet(f"color: {COLORS['text_light']};")
            progress_layout.addWidget(goal_label)

            layout.addLayout(progress_layout)

        # Transaction buttons
        btn_layout = QHBoxLayout()

        deposit_btn = QPushButton(f"💰 Deposit")
        deposit_btn.setStyleSheet(f"background-color: {COLORS['mint']}; color: {COLORS['text_dark']};")
        deposit_btn.clicked.connect(lambda: self.add_transaction(account["id"], "deposit"))
        btn_layout.addWidget(deposit_btn)

        withdraw_btn = QPushButton(f"💸 Withdraw")
        withdraw_btn.setStyleSheet(f"background-color: {COLORS['peach']}; color: {COLORS['text_dark']};")
        withdraw_btn.clicked.connect(lambda: self.add_transaction(account["id"], "withdraw"))
        btn_layout.addWidget(withdraw_btn)

        history_btn = QPushButton(f"📜 History")
        history_btn.setStyleSheet(f"background-color: {COLORS['lavender']}; color: {COLORS['text_dark']};")
        history_btn.clicked.connect(lambda: self.show_history(account["id"], account["name"]))
        btn_layout.addWidget(history_btn)

        layout.addLayout(btn_layout)

        return frame

    def add_transaction(self, savings_id, transaction_type):
        dialog = TransactionDialog(transaction_type, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            amount = dialog.amount
            notes = dialog.notes
            date = dialog.date

            self.db.add_savings_transaction(savings_id, amount, transaction_type, date, notes)
            self.load_savings()

    def show_history(self, savings_id, name):
        transactions = self.db.get_savings_transactions(savings_id)

        dialog = QDialog(self)
        dialog.setWindowTitle(f"{SPARKLE} Transaction History - {name} {SPARKLE}")
        dialog.setMinimumSize(500, 400)
        dialog.setStyleSheet(CUTE_STYLESHEET)

        layout = QVBoxLayout(dialog)

        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["📅 Date", "📋 Type", "💰 Amount", "📝 Notes"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setRowCount(len(transactions))
        table.setAlternatingRowColors(True)

        for row, trans in enumerate(transactions):
            table.setItem(row, 0, QTableWidgetItem(trans["date"]))
            type_emoji = "💰" if trans["transaction_type"] == "deposit" else "💸"
            table.setItem(row, 1, QTableWidgetItem(f"{type_emoji} {trans['transaction_type'].title()}"))

            amount_str = f"${trans['amount']:.2f}"
            if trans["transaction_type"] == "deposit":
                amount_str = "+" + amount_str
            else:
                amount_str = "-" + amount_str
            table.setItem(row, 2, QTableWidgetItem(amount_str))
            table.setItem(row, 3, QTableWidgetItem(trans["notes"] or ""))

        layout.addWidget(table)

        close_btn = QPushButton(f"Close {CAT_HAPPY}")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec()

    def delete_account(self, savings_id):
        reply = QMessageBox.question(
            self, f"Wait! {CAT_SAD}",
            f"Are you sure you want to delete this savings goal?\n\nAll your progress will be lost... {CAT_SAD}\n\n{CAT_LOVE} But it's okay if you need to~",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_savings_account(savings_id)
            self.load_savings()


class TransactionDialog(QDialog):
    """Dialog for adding savings transactions."""

    def __init__(self, transaction_type, parent=None):
        super().__init__(parent)
        self.transaction_type = transaction_type
        emoji = "💰" if transaction_type == "deposit" else "💸"
        self.setWindowTitle(f"{emoji} Add {transaction_type.title()} {CAT_HAPPY}")
        self.setStyleSheet(CUTE_STYLESHEET)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.01, 999999.99)
        self.amount_input.setPrefix("$")
        self.amount_input.setDecimals(2)
        layout.addRow(f"{COIN} Amount:", self.amount_input)

        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        layout.addRow("📅 Date:", self.date_input)

        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("Any notes? (optional)")
        layout.addRow("📝 Notes:", self.notes_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def validate_and_accept(self):
        if self.amount_input.value() <= 0:
            QMessageBox.warning(self, f"Oopsie! {CAT_SAD}", "Please enter a valid amount, nya~")
            return

        self.amount = self.amount_input.value()
        self.date = self.date_input.date().toString("yyyy-MM-dd")
        self.notes = self.notes_input.text().strip() or None
        self.accept()


class BillAccountTab(QWidget):
    """Tab for managing the bill account - money set aside for bills."""

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Current balance display
        balance_group = QGroupBox(f"{SPARKLE} Bill Account Balance {SPARKLE}")
        balance_layout = QVBoxLayout()

        self.balance_label = QLabel("$0.00")
        self.balance_label.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        self.balance_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.balance_label.setStyleSheet(f"color: {COLORS['sky']};")
        balance_layout.addWidget(self.balance_label)

        # Comparison with bills owed
        self.comparison_label = QLabel()
        self.comparison_label.setFont(QFont("Segoe UI", 12))
        self.comparison_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        balance_layout.addWidget(self.comparison_label)

        balance_group.setLayout(balance_layout)
        layout.addWidget(balance_group)

        # Quick actions
        actions_group = QGroupBox(f"{PAW} Quick Actions {PAW}")
        actions_layout = QHBoxLayout()

        self.deposit_amount = QDoubleSpinBox()
        self.deposit_amount.setRange(0.01, 999999.99)
        self.deposit_amount.setPrefix("$")
        self.deposit_amount.setDecimals(2)
        self.deposit_amount.setValue(0)
        actions_layout.addWidget(QLabel(f"{COIN} Amount:"))
        actions_layout.addWidget(self.deposit_amount)

        deposit_btn = QPushButton(f"💰 Deposit")
        deposit_btn.clicked.connect(self.quick_deposit)
        deposit_btn.setStyleSheet(f"background-color: {COLORS['mint']}; color: {COLORS['text_dark']};")
        actions_layout.addWidget(deposit_btn)

        withdraw_btn = QPushButton(f"💸 Withdraw")
        withdraw_btn.clicked.connect(self.quick_withdraw)
        withdraw_btn.setStyleSheet(f"background-color: {COLORS['peach']}; color: {COLORS['text_dark']};")
        actions_layout.addWidget(withdraw_btn)

        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)

        # Detailed transaction form
        form_group = QGroupBox(f"📝 Add Transaction with Details")
        form_layout = QFormLayout()

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.01, 999999.99)
        self.amount_input.setPrefix("$")
        self.amount_input.setDecimals(2)
        form_layout.addRow(f"{COIN} Amount:", self.amount_input)

        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form_layout.addRow("📅 Date:", self.date_input)

        self.type_input = QComboBox()
        self.type_input.addItems(["💰 Deposit", "💸 Withdraw"])
        form_layout.addRow("📋 Type:", self.type_input)

        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("e.g., From paycheck, Paid electric bill~")
        form_layout.addRow("📝 Notes:", self.notes_input)

        add_btn = QPushButton(f"Add Transaction {CAT_HAPPY}")
        add_btn.clicked.connect(self.add_transaction)
        form_layout.addRow(add_btn)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Transaction history
        history_group = QGroupBox(f"📜 Transaction History")
        history_layout = QVBoxLayout()

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["📅 Date", "📋 Type", "💰 Amount", "📝 Notes"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.setAlternatingRowColors(True)
        history_layout.addWidget(self.history_table)

        history_group.setLayout(history_layout)
        layout.addWidget(history_group)

        # Set balance manually (for corrections)
        correction_layout = QHBoxLayout()
        correction_layout.addWidget(QLabel("🔧 Set Balance:"))
        self.set_balance_input = QDoubleSpinBox()
        self.set_balance_input.setRange(0, 999999.99)
        self.set_balance_input.setPrefix("$")
        self.set_balance_input.setDecimals(2)
        correction_layout.addWidget(self.set_balance_input)
        set_btn = QPushButton("Set")
        set_btn.clicked.connect(self.set_balance)
        correction_layout.addWidget(set_btn)
        correction_layout.addStretch()
        layout.addLayout(correction_layout)

    def refresh(self):
        balance = self.db.get_bill_account_balance()
        self.balance_label.setText(f"${balance:.2f}")

        # Get current month's unpaid bills
        year = datetime.now().year
        month = datetime.now().month
        unpaid = self.db.get_unpaid_bills_total(year, month)
        total_bills = self.db.get_total_monthly_bills()

        if unpaid > 0:
            difference = balance - unpaid
            if difference >= 0:
                self.comparison_label.setText(
                    f"Bills still owed: ${unpaid:.2f}\n"
                    f"{CAT_HAPPY} You have ${difference:.2f} extra after paying remaining bills!"
                )
                self.comparison_label.setStyleSheet(f"color: {COLORS['mint']};")
            else:
                self.comparison_label.setText(
                    f"Bills still owed: ${unpaid:.2f}\n"
                    f"{CAT_SAD} You need ${abs(difference):.2f} more to cover remaining bills"
                )
                self.comparison_label.setStyleSheet(f"color: {COLORS['coral']};")
        else:
            self.comparison_label.setText(
                f"{CAT_SPARKLE} All bills paid for this month! {CAT_SPARKLE}\n"
                f"Total monthly bills: ${total_bills:.2f}"
            )
            self.comparison_label.setStyleSheet(f"color: {COLORS['mint']};")

        # Load transaction history
        transactions = self.db.get_bill_account_transactions()
        self.history_table.setRowCount(len(transactions))

        for row, trans in enumerate(transactions):
            self.history_table.setItem(row, 0, QTableWidgetItem(trans["date"]))

            type_emoji = "💰" if trans["transaction_type"] == "deposit" else "💸"
            type_item = QTableWidgetItem(f"{type_emoji} {trans['transaction_type'].title()}")
            self.history_table.setItem(row, 1, type_item)

            amount_str = f"${trans['amount']:.2f}"
            if trans["transaction_type"] == "deposit":
                amount_str = "+" + amount_str
                color = Qt.GlobalColor.darkGreen
            else:
                amount_str = "-" + amount_str
                color = Qt.GlobalColor.red

            amount_item = QTableWidgetItem(amount_str)
            amount_item.setForeground(color)
            self.history_table.setItem(row, 2, amount_item)

            self.history_table.setItem(row, 3, QTableWidgetItem(trans["notes"] or ""))

    def quick_deposit(self):
        amount = self.deposit_amount.value()
        if amount <= 0:
            QMessageBox.warning(self, f"Oopsie! {CAT_SAD}", "Please enter an amount, nya~")
            return

        date = QDate.currentDate().toString("yyyy-MM-dd")
        self.db.add_bill_account_transaction(amount, "deposit", date, "Quick deposit~")
        self.deposit_amount.setValue(0)
        self.refresh()

    def quick_withdraw(self):
        amount = self.deposit_amount.value()
        if amount <= 0:
            QMessageBox.warning(self, f"Oopsie! {CAT_SAD}", "Please enter an amount, nya~")
            return

        balance = self.db.get_bill_account_balance()
        if amount > balance:
            QMessageBox.warning(self, f"Oopsie! {CAT_SAD}", "Not enough funds in your bill account, nya~")
            return

        date = QDate.currentDate().toString("yyyy-MM-dd")
        self.db.add_bill_account_transaction(amount, "withdraw", date, "Quick withdraw~")
        self.deposit_amount.setValue(0)
        self.refresh()

    def add_transaction(self):
        amount = self.amount_input.value()
        if amount <= 0:
            QMessageBox.warning(self, f"Oopsie! {CAT_SAD}", "Please enter an amount, nya~")
            return

        date = self.date_input.date().toString("yyyy-MM-dd")
        trans_type_text = self.type_input.currentText()
        trans_type = "deposit" if "Deposit" in trans_type_text else "withdraw"
        notes = self.notes_input.text().strip() or None

        if trans_type == "withdraw":
            balance = self.db.get_bill_account_balance()
            if amount > balance:
                QMessageBox.warning(self, f"Oopsie! {CAT_SAD}", "Not enough funds, nya~")
                return

        self.db.add_bill_account_transaction(amount, trans_type, date, notes)

        # Clear form
        self.amount_input.setValue(0)
        self.notes_input.clear()
        self.refresh()

    def set_balance(self):
        new_balance = self.set_balance_input.value()
        reply = QMessageBox.question(
            self, f"Confirm {CAT_LOVE}",
            f"Set bill account balance to ${new_balance:.2f}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.set_bill_account_balance(new_balance)
            self.set_balance_input.setValue(0)
            self.refresh()


class DashboardTab(QWidget):
    """Dashboard showing budget summary and paycheck breakdown."""

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.setup_ui()
        self.refresh()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Month selector
        month_layout = QHBoxLayout()
        month_layout.addWidget(QLabel("📅 View Month:"))

        self.month_selector = QComboBox()
        current_year = datetime.now().year
        current_month = datetime.now().month
        for year in range(current_year, current_year - 2, -1):
            for month in range(12, 0, -1):
                month_name = datetime(year, month, 1).strftime("%B %Y")
                self.month_selector.addItem(month_name, (year, month))
                if year == current_year and month == current_month:
                    self.month_selector.setCurrentIndex(self.month_selector.count() - 1)
        self.month_selector.currentIndexChanged.connect(self.refresh)
        month_layout.addWidget(self.month_selector)

        refresh_btn = QPushButton(f"🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh)
        month_layout.addWidget(refresh_btn)

        month_layout.addStretch()
        layout.addLayout(month_layout)

        # Main content area
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side - Summary
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Monthly Bills Summary with Pay Bill checkboxes
        bills_group = QGroupBox(f"{PAW} Monthly Bills (Recurring) {PAW}")
        bills_layout = QVBoxLayout()

        self.bills_table = QTableWidget()
        self.bills_table.setColumnCount(4)
        self.bills_table.setHorizontalHeaderLabels(["✓", "Name", "Amount", "Due"])
        self.bills_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.bills_table.setColumnWidth(0, 50)
        self.bills_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.bills_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.bills_table.setColumnWidth(2, 100)
        self.bills_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.bills_table.setColumnWidth(3, 60)
        self.bills_table.setAlternatingRowColors(True)
        self.bills_table.setMaximumHeight(200)
        bills_layout.addWidget(self.bills_table)

        self.bills_total_label = QLabel()
        self.bills_total_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        bills_layout.addWidget(self.bills_total_label)

        self.bills_unpaid_label = QLabel()
        self.bills_unpaid_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.bills_unpaid_label.setStyleSheet(f"color: {COLORS['coral']};")
        bills_layout.addWidget(self.bills_unpaid_label)

        bills_group.setLayout(bills_layout)
        left_layout.addWidget(bills_group)

        # Income Summary
        income_group = QGroupBox(f"{MONEY_CAT} Income This Month")
        income_layout = QVBoxLayout()
        self.income_label = QLabel()
        income_layout.addWidget(self.income_label)
        income_group.setLayout(income_layout)
        left_layout.addWidget(income_group)

        # Spending Summary
        spending_group = QGroupBox(f"🛍️ Spending This Month")
        spending_layout = QVBoxLayout()
        self.spending_label = QLabel()
        spending_layout.addWidget(self.spending_label)
        spending_group.setLayout(spending_layout)
        left_layout.addWidget(spending_group)

        left_layout.addStretch()
        splitter.addWidget(left_widget)

        # Right side - Budget Analysis
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Budget Overview
        overview_group = QGroupBox(f"{SPARKLE} Budget Overview {SPARKLE}")
        overview_layout = QVBoxLayout()
        self.overview_label = QLabel()
        self.overview_label.setFont(QFont("Segoe UI", 11))
        overview_layout.addWidget(self.overview_label)
        overview_group.setLayout(overview_layout)
        right_layout.addWidget(overview_group)

        # Paycheck Breakdown
        paycheck_group = QGroupBox(f"💰 Paycheck Breakdown (2 Paychecks/Month)")
        paycheck_layout = QVBoxLayout()
        self.paycheck_breakdown_label = QLabel()
        self.paycheck_breakdown_label.setFont(QFont("Segoe UI", 11))
        paycheck_layout.addWidget(self.paycheck_breakdown_label)
        paycheck_group.setLayout(paycheck_layout)
        right_layout.addWidget(paycheck_group)

        # Bill Account Summary
        bill_account_group = QGroupBox(f"🏦 Bill Account")
        bill_account_layout = QVBoxLayout()
        self.bill_account_label = QLabel()
        self.bill_account_label.setFont(QFont("Segoe UI", 11))
        bill_account_layout.addWidget(self.bill_account_label)
        bill_account_group.setLayout(bill_account_layout)
        right_layout.addWidget(bill_account_group)

        # Savings Summary
        savings_group = QGroupBox(f"{PIGGY} Savings Overview")
        savings_layout = QVBoxLayout()
        self.savings_label = QLabel()
        self.savings_label.setFont(QFont("Segoe UI", 11))
        savings_layout.addWidget(self.savings_label)
        savings_group.setLayout(savings_layout)
        right_layout.addWidget(savings_group)

        right_layout.addStretch()
        splitter.addWidget(right_widget)

        layout.addWidget(splitter)

    def refresh(self):
        year, month = self.month_selector.currentData() or (datetime.now().year, datetime.now().month)
        self.current_year = year
        self.current_month = month

        # Get data
        bills = self.db.get_monthly_bills()
        total_bills = sum(b["amount"] for b in bills)
        paid_bill_ids = self.db.get_paid_bill_ids(year, month)
        unpaid_total = self.db.get_unpaid_bills_total(year, month)

        paychecks = self.db.get_paychecks(year, month)
        total_income = sum(p["amount"] for p in paychecks)
        purchases = self.db.get_purchases(year, month)
        total_spending = sum(p["amount"] for p in purchases)
        savings_accounts = self.db.get_savings_accounts()
        total_savings = sum(s["current_amount"] for s in savings_accounts)

        # Update Bills Table with checkboxes
        self.bills_table.setRowCount(len(bills))
        for row, bill in enumerate(bills):
            # Checkbox for paid status
            checkbox = QCheckBox()
            checkbox.setChecked(bill["id"] in paid_bill_ids)
            checkbox.stateChanged.connect(
                lambda state, b=bill: self.on_bill_paid_changed(b["id"], state)
            )
            # Center the checkbox in the cell
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            self.bills_table.setCellWidget(row, 0, checkbox_widget)

            # Bill name
            name_item = QTableWidgetItem(bill["name"])
            if bill["id"] in paid_bill_ids:
                name_item.setForeground(Qt.GlobalColor.gray)
            self.bills_table.setItem(row, 1, name_item)

            # Amount
            amount_item = QTableWidgetItem(f"${bill['amount']:.2f}")
            if bill["id"] in paid_bill_ids:
                amount_item.setForeground(Qt.GlobalColor.gray)
            self.bills_table.setItem(row, 2, amount_item)

            # Due day
            due_text = str(bill["due_day"]) if bill["due_day"] else "~"
            due_item = QTableWidgetItem(due_text)
            if bill["id"] in paid_bill_ids:
                due_item.setForeground(Qt.GlobalColor.gray)
            self.bills_table.setItem(row, 3, due_item)

        self.bills_total_label.setText(f"{PAW} Total Monthly Bills: ${total_bills:.2f}")
        if unpaid_total > 0:
            self.bills_unpaid_label.setText(f"{CAT_SAD} Still Owed: ${unpaid_total:.2f}")
        else:
            self.bills_unpaid_label.setText(f"{CAT_SPARKLE} All paid!")
            self.bills_unpaid_label.setStyleSheet(f"color: {COLORS['mint']};")

        # Update Income
        income_text = f"{SPARKLE} Total Income: ${total_income:.2f}\n"
        income_text += f"💵 Paychecks Received: {len(paychecks)}\n"
        if paychecks:
            income_text += "\n📋 Paychecks:\n"
            for p in paychecks:
                income_text += f"  {p['date']}: ${p['amount']:.2f}"
                if p['source']:
                    income_text += f" ({p['source']})"
                income_text += "\n"
        self.income_label.setText(income_text)

        # Update Spending
        spending_text = f"{SPARKLE} Total Purchases: ${total_spending:.2f}\n"
        spending_text += f"🛒 Number of Purchases: {len(purchases)}\n"

        # Category breakdown
        categories = {}
        for p in purchases:
            cat = p["category"] or "📦 Other"
            categories[cat] = categories.get(cat, 0) + p["amount"]

        if categories:
            spending_text += "\n📊 By Category:\n"
            for cat, amount in sorted(categories.items(), key=lambda x: -x[1]):
                spending_text += f"  {cat}: ${amount:.2f}\n"

        self.spending_label.setText(spending_text)

        # Budget Overview
        total_expenses = total_bills + total_spending
        remaining = total_income - total_expenses

        overview_text = f"💰 Income: ${total_income:.2f}\n"
        overview_text += f"📄 Bills: -${total_bills:.2f}\n"
        overview_text += f"🛍️ Purchases: -${total_spending:.2f}\n"
        overview_text += f"{'─'*30}\n"

        if remaining >= 0:
            overview_text += f"{CAT_SPARKLE} Remaining: ${remaining:.2f}"
            self.overview_label.setStyleSheet(f"color: {COLORS['mint']};")
        else:
            overview_text += f"{CAT_SAD} Over Budget: -${abs(remaining):.2f}"
            self.overview_label.setStyleSheet(f"color: {COLORS['coral']};")

        self.overview_label.setText(overview_text)

        # Paycheck Breakdown
        amount_per_paycheck = total_bills / 2
        unpaid_per_paycheck = unpaid_total / 2

        paycheck_text = f"📄 Monthly Bills Total: ${total_bills:.2f}\n"
        paycheck_text += f"⏳ Still Owed This Month: ${unpaid_total:.2f}\n\n"

        paycheck_text += f"💡 To cover ALL bills monthly:\n"
        paycheck_text += f"  ${amount_per_paycheck:.2f} per paycheck\n\n"

        if unpaid_total > 0:
            paycheck_text += f"💡 To cover REMAINING unpaid bills:\n"
            paycheck_text += f"  ${unpaid_per_paycheck:.2f} per paycheck\n\n"

        if total_income > 0:
            avg_paycheck = total_income / max(len(paychecks), 1)
            after_bills = avg_paycheck - amount_per_paycheck
            paycheck_text += f"📊 Average Paycheck: ${avg_paycheck:.2f}\n"
            paycheck_text += f"{CAT_HAPPY} After Bills Allocation: ${after_bills:.2f}\n"
        else:
            paycheck_text += f"{CAT_LOVE} Enter paychecks to see breakdown~"

        self.paycheck_breakdown_label.setText(paycheck_text)

        # Bill Account Overview
        bill_account_balance = self.db.get_bill_account_balance()
        bill_account_text = f"💰 Balance: ${bill_account_balance:.2f}\n"

        if unpaid_total > 0:
            difference = bill_account_balance - unpaid_total
            if difference >= 0:
                bill_account_text += f"📄 Bills Owed: ${unpaid_total:.2f}\n"
                bill_account_text += f"{CAT_SPARKLE} Surplus: ${difference:.2f}"
                self.bill_account_label.setStyleSheet(f"color: {COLORS['mint']};")
            else:
                bill_account_text += f"📄 Bills Owed: ${unpaid_total:.2f}\n"
                bill_account_text += f"{CAT_SAD} Short: ${abs(difference):.2f}"
                self.bill_account_label.setStyleSheet(f"color: {COLORS['coral']};")
        else:
            bill_account_text += f"{CAT_SPARKLE} All bills paid!"
            self.bill_account_label.setStyleSheet(f"color: {COLORS['mint']};")

        self.bill_account_label.setText(bill_account_text)

        # Savings Overview
        savings_text = f"{SPARKLE} Total in Savings: ${total_savings:.2f}\n\n"
        if savings_accounts:
            savings_text += f"{STAR} Accounts:\n"
            for acc in savings_accounts:
                savings_text += f"  {acc['name']}: ${acc['current_amount']:.2f}"
                if acc['goal_amount']:
                    progress = (acc['current_amount'] / acc['goal_amount']) * 100
                    savings_text += f" ({progress:.1f}% of ${acc['goal_amount']:.2f})"
                savings_text += "\n"
        else:
            savings_text += f"{CAT_LOVE} No savings accounts set up yet~"

        self.savings_label.setText(savings_text)

    def on_bill_paid_changed(self, bill_id: int, state: int):
        """Handle when a bill's paid checkbox is toggled."""
        today = QDate.currentDate().toString("yyyy-MM-dd")

        if state == 2:  # Checked (Qt.CheckState.Checked = 2)
            self.db.mark_bill_paid(bill_id, self.current_year, self.current_month, today)
        else:  # Unchecked
            self.db.mark_bill_unpaid(bill_id, self.current_year, self.current_month)

        # Refresh to update totals
        self.refresh()


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.db = Database()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle(f"NekoBudget {CAT_HAPPY} - Monthly Budget Tracker")
        self.setMinimumSize(900, 700)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Header with cute cat face
        header = QLabel(f"🐱 NekoBudget {CAT_SPARKLE}")
        header.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet(f"""
            color: {COLORS['pink_dark']};
            padding: 10px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {COLORS['cream']}, stop:0.5 {COLORS['pink']}, stop:1 {COLORS['cream']});
            border-radius: 15px;
            margin: 5px;
        """)
        layout.addWidget(header)

        # Cute subtitle
        subtitle = QLabel(f"{HEART} Your purrfect budget companion! {HEART}")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"color: {COLORS['text_light']}; margin-bottom: 10px;")
        layout.addWidget(subtitle)

        # Tab widget
        self.tabs = QTabWidget()

        # Create tabs
        self.dashboard_tab = DashboardTab(self.db)
        self.bills_tab = MonthlyBillsTab(self.db)
        self.bill_account_tab = BillAccountTab(self.db)
        self.paycheck_tab = PaycheckTab(self.db)
        self.purchases_tab = PurchasesTab(self.db)
        self.savings_tab = SavingsTab(self.db)

        self.tabs.addTab(self.dashboard_tab, f"🏠 Dashboard")
        self.tabs.addTab(self.bills_tab, f"📄 Monthly Bills")
        self.tabs.addTab(self.bill_account_tab, f"🏦 Bill Account")
        self.tabs.addTab(self.paycheck_tab, f"💰 Paychecks")
        self.tabs.addTab(self.purchases_tab, f"🛍️ Purchases")
        self.tabs.addTab(self.savings_tab, f"{PIGGY} Savings")

        # Refresh tabs when switching
        self.tabs.currentChanged.connect(self.on_tab_changed)

        layout.addWidget(self.tabs)

    def on_tab_changed(self, index):
        if index == 0:  # Dashboard tab
            self.dashboard_tab.refresh()
        elif index == 2:  # Bill Account tab
            self.bill_account_tab.refresh()

    def closeEvent(self, event):
        self.db.close()
        event.accept()


def main():
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle("Fusion")

    # Apply cute stylesheet
    app.setStyleSheet(CUTE_STYLESHEET)

    # Set cute palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(COLORS['cream']))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(COLORS['text_dark']))
    palette.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(COLORS['lavender']))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(COLORS['pink']))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(COLORS['text_dark']))
    palette.setColor(QPalette.ColorRole.Text, QColor(COLORS['text_dark']))
    palette.setColor(QPalette.ColorRole.Button, QColor(COLORS['pink']))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(COLORS['text_dark']))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(COLORS['pink_dark']))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
    app.setPalette(palette)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
