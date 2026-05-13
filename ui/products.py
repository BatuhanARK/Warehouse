from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialog, QFormLayout, QLineEdit,
    QMessageBox, QComboBox
)
from PySide6.QtCore import Qt
from services.product_service import ProductService
from utils.table_helper import setup_table, make_item, format_qty
from utils.base_dialog import BaseDialog

class ProductDialog(BaseDialog):
    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.product = product
        self.setWindowTitle("Ürün Ekle" if not product else "Ürün Düzenle")
        self.setMinimumWidth(400)
        self._build_ui()

    def _build_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(12)

        self.sku         = QLineEdit()
        self.name        = QLineEdit()
        self.description = QLineEdit()
        self.category    = QLineEdit()
        self.weight_kg   = QLineEdit()

        self.unit = QComboBox()
        self.unit.addItems(["PCS", "KG", "CBM", "PLT", "BOX", "LT"])

        layout.addRow("SKU *",       self.sku)
        layout.addRow("Ürün Adı *",  self.name)
        layout.addRow("Birim",       self.unit)
        layout.addRow("Kategori",    self.category)
        layout.addRow("Ağırlık (kg)", self.weight_kg)
        layout.addRow("Açıklama",    self.description)

        # Düzenleme modunda mevcut değerleri doldur
        if self.product:
            self.sku.setText(self.product.sku)
            self.sku.setEnabled(False)
            self.name.setText(self.product.name or "")
            self.description.setText(self.product.description or "")
            self.category.setText(self.product.category or "")
            self.weight_kg.setText(str(self.product.weight_kg) if self.product.weight_kg else "")
            index = self.unit.findText(self.product.unit)
            if index >= 0:
                self.unit.setCurrentIndex(index)

        # Butonlar
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

    def _save(self):
        if not self.sku.text().strip() or not self.name.text().strip():
            QMessageBox.warning(self, "Uyarı", "SKU ve Ürün Adı zorunludur.")
            return
        weight = self.weight_kg.text().strip()
        if weight:
            try:
                float(weight)
            except ValueError:
                QMessageBox.warning(self, "Uyarı", "Ağırlık sayısal olmalıdır.")
                return
        self.accept()

    def get_data(self):
        weight = self.weight_kg.text().strip()
        return {
            "sku":         self.sku.text().strip(),
            "name":        self.name.text().strip(),
            "unit":        self.unit.currentText(),
            "category":    self.category.text().strip() or None,
            "weight_kg":   float(weight) if weight else None,
            "description": self.description.text().strip() or None,
        }


class ProductsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.service = ProductService()
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Başlık ve buton satırı
        top = QHBoxLayout()
        title = QLabel("🛒 Ürünler")
        title.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #1B3A6B;"
        )
        add_btn = QPushButton("+ Yeni Ürün")
        add_btn.setStyleSheet(
            "background:#2563EB; color:white; padding:8px 16px;"
            "border-radius:4px; font-size:13px;"
        )
        add_btn.clicked.connect(self._add_product)
        top.addWidget(title)
        top.addStretch()
        top.addWidget(add_btn)
        layout.addLayout(top)

        # Arama
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Ürün ara (ad veya SKU)...")
        self.search_input.setStyleSheet(
            "padding:8px; border:1px solid #d1d5db;"
            "border-radius:4px; font-size:13px;"
        )
        self.search_input.textChanged.connect(self._filter_table)
        layout.addWidget(self.search_input)

        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ["ID", "SKU", "Ürün Adı", "Birim", "Kategori", "Ağırlık (kg)", "Açıklama", "İşlemler"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 50)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.setColumnWidth(7, 180)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        setup_table(self.table)
        layout.addWidget(self.table)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)

    def load_data(self):
        self.products = self.service.get_all_products()
        self._populate_table(self.products)

    def _populate_table(self, products):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(products))
        for row, p in enumerate(products):
            values = [
                str(p.id), p.sku, p.name,
                p.unit or "", p.category or "",
                format_qty(p.weight_kg) if p.weight_kg else "",
                p.description or "",
            ]
            for col, text in enumerate(values):
                self.table.setItem(row, col, make_item(text))

            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(4, 2, 4, 2)
            btn_layout.setSpacing(4)
            edit_btn = QPushButton("Düzenle")
            edit_btn.setStyleSheet(
                "background:#2563EB; color:white; padding:4px 8px; border-radius:3px;"
            )
            edit_btn.clicked.connect(lambda _, prod=p: self._edit_product(prod))
            del_btn = QPushButton("Pasif")
            del_btn.setStyleSheet(
                "background:#dc2626; color:white; padding:4px 8px; border-radius:3px;"
            )
            del_btn.clicked.connect(lambda _, prod=p: self._deactivate_product(prod))
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(del_btn)
            self.table.setCellWidget(row, 7, btn_widget)
        self.table.setSortingEnabled(True)

    def _filter_table(self, text):
        text = text.lower()
        filtered = [
            p for p in self.products
            if text in p.name.lower() or text in p.sku.lower()
        ]
        self._populate_table(filtered)

    def _add_product(self):
        try:
            dialog = ProductDialog(self)
            result = dialog.exec()
            if result == QDialog.Accepted:
                data = dialog.get_data()
                try:
                    self.service.add_product(**data)
                    self.load_data()
                    QMessageBox.information(self, "Başarılı", "Ürün eklendi.")
                except Exception as e:
                    QMessageBox.critical(self, "Hata", str(e))
        finally:
            dialog.deleteLater()

    def _edit_product(self, product):
        try:
            dialog = ProductDialog(self, product)
            result = dialog.exec()
            if result == QDialog.Accepted:
                data = dialog.get_data()
                data.pop("sku", None)
                try:
                    self.service.update_product(product.id, **data)
                    self.load_data()
                    QMessageBox.information(self, "Başarılı", "Ürün güncellendi.")
                except Exception as e:
                    QMessageBox.critical(self, "Hata", str(e))
        finally:
            dialog.deleteLater()

    def _deactivate_product(self, product):
        reply = QMessageBox.question(
            self, "Onay",
            f"'{product.name}' ürününü pasife almak istiyor musunuz?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self.service.deactivate_product(product.id)
                self.load_data()
                QMessageBox.information(self, "Başarılı", "Ürün pasife alındı.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", str(e))