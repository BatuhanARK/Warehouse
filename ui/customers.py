from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialog, QFormLayout, QLineEdit,
    QMessageBox, QFrame
)
from PySide6.QtCore import Qt
from services.customer_service import CustomerService
from utils.table_helper import setup_table, make_item
from utils.base_dialog import BaseDialog

class CustomerDialog(BaseDialog):
    def __init__(self, parent=None, customer=None):
        super().__init__(parent)
        self.customer = customer
        self.setWindowTitle("Müşteri Ekle" if not customer else "Müşteri Düzenle")
        self.setMinimumWidth(400)
        self._build_ui()

    def _build_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(12)

        self.code    = QLineEdit()
        self.name    = QLineEdit()
        self.contact = QLineEdit()
        self.email   = QLineEdit()
        self.phone   = QLineEdit()

        layout.addRow("Kod *",     self.code)
        layout.addRow("Ad *",      self.name)
        layout.addRow("İlgili",    self.contact)
        layout.addRow("E-posta",   self.email)
        layout.addRow("Telefon",   self.phone)

        # Düzenleme modunda mevcut değerleri doldur
        if self.customer:
            self.code.setText(self.customer.code)
            self.code.setEnabled(False)
            self.name.setText(self.customer.name or "")
            self.contact.setText(self.customer.contact or "")
            self.email.setText(self.customer.email or "")
            self.phone.setText(self.customer.phone or "")

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
        if not self.code.text().strip() or not self.name.text().strip():
            QMessageBox.warning(self, "Uyarı", "Kod ve Ad alanları zorunludur.")
            return
        self.accept()

    def get_data(self):
        return {
            "code":    self.code.text().strip(),
            "name":    self.name.text().strip(),
            "contact": self.contact.text().strip() or None,
            "email":   self.email.text().strip() or None,
            "phone":   self.phone.text().strip() or None,
        }


class CustomersWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.service = CustomerService()
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Başlık ve buton satırı
        top = QHBoxLayout()
        title = QLabel("👥 Müşteriler")
        title.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #1B3A6B;"
        )
        add_btn = QPushButton("+ Yeni Müşteri")
        add_btn.setStyleSheet(
            "background:#2563EB; color:white; padding:8px 16px;"
            "border-radius:4px; font-size:13px;"
        )
        add_btn.clicked.connect(self._add_customer)
        top.addWidget(title)
        top.addStretch()
        top.addWidget(add_btn)
        layout.addLayout(top)

        # Arama
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Müşteri ara...")
        self.search_input.setStyleSheet(
            "padding:8px; border:1px solid #d1d5db; border-radius:4px; font-size:13px;"
        )
        self.search_input.textChanged.connect(self._filter_table)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Kod", "Ad", "İlgili Kişi", "E-posta", "Telefon", "İşlemler"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 50)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.setColumnWidth(6, 180)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        setup_table(self.table)
        layout.addWidget(self.table)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)

    def load_data(self):
        self.customers = self.service.get_all_customers()
        self._populate_table(self.customers)

    def _populate_table(self, customers):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(customers))
        for row, c in enumerate(customers):
            self.table.setItem(row, 0, make_item(str(c.id)))
            self.table.setItem(row, 1, make_item(c.code))
            self.table.setItem(row, 2, make_item(c.name))
            self.table.setItem(row, 3, make_item(c.contact or ""))
            self.table.setItem(row, 4, make_item(c.email or ""))
            self.table.setItem(row, 5, make_item(c.phone or ""))

            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(4, 2, 4, 2)
            btn_layout.setSpacing(4)
            edit_btn = QPushButton("Düzenle")
            edit_btn.setStyleSheet(
                "background:#2563EB; color:white; padding:4px 8px; border-radius:3px;"
            )
            edit_btn.clicked.connect(lambda _, cust=c: self._edit_customer(cust))
            del_btn = QPushButton("Pasif")
            del_btn.setStyleSheet(
                "background:#dc2626; color:white; padding:4px 8px; border-radius:3px;"
            )
            del_btn.clicked.connect(lambda _, cust=c: self._deactivate_customer(cust))
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(del_btn)
            self.table.setCellWidget(row, 6, btn_widget)
        self.table.setSortingEnabled(True)

    def _filter_table(self, text):
        text = text.lower()
        filtered = [
            c for c in self.customers
            if text in c.name.lower() or text in c.code.lower()
        ]
        self._populate_table(filtered)

    def _add_customer(self):
        try:
            dialog = CustomerDialog(self)
            result = dialog.exec()
            if result == QDialog.Accepted:
                data = dialog.get_data()
                try:
                    self.service.add_customer(**data)
                    self.load_data()
                    QMessageBox.information(self, "Başarılı", "Müşteri eklendi.")
                except Exception as e:
                    QMessageBox.critical(self, "Hata", str(e))
        finally:
            dialog.deleteLater()

    def _edit_customer(self, customer):
        try:
            dialog = CustomerDialog(self, customer)
            result = dialog.exec()
            if result == QDialog.Accepted:
                data = dialog.get_data()
                try:
                    self.service.update_customer(customer.id, **data)
                    self.load_data()
                    QMessageBox.information(self, "Başarılı", "Müşteri güncellendi.")
                except Exception as e:
                    QMessageBox.critical(self, "Hata", str(e))
        finally:
            dialog.deleteLater()
        
    def _deactivate_customer(self, customer):
        reply = QMessageBox.question(
            self, "Onay",
            f"'{customer.name}' müşterisini pasife almak istiyor musunuz?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self.service.deactivate_customer(customer.id)
                self.load_data()
                QMessageBox.information(self, "Başarılı", "Müşteri pasife alındı.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", str(e))