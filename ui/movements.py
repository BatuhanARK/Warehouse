from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialog, QFormLayout, QLineEdit,
    QMessageBox, QComboBox, QDoubleSpinBox,
    QDateEdit, QTextEdit, QFrame
)
from PySide6.QtCore import Qt, QDate, Signal
from services.movement_service import MovementService, InsufficientStockError
from services.customer_service import CustomerService
from services.product_service import ProductService
from services.location_service import LocationService
from utils.table_helper import setup_table, make_item, make_numeric_item, format_qty
from utils.base_dialog import BaseDialog

class MovementDialog(BaseDialog):
    def __init__(self, parent=None, customers=None, products=None, locations=None):
        super().__init__(parent)
        self.setWindowTitle("Yeni Hareket Ekle")
        self.setMinimumWidth(480)
        self.customers = customers or []
        self.products  = products  or []
        self.locations = locations or []
        self._build_ui()

    def _build_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(12)

        self.movement_type = QComboBox()
        self.movement_type.addItems(["IN", "OUT", "TRANSFER"])
        self.movement_type.currentTextChanged.connect(self._on_type_changed)
        layout.addRow("Hareket Tipi *", self.movement_type)

        self.customer_combo = QComboBox()
        for c in self.customers:
            self.customer_combo.addItem(f"{c.code} - {c.name}", c.id)
        layout.addRow("Müşteri *", self.customer_combo)

        self.product_combo = QComboBox()
        for p in self.products:
            self.product_combo.addItem(f"{p.sku} - {p.name}", p.id)
        layout.addRow("Ürün *", self.product_combo)

        self.from_label = QLabel("Çıkış Lokasyonu *")
        self.from_label.setStyleSheet("color: #111111; font-size: 13px;")
        self.from_combo = QComboBox()
        for loc in self.locations:
            self.from_combo.addItem(loc.code, loc.id)
        layout.addRow(self.from_label, self.from_combo)

        self.to_label = QLabel("Giriş Lokasyonu *")
        self.to_label.setStyleSheet("color: #111111; font-size: 13px;")
        self.to_combo = QComboBox()
        for loc in self.locations:
            self.to_combo.addItem(loc.code, loc.id)
        layout.addRow(self.to_label, self.to_combo)

        self.quantity = QDoubleSpinBox()
        self.quantity.setMinimum(1)
        self.quantity.setMaximum(999999)
        self.quantity.setDecimals(0)
        self.quantity.setValue(1)
        self.quantity.setSingleStep(1)
        layout.addRow("Miktar *", self.quantity)

        self.movement_date = QDateEdit()
        self.movement_date.setDate(QDate.currentDate())
        self.movement_date.setCalendarPopup(True)
        layout.addRow("Tarih *", self.movement_date)

        self.reference = QLineEdit()
        self.reference.setPlaceholderText("örn: PO-2026-001")
        layout.addRow("Referans No", self.reference)

        self.notes = QTextEdit()
        self.notes.setMaximumHeight(70)
        self.notes.setPlaceholderText("İsteğe bağlı notlar...")
        layout.addRow("Notlar", self.notes)

        btn_layout = QHBoxLayout()
        save_btn   = QPushButton("Kaydet")
        cancel_btn = QPushButton("İptal")
        save_btn.setStyleSheet(
            "background:#2563EB; color:white; padding:8px 20px; border-radius:4px;"
        )
        cancel_btn.setStyleSheet(
            "background:#6b7280; color:white; padding:8px 20px; border-radius:4px;"
        )
        save_btn.clicked.connect(self._save)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addRow(btn_layout)

        self._on_type_changed("IN")

    def _on_type_changed(self, movement_type):
        style = "color: #111111; font-size: 13px;"
        if movement_type == "IN":
            self.from_label.hide()
            self.from_combo.hide()
            self.to_label.setText("Giriş Lokasyonu *")
            self.to_label.setStyleSheet(style)
            self.to_label.show()
            self.to_combo.show()
        elif movement_type == "OUT":
            self.from_label.setText("Çıkış Lokasyonu *")
            self.from_label.setStyleSheet(style)
            self.from_label.show()
            self.from_combo.show()
            self.to_label.hide()
            self.to_combo.hide()
        elif movement_type == "TRANSFER":
            self.from_label.setText("Çıkış Lokasyonu *")
            self.from_label.setStyleSheet(style)
            self.from_label.show()
            self.from_combo.show()
            self.to_label.setText("Giriş Lokasyonu *")
            self.to_label.setStyleSheet(style)
            self.to_label.show()
            self.to_combo.show()

    def _save(self):
        if not self.customers:
            QMessageBox.warning(self, "Uyarı", "Önce müşteri eklemelisiniz.")
            return
        if not self.products:
            QMessageBox.warning(self, "Uyarı", "Önce ürün eklemelisiniz.")
            return
        if not self.locations:
            QMessageBox.warning(self, "Uyarı", "Önce lokasyon eklemelisiniz.")
            return
        if self.movement_type.currentText() == "TRANSFER":
            if self.from_combo.currentData() == self.to_combo.currentData():
                QMessageBox.warning(
                    self, "Uyarı",
                    "Çıkış ve giriş lokasyonu aynı olamaz."
                )
                return
        self.accept()

    def get_data(self):
        qdate   = self.movement_date.date()
        from datetime import date
        mv_date = date(qdate.year(), qdate.month(), qdate.day())
        return {
            "movement_type":    self.movement_type.currentText(),
            "customer_id":      self.customer_combo.currentData(),
            "product_id":       self.product_combo.currentData(),
            "from_location_id": self.from_combo.currentData(),
            "to_location_id":   self.to_combo.currentData(),
            "quantity":         self.quantity.value(),
            "reference":        self.reference.text().strip() or None,
            "notes":            self.notes.toPlainText().strip() or None,
            "movement_date":    mv_date,
        }


class MovementsWidget(QWidget):
    movement_saved = Signal()
    
    def __init__(self):
        super().__init__()
        self.movement_service = MovementService()
        self.customer_service = CustomerService()
        self.product_service  = ProductService()
        self.location_service = LocationService()
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Başlık ve buton
        top = QHBoxLayout()
        title = QLabel("🔄 Hareketler")
        title.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #1B3A6B;"
        )
        add_btn = QPushButton("+ Yeni Hareket")
        add_btn.setStyleSheet(
            "background:#2563EB; color:white; padding:8px 16px;"
            "border-radius:4px; font-size:13px;"
        )
        add_btn.clicked.connect(self._add_movement)
        top.addWidget(title)
        top.addStretch()
        top.addWidget(add_btn)
        layout.addLayout(top)

        # Filtreler
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)

        self.filter_type = QComboBox()
        self.filter_type.addItems(["Tümü", "IN", "OUT", "TRANSFER"])
        self.filter_type.setStyleSheet(
            "padding:7px; border:1px solid #d1d5db; border-radius:4px;"
        )
        self.filter_type.currentTextChanged.connect(self.load_data)

        self.filter_customer = QComboBox()
        self.filter_customer.addItem("Tüm Müşteriler", None)
        for c in self.customer_service.get_all_customers():
            self.filter_customer.addItem(c.name, c.id)
        self.filter_customer.setStyleSheet(
            "padding:7px; border:1px solid #d1d5db; border-radius:4px;"
        )
        self.filter_customer.currentIndexChanged.connect(self.load_data)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Referans ara...")
        self.search_input.setStyleSheet(
            "padding:8px; border:1px solid #d1d5db;"
            "border-radius:4px; font-size:13px;"
        )
        self.search_input.textChanged.connect(self._filter_table)

        filter_layout.addWidget(self._lbl("Tip:"))
        filter_layout.addWidget(self.filter_type)
        filter_layout.addWidget(self._lbl("Müşteri:"))
        filter_layout.addWidget(self.filter_customer)
        filter_layout.addWidget(self.search_input, 1)
        layout.addLayout(filter_layout)

        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Tarih", "Tip", "Müşteri",
            "Ürün", "Çıkış Lok.", "Giriş Lok.", "Miktar", "Referans"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 50)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.setColumnWidth(1, 100)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.setColumnWidth(2, 90)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        setup_table(self.table)
        layout.addWidget(self.table)

    def load_data(self):
        mv_type     = self.filter_type.currentText()
        customer_id = self.filter_customer.currentData()

        self.movements = self.movement_service.get_movements(
            movement_type=None if mv_type == "Tümü" else mv_type,
            customer_id=customer_id
        )
        self._populate_table(self.movements)

    def _populate_table(self, movements):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(movements))
        type_colors = {
            "IN":       ("#ffffff", "#16a34a"),
            "OUT":      ("#ffffff", "#dc2626"),
            "TRANSFER": ("#ffffff", "#d97706"),
        }
        for row, m in enumerate(movements):
            values = [
                str(m.id),
                str(m.movement_date),
                m.movement_type,
                m.customer.name if m.customer else "",
                m.product.name  if m.product  else "",
                m.from_loc.code if m.from_loc else "-",
                m.to_loc.code   if m.to_loc   else "-",
                format_qty(m.quantity),
                m.reference or "",
            ]
            for col, text in enumerate(values):
                if col == 2:
                    fg, bg = type_colors.get(text, ("#111111", "#ffffff"))
                    self.table.setItem(row, col, make_item(text, color=fg, bg_color=bg))
                elif col == 7:
                    self.table.setItem(row, col,
                        make_numeric_item(m.quantity, format_qty(m.quantity)))
                else:
                    self.table.setItem(row, col, make_item(text))
        self.table.setSortingEnabled(True)
    
    def _lbl(self, text):
        l = QLabel(text)
        l.setStyleSheet("color: #111111; font-size: 13px;")
        return l

    def _filter_table(self, text):
        text = text.lower()
        filtered = [
            m for m in self.movements
            if text in (m.reference or "").lower()
            or text in (m.product.name if m.product else "").lower()
        ]
        self._populate_table(filtered)

    def _add_movement(self):
        customers = self.customer_service.get_all_customers()
        products  = self.product_service.get_all_products()
        locations = self.location_service.get_all_locations()

        dialog = MovementDialog(
            parent=self,
            customers=customers,
            products=products,
            locations=locations
        )
        result = dialog.exec()
        dialog.deleteLater()

        if result == QDialog.Accepted:
            data    = dialog.get_data()
            mv_type = data["movement_type"]
            try:
                if mv_type == "IN":
                    self.movement_service.record_inbound(
                        customer_id=data["customer_id"],
                        product_id=data["product_id"],
                        to_location_id=data["to_location_id"],
                        quantity=data["quantity"],
                        reference=data["reference"],
                        notes=data["notes"],
                    )
                elif mv_type == "OUT":
                    self.movement_service.record_outbound(
                        customer_id=data["customer_id"],
                        product_id=data["product_id"],
                        from_location_id=data["from_location_id"],
                        quantity=data["quantity"],
                        reference=data["reference"],
                        notes=data["notes"],
                    )
                elif mv_type == "TRANSFER":
                    self.movement_service.record_transfer(
                        customer_id=data["customer_id"],
                        product_id=data["product_id"],
                        from_location_id=data["from_location_id"],
                        to_location_id=data["to_location_id"],
                        quantity=data["quantity"],
                        reference=data["reference"],
                        notes=data["notes"],
                    )
                self.load_data()
                self.movement_saved.emit()
                QMessageBox.information(self, "Başarılı", "Hareket kaydedildi.")
            except InsufficientStockError as e:
                QMessageBox.critical(self, "Yetersiz Stok", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Hata", str(e))