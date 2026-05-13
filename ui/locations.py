from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialog, QFormLayout, QLineEdit,
    QMessageBox
)
from PySide6.QtCore import Qt
from services.location_service import LocationService
from utils.table_helper import setup_table, make_item, format_qty
from utils.base_dialog import BaseDialog

class LocationDialog(BaseDialog):
    def __init__(self, parent=None, location=None):
        super().__init__(parent)
        self.location = location
        self.setWindowTitle("Lokasyon Ekle" if not location else "Lokasyon Düzenle")
        self.setMinimumWidth(400)
        self._build_ui()

    def _build_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(12)

        self.code       = QLineEdit()
        self.aisle      = QLineEdit()
        self.rack       = QLineEdit()
        self.bin        = QLineEdit()
        self.max_weight = QLineEdit()
        self.max_volume = QLineEdit()

        self.code.setPlaceholderText("örn: A-01-01")
        self.aisle.setPlaceholderText("örn: A")
        self.rack.setPlaceholderText("örn: 01")
        self.bin.setPlaceholderText("örn: 01")
        self.max_weight.setPlaceholderText("kg cinsinden")
        self.max_volume.setPlaceholderText("m³ cinsinden")

        layout.addRow("Kod *",          self.code)
        layout.addRow("Koridor",        self.aisle)
        layout.addRow("Raf",            self.rack)
        layout.addRow("Göz",            self.bin)
        layout.addRow("Maks. Ağırlık",  self.max_weight)
        layout.addRow("Maks. Hacim",    self.max_volume)

        if self.location:
            self.code.setText(self.location.code)
            self.code.setEnabled(False)
            self.aisle.setText(self.location.aisle or "")
            self.rack.setText(self.location.rack or "")
            self.bin.setText(self.location.bin or "")
            self.max_weight.setText(
                str(self.location.max_weight) if self.location.max_weight else "")
            self.max_volume.setText(
                str(self.location.max_volume) if self.location.max_volume else "")

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
        if not self.code.text().strip():
            QMessageBox.warning(self, "Uyarı", "Kod alanı zorunludur.")
            return
        for field, label in [(self.max_weight, "Maks. Ağırlık"),
                              (self.max_volume, "Maks. Hacim")]:
            val = field.text().strip()
            if val:
                try:
                    float(val)
                except ValueError:
                    QMessageBox.warning(self, "Uyarı", f"{label} sayısal olmalıdır.")
                    return
        self.accept()

    def get_data(self):
        max_w = self.max_weight.text().strip()
        max_v = self.max_volume.text().strip()
        return {
            "code":       self.code.text().strip(),
            "aisle":      self.aisle.text().strip() or None,
            "rack":       self.rack.text().strip() or None,
            "bin":        self.bin.text().strip() or None,
            "max_weight": float(max_w) if max_w else None,
            "max_volume": float(max_v) if max_v else None,
        }


class LocationsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.service = LocationService()
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Başlık ve buton
        top = QHBoxLayout()
        title = QLabel("📍 Lokasyonlar")
        title.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #1B3A6B;"
        )
        add_btn = QPushButton("+ Yeni Lokasyon")
        add_btn.setStyleSheet(
            "background:#2563EB; color:white; padding:8px 16px;"
            "border-radius:4px; font-size:13px;"
        )
        add_btn.clicked.connect(self._add_location)
        top.addWidget(title)
        top.addStretch()
        top.addWidget(add_btn)
        layout.addLayout(top)

        # Arama
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Lokasyon ara (kod veya koridor)...")
        self.search_input.setStyleSheet(
            "padding:8px; border:1px solid #d1d5db;"
            "border-radius:4px; font-size:13px;"
        )
        self.search_input.textChanged.connect(self._filter_table)
        layout.addWidget(self.search_input)

        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Kod", "Koridor", "Raf", "Göz",
            "Maks. Ağırlık", "Maks. Hacim", "İşlemler"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 50)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Fixed)
        self.table.setColumnWidth(7, 180)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        setup_table(self.table)
        layout.addWidget(self.table)

    def load_data(self):
        self.locations = self.service.get_all_locations()
        self._populate_table(self.locations)

    def _populate_table(self, locations):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(locations))
        for row, loc in enumerate(locations):
            values = [
                str(loc.id), loc.code,
                loc.aisle or "", loc.rack or "", loc.bin or "",
                format_qty(loc.max_weight) if loc.max_weight else "",
                format_qty(loc.max_volume) if loc.max_volume else "",
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
            edit_btn.clicked.connect(lambda _, l=loc: self._edit_location(l))
            del_btn = QPushButton("Pasif")
            del_btn.setStyleSheet(
                "background:#dc2626; color:white; padding:4px 8px; border-radius:3px;"
            )
            del_btn.clicked.connect(lambda _, l=loc: self._deactivate_location(l))
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(del_btn)
            self.table.setCellWidget(row, 7, btn_widget)
        self.table.setSortingEnabled(True)

    def _filter_table(self, text):
        text = text.lower()
        filtered = [
            loc for loc in self.locations
            if text in loc.code.lower()
            or text in (loc.aisle or "").lower()
        ]
        self._populate_table(filtered)

    def _add_location(self):
        try:
            dialog = LocationDialog(self)
            result = dialog.exec()
            if result == QDialog.Accepted:
                data = dialog.get_data()
                try:
                    self.service.add_location(**data)
                    self.load_data()
                    QMessageBox.information(self, "Başarılı", "Lokasyon eklendi.")
                except Exception as e:
                    QMessageBox.critical(self, "Hata", str(e))
        finally:
            dialog.deleteLater()

    def _edit_location(self, location):
        try:
            dialog = LocationDialog(self, location)
            result = dialog.exec()
            if result == QDialog.Accepted:
                data = dialog.get_data()
                data.pop("code", None)
                try:
                    loc = self.service.get_location_by_id(location.id)
                    for key, value in data.items():
                        if hasattr(loc, key):
                            setattr(loc, key, value)
                    self.service.session.commit()
                    self.load_data()
                    QMessageBox.information(self, "Başarılı", "Lokasyon güncellendi.")
                except Exception as e:
                    QMessageBox.critical(self, "Hata", str(e))
        finally:
            dialog.deleteLater()

    def _deactivate_location(self, location):
        reply = QMessageBox.question(
            self, "Onay",
            f"'{location.code}' lokasyonunu pasife almak istiyor musunuz?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self.service.deactivate_location(location.id)
                self.load_data()
                QMessageBox.information(self, "Başarılı", "Lokasyon pasife alındı.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", str(e))