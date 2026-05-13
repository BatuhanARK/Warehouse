from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QComboBox, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from services.stock_service import StockService
from services.customer_service import CustomerService
from services.product_service import ProductService
from services.location_service import LocationService
from utils.table_helper import setup_table, make_item, format_qty, make_numeric_item


class StockViewWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.stock_service    = StockService()
        self.customer_service = CustomerService()
        self.product_service  = ProductService()
        self.location_service = LocationService()
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Başlık
        top = QHBoxLayout()
        title = QLabel("📦 Stok Durumu")
        title.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #1B3A6B;"
        )
        refresh_btn = QPushButton("🔄 Yenile")
        refresh_btn.setStyleSheet(
            "background:#2563EB; color:white; padding:8px 16px;"
            "border-radius:4px; font-size:13px;"
        )
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.clicked.connect(self.load_data)
        top.addWidget(title)
        top.addStretch()
        top.addWidget(refresh_btn)
        layout.addLayout(top)

        # Özet kartları
        self.summary_layout = QHBoxLayout()
        self.summary_layout.setSpacing(10)
        layout.addLayout(self.summary_layout)

        # Filtreler
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)

        # Müşteri filtresi
        self.filter_customer = QComboBox()
        self.filter_customer.addItem("Tüm Müşteriler", None)
        for c in self.customer_service.get_all_customers():
            self.filter_customer.addItem(c.name, c.id)
        self.filter_customer.setStyleSheet(
            "padding:7px; border:1px solid #d1d5db; border-radius:4px;"
        )
        self.filter_customer.currentIndexChanged.connect(self._apply_filters)

        # Lokasyon filtresi
        self.filter_location = QComboBox()
        self.filter_location.addItem("Tüm Lokasyonlar", None)
        for loc in self.location_service.get_all_locations():
            self.filter_location.addItem(loc.code, loc.id)
        self.filter_location.setStyleSheet(
            "padding:7px; border:1px solid #d1d5db; border-radius:4px;"
        )
        self.filter_location.currentIndexChanged.connect(self._apply_filters)

        # Düşük stok filtresi
        self.filter_low = QComboBox()
        self.filter_low.addItems(["Tüm Stok", "Düşük Stok (≤10)"])
        self.filter_low.setStyleSheet(
            "padding:7px; border:1px solid #d1d5db; border-radius:4px;"
        )
        self.filter_low.currentIndexChanged.connect(self._apply_filters)

        # Arama
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Ürün veya SKU ara...")
        self.search_input.setStyleSheet(
            "padding:8px; border:1px solid #d1d5db;"
            "border-radius:4px; font-size:13px;"
        )
        self.search_input.textChanged.connect(self._apply_filters)

        filter_layout.addWidget(self._lbl("Müşteri:"))
        filter_layout.addWidget(self.filter_customer)
        filter_layout.addWidget(self._lbl("Lokasyon:"))
        filter_layout.addWidget(self.filter_location)
        filter_layout.addWidget(self.filter_low)
        filter_layout.addWidget(self.search_input, 1)
        layout.addLayout(filter_layout)

        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Müşteri", "SKU", "Ürün Adı",
            "Lokasyon", "Miktar", "Birim", "Durum"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 50)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.table.setColumnWidth(5, 100)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.setColumnWidth(6, 80)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Fixed)
        self.table.setColumnWidth(7, 120)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        setup_table(self.table)
        layout.addWidget(self.table)

        # Alt bilgi satırı
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("color: #6b7280; font-size: 12px;")
        layout.addWidget(self.info_label)

    def load_data(self):
        self.all_stock = self.stock_service.get_all_stock()
        self._refresh_summary()
        self._apply_filters()

    def _refresh_summary(self):
        # Kartları temizle
        while self.summary_layout.count():
            item = self.summary_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        total_items  = len(self.all_stock)
        total_qty    = sum(float(s.quantity) for s in self.all_stock)
        low_stock    = len(self.stock_service.get_low_stock())
        empty_slots  = len([s for s in self.all_stock if float(s.quantity) == 0])

        cards = [
            ("Toplam Kalem",    str(total_items),        "#2563EB"),
            ("Toplam Miktar",   f"{total_qty:,.0f}",     "#16a34a"),
            ("Düşük Stok",      str(low_stock),          "#d97706"),
            ("Sıfır Stok",      str(empty_slots),        "#dc2626"),
        ]
        for title, value, color in cards:
            card = self._make_card(title, value, color)
            self.summary_layout.addWidget(card)

    def _make_card(self, title, value, color):
        card = QFrame()
        card.setFixedHeight(100)
        card.setObjectName("kpiCard")
        card.setStyleSheet("""
            QFrame#kpiCard {
                background: white;
                border-radius: 8px;
                border: 1px solid #e5e7eb;
            }
        """)
        layout = QVBoxLayout(card)
        val_lbl = QLabel(value)
        val_lbl.setAlignment(Qt.AlignCenter)
        val_lbl.setStyleSheet(
            f"font-size: 28px; font-weight: bold; color: {color};"
        )
        title_lbl = QLabel(title)
        title_lbl.setAlignment(Qt.AlignCenter)
        title_lbl.setStyleSheet("font-size: 12px; color: #6b7280;")
        layout.addWidget(val_lbl)
        layout.addWidget(title_lbl)
        return card

    def _apply_filters(self):
        customer_id = self.filter_customer.currentData()
        location_id = self.filter_location.currentData()
        low_only    = self.filter_low.currentIndex() == 1
        search_text = self.search_input.text().lower()

        filtered = self.all_stock

        if customer_id:
            filtered = [s for s in filtered if s.customer_id == customer_id]
        if location_id:
            filtered = [s for s in filtered if s.location_id == location_id]
        if low_only:
            filtered = [s for s in filtered if float(s.quantity) <= 10]
        if search_text:
            filtered = [
                s for s in filtered
                if search_text in s.product.name.lower()
                or search_text in s.product.sku.lower()
            ]

        self._populate_table(filtered)
        self.info_label.setText(
            f"Toplam {len(filtered)} kayıt gösteriliyor."
        )
    
    def _lbl(self, text):
        l = QLabel(text)
        l.setStyleSheet("color: #111111; font-size: 13px;")
        return l

    def _populate_table(self, stock_list):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(stock_list))
        for row, s in enumerate(stock_list):
            qty = float(s.quantity)

            if qty == 0:
                durum, durum_color, durum_bg = "Stok Yok",   "#dc2626", "#fee2e2"
            elif qty <= 10:
                durum, durum_color, durum_bg = "Düşük Stok", "#d97706", "#fef3c7"
            else:
                durum, durum_color, durum_bg = "Normal",     "#16a34a", "#dcfce7"

            qty_color = "#dc2626" if qty == 0 else "#d97706" if qty <= 10 else "#111111"

            values = [
                (str(s.id),                             "text",    None,       None),
                (s.customer.name if s.customer else "", "text",    None,       None),
                (s.product.sku   if s.product  else "", "text",    None,       None),
                (s.product.name  if s.product  else "", "text",    None,       None),
                (s.location.code if s.location else "", "text",    None,       None),
                (qty,                                   "numeric", qty_color,  None),
                (s.product.unit  if s.product  else "", "text",    None,       None),
                (durum,                                 "text",    durum_color, durum_bg),
            ]
            for col, (val, kind, color, bg) in enumerate(values):
                if kind == "numeric":
                    self.table.setItem(row, col,
                        make_numeric_item(val, format_qty(val), color, bg))
                else:
                    self.table.setItem(row, col, make_item(str(val), color, bg))
        self.table.setSortingEnabled(True)