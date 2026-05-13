from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class NumericItem(QTableWidgetItem):
    """Sayısal değerleri doğru sıralayan tablo hücresi."""
    def __init__(self, value, display_text=None, color=None, bg_color=None):
        text = display_text if display_text is not None else str(value)
        super().__init__(text)
        try:
            self._value = float(value)
        except (ValueError, TypeError):
            self._value = 0.0
        self.setForeground(QColor(color) if color else QColor("#111111"))
        if bg_color:
            self.setBackground(QColor(bg_color))

    def __lt__(self, other):
        if isinstance(other, NumericItem):
            return self._value < other._value
        return super().__lt__(other)


def setup_table(table):
    from PySide6.QtWidgets import QAbstractItemView
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    table.setAlternatingRowColors(False)
    table.verticalHeader().setVisible(False)
    table.setSelectionBehavior(QAbstractItemView.SelectRows)
    table.setSelectionMode(QAbstractItemView.SingleSelection)
    table.setSortingEnabled(True)
    table.horizontalHeader().setSectionsClickable(True)
    table.setStyleSheet("""
        QTableWidget {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            gridline-color: #f3f4f6;
            outline: none;
        }
        QHeaderView::section {
            background-color: #1B3A6B;
            color: white;
            padding: 8px;
            font-weight: bold;
            border: none;
        }
        QHeaderView::section:hover {
            background-color: #2563EB;
        }
        QTableWidget::item {
            color: #111111;
            padding: 4px 8px;
            border: none;
            outline: none;
        }
        QTableWidget::item:selected {
            background-color: #2563EB;
            color: white;
        }
        QTableWidget::item:focus {
            background-color: #2563EB;
            color: white;
            border: none;
            outline: none;
        }
    """)


def make_item(text, color=None, bg_color=None):
    """Metin tablo hücresi."""
    item = QTableWidgetItem(str(text))
    item.setForeground(QColor(color) if color else QColor("#111111"))
    if bg_color:
        item.setBackground(QColor(bg_color))
    return item


def make_numeric_item(value, display_text=None, color=None, bg_color=None):
    """Sayısal sıralama destekli tablo hücresi."""
    return NumericItem(value, display_text, color, bg_color)


def format_qty(value):
    """Miktarı tam sayı veya ondalık olarak formatlar."""
    try:
        f = float(value)
        if f == int(f):
            return str(int(f))
        return f"{f:,.3f}".rstrip("0").rstrip(".")
    except (ValueError, TypeError):
        return str(value)