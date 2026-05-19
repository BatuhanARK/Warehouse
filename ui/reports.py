from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QDateEdit, QFrame,
    QFileDialog, QMessageBox, QTabWidget
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor
from services.report_service import ReportService
from services.customer_service import CustomerService
from utils.table_helper import setup_table, make_item, make_numeric_item, format_qty


class ReportsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.report_service   = ReportService()
        self.customer_service = CustomerService()
        self._build_ui()

    def refresh(self):
        """Hareket kaydedilince açık sekmeyi otomatik yenile."""
        current_tab = self.tabs.currentIndex()
        if current_tab == 0 and hasattr(self, "mov_data"):
            self._generate_movement_report()
        elif current_tab == 1 and hasattr(self, "stock_data"):
            self._generate_stock_report()
        elif current_tab == 2 and hasattr(self, "cust_data"):
            self._generate_customer_report()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Başlık
        title = QLabel("📈 Raporlar")
        title.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #1B3A6B;"
        )
        layout.addWidget(title)

        # Sekmeler
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                background: white;
                padding: 0px;
                margin: 0px;
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
            QTabBar::tab {
                background: #f3f4f6;
                color: #374151;
                padding: 8px 20px;
                border: 1px solid #e5e7eb;
                border-bottom: none;
                border-radius: 4px 4px 0 0;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background: #1B3A6B;
                color: white;
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background: #2563EB;
                color: white;
            }
        """)
        self.tabs.setContentsMargins(0, 0, 0, 0)
        self.tabs.addTab(self._build_movement_report_tab(), "📋 Hareket Raporu")
        self.tabs.addTab(self._build_stock_report_tab(),    "📦 Stok Raporu")
        self.tabs.addTab(self._build_customer_report_tab(), "👥 Müşteri Raporu")

        layout.addWidget(self.tabs)

    # ── HAREKET RAPORU ──────────────────────────────────────
    def _build_movement_report_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 10, 15, 15)
        layout.setSpacing(12)

        # Filtreler
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        filter_layout.setContentsMargins(0, 0, 0, 0)

        self.mov_start = QDateEdit()
        self.mov_start.setDate(QDate.currentDate().addDays(-7))
        self.mov_start.setCalendarPopup(True)
        self.mov_start.setStyleSheet(
            "padding:6px; border:1px solid #d1d5db; border-radius:4px;"
        )

        self.mov_end = QDateEdit()
        self.mov_end.setDate(QDate.currentDate())
        self.mov_end.setCalendarPopup(True)
        self.mov_end.setStyleSheet(
            "padding:6px; border:1px solid #d1d5db; border-radius:4px;"
        )

        self.mov_type_filter = QComboBox()
        self.mov_type_filter.addItems(["Tümü", "IN", "OUT", "TRANSFER"])
        self.mov_type_filter.setStyleSheet(
            "padding:6px; border:1px solid #d1d5db; border-radius:4px;"
        )

        generate_btn = QPushButton("📊 Raporu Oluştur")
        generate_btn.setStyleSheet(
            "background:#2563EB; color:white; padding:8px 16px;"
            "border-radius:4px; font-size:13px;"
        )
        generate_btn.clicked.connect(self._generate_movement_report)

        excel_btn = QPushButton("📥 Excel'e Aktar")
        excel_btn.setStyleSheet(
            "background:#16a34a; color:white; padding:8px 16px;"
            "border-radius:4px; font-size:13px;"
        )
        excel_btn.clicked.connect(self._export_movement_excel)

        pdf_btn = QPushButton("📄 PDF'e Aktar")
        pdf_btn.setStyleSheet(
            "background:#dc2626; color:white; padding:8px 16px;"
            "border-radius:4px; font-size:13px;"
        )
        pdf_btn.clicked.connect(self._export_movement_pdf)

        filter_layout.addWidget(self._lbl("Başlangıç:"))
        filter_layout.addWidget(self.mov_start)
        filter_layout.addWidget(self._lbl("Bitiş:"))
        filter_layout.addWidget(self.mov_end)
        filter_layout.addWidget(self._lbl("Tip:"))
        filter_layout.addWidget(self.mov_type_filter)
        filter_layout.addStretch()
        filter_layout.addWidget(generate_btn)
        filter_layout.addWidget(excel_btn)
        filter_layout.addWidget(pdf_btn)
        filter_container = QWidget()
        filter_container.setContentsMargins(0, 0, 0, 0)
        filter_container.setStyleSheet("margin: 0px; padding: 0px;")
        widget.setStyleSheet("QWidget { margin: 0px; padding: 0px; }")
        filter_container.setLayout(filter_layout)
        layout.addWidget(filter_container)

        # Özet kartları
        self.mov_summary_layout = QHBoxLayout()
        self.mov_summary_layout.setSpacing(10)
        layout.addLayout(self.mov_summary_layout)

        # Tablo
        self.mov_table = QTableWidget()
        self.mov_table.setColumnCount(8)
        self.mov_table.setHorizontalHeaderLabels([
            "ID", "Tarih", "Tip", "Müşteri",
            "Ürün", "Çıkış Lok.", "Giriş Lok.", "Miktar"
        ])
        self.mov_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.mov_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.mov_table.setColumnWidth(0, 50)
        self.mov_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.mov_table.setColumnWidth(2, 90)
        self.mov_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        setup_table(self.mov_table)
        layout.addWidget(self.mov_table)

        self.mov_info = QLabel("")
        self.mov_info.setStyleSheet("color:#6b7280; font-size:12px;")
        layout.addWidget(self.mov_info)

        return widget

    # ── STOK RAPORU ─────────────────────────────────────────
    def _build_stock_report_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 10, 15, 15)
        layout.setSpacing(12)

        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        filter_layout.setContentsMargins(0, 0, 0, 0)

        self.stock_customer_filter = QComboBox()
        self.stock_customer_filter.addItem("Tüm Müşteriler", None)
        for c in self.customer_service.get_all_customers():
            self.stock_customer_filter.addItem(c.name, c.id)
        self.stock_customer_filter.setStyleSheet(
            "padding:6px; border:1px solid #d1d5db; border-radius:4px;"
        )

        generate_btn = QPushButton("📊 Raporu Oluştur")
        generate_btn.setStyleSheet(
            "background:#2563EB; color:white; padding:8px 16px;"
            "border-radius:4px; font-size:13px;"
        )
        generate_btn.clicked.connect(self._generate_stock_report)

        excel_btn = QPushButton("📥 Excel'e Aktar")
        excel_btn.setStyleSheet(
            "background:#16a34a; color:white; padding:8px 16px;"
            "border-radius:4px; font-size:13px;"
        )
        excel_btn.clicked.connect(self._export_stock_excel)
        
        pdf_btn = QPushButton("📄 PDF'e Aktar")
        pdf_btn.setStyleSheet(
            "background:#dc2626; color:white; padding:8px 16px;"
            "border-radius:4px; font-size:13px;"
        )
        pdf_btn.clicked.connect(self._export_stock_pdf)

        filter_layout.addWidget(self._lbl("Müşteri:"))
        filter_layout.addWidget(self.stock_customer_filter)
        filter_layout.addStretch()
        filter_layout.addWidget(generate_btn)
        filter_layout.addWidget(excel_btn)
        filter_layout.addWidget(pdf_btn)
        filter_container = QWidget()
        filter_container.setContentsMargins(0, 0, 0, 0)
        filter_container.setStyleSheet("margin: 0px; padding: 0px;")
        widget.setStyleSheet("QWidget { margin: 0px; padding: 0px; }")
        filter_container.setLayout(filter_layout)
        layout.addWidget(filter_container)

        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(6)
        self.stock_table.setHorizontalHeaderLabels([
            "Müşteri", "SKU", "Ürün Adı",
            "Lokasyon", "Miktar", "Birim"
        ])
        self.stock_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.stock_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.stock_table.setColumnWidth(4, 100)
        self.stock_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.stock_table.setColumnWidth(5, 80)
        self.stock_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        setup_table(self.stock_table)
        layout.addWidget(self.stock_table)

        self.stock_info = QLabel("")
        self.stock_info.setStyleSheet("color:#6b7280; font-size:12px;")
        layout.addWidget(self.stock_info)

        return widget

    # ── MÜŞTERİ RAPORU ──────────────────────────────────────
    def _build_customer_report_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 10, 15, 15)
        layout.setSpacing(12)

        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        filter_layout.setContentsMargins(0, 0, 0, 0)

        self.cust_filter = QComboBox()
        self.cust_filter.addItem("Müşteri Seçin", None)
        for c in self.customer_service.get_all_customers():
            self.cust_filter.addItem(f"{c.code} - {c.name}", c.id)
        self.cust_filter.setStyleSheet(
            "padding:6px; border:1px solid #d1d5db; border-radius:4px;"
        )

        self.cust_start = QDateEdit()
        self.cust_start.setDate(QDate.currentDate().addDays(-30))
        self.cust_start.setCalendarPopup(True)
        self.cust_start.setStyleSheet(
            "padding:6px; border:1px solid #d1d5db; border-radius:4px;"
        )

        self.cust_end = QDateEdit()
        self.cust_end.setDate(QDate.currentDate())
        self.cust_end.setCalendarPopup(True)
        self.cust_end.setStyleSheet(
            "padding:6px; border:1px solid #d1d5db; border-radius:4px;"
        )

        generate_btn = QPushButton("📊 Raporu Oluştur")
        generate_btn.setStyleSheet(
            "background:#2563EB; color:white; padding:8px 16px;"
            "border-radius:4px; font-size:13px;"
        )
        generate_btn.clicked.connect(self._generate_customer_report)

        excel_btn = QPushButton("📥 Excel'e Aktar")
        excel_btn.setStyleSheet(
            "background:#16a34a; color:white; padding:8px 16px;"
            "border-radius:4px; font-size:13px;"
        )
        excel_btn.clicked.connect(self._export_customer_excel)
        
        pdf_btn = QPushButton("📄 PDF'e Aktar")
        pdf_btn.setStyleSheet(
            "background:#dc2626; color:white; padding:8px 16px;"
            "border-radius:4px; font-size:13px;"
        )
        pdf_btn.clicked.connect(self._export_customer_pdf)

        filter_layout.addWidget(self._lbl("Müşteri:"))
        filter_layout.addWidget(self.cust_filter)
        filter_layout.addWidget(self._lbl("Başlangıç:"))
        filter_layout.addWidget(self.cust_start)
        filter_layout.addWidget(self._lbl("Bitiş:"))
        filter_layout.addWidget(self.cust_end)
        filter_layout.addStretch()
        filter_layout.addWidget(generate_btn)
        filter_layout.addWidget(excel_btn)
        filter_layout.addWidget(pdf_btn)
        filter_container = QWidget()
        filter_container.setContentsMargins(0, 0, 0, 0)
        filter_container.setStyleSheet("margin: 0px; padding: 0px;")
        widget.setStyleSheet("QWidget { margin: 0px; padding: 0px; }")
        filter_container.setLayout(filter_layout)
        layout.addWidget(filter_container)

        self.cust_table = QTableWidget()
        self.cust_table.setColumnCount(7)
        self.cust_table.setHorizontalHeaderLabels([
            "ID", "Tarih", "Tip", "Ürün",
            "Çıkış Lok.", "Giriş Lok.", "Miktar"
        ])
        self.cust_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cust_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.cust_table.setColumnWidth(0, 50)
        self.cust_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.cust_table.setColumnWidth(2, 90)
        self.cust_table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        setup_table(self.cust_table)
        layout.addWidget(self.cust_table)

        self.cust_info = QLabel("")
        self.cust_info.setStyleSheet("color:#6b7280; font-size:12px;")
        layout.addWidget(self.cust_info)

        return widget

    # ── VERİ YÜKLEME ────────────────────────────────────────
    def _get_date(self, date_edit):
        qd = date_edit.date()
        from datetime import date
        return date(qd.year(), qd.month(), qd.day())

    def _generate_movement_report(self):
        start   = self._get_date(self.mov_start)
        end     = self._get_date(self.mov_end)
        mv_type = self.mov_type_filter.currentText()
        if mv_type == "Tümü":
            mv_type = None

        movements = self.report_service.get_movement_report(start, end, mv_type)
        self.mov_data = movements

        # Özet kartları
        while self.mov_summary_layout.count():
            item = self.mov_summary_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        total   = len(movements)
        giris   = sum(1 for m in movements if m.movement_type == "IN")
        cikis   = sum(1 for m in movements if m.movement_type == "OUT")
        transfer = sum(1 for m in movements if m.movement_type == "TRANSFER")

        for label, val, color in [
            ("Toplam Hareket", total,    "#2563EB"),
            ("Giriş (IN)",     giris,    "#16a34a"),
            ("Çıkış (OUT)",    cikis,    "#dc2626"),
            ("Transfer",       transfer, "#d97706"),
        ]:
            card = self._make_summary_card(label, str(val), color)
            self.mov_summary_layout.addWidget(card)

        # Tabloyu doldur
        type_colors = {
            "IN":       ("#ffffff", "#16a34a"),
            "OUT":      ("#ffffff", "#dc2626"),
            "TRANSFER": ("#ffffff", "#d97706"),
        }
        self.mov_table.setSortingEnabled(False)
        self.mov_table.setRowCount(len(movements))
        for row, m in enumerate(movements):
            values = [
                str(m.id),
                str(m.movement_date),
                m.movement_type,
                m.customer.name if m.customer else "",
                m.product.name  if m.product  else "",
                m.from_loc.code if m.from_loc  else "-",
                m.to_loc.code   if m.to_loc    else "-",
                format_qty(m.quantity),
            ]
            for col, text in enumerate(values):
                if col == 2:
                    fg, bg = type_colors.get(text, ("#111111", "#ffffff"))
                    self.mov_table.setItem(row, col, make_item(text, color=fg, bg_color=bg))
                elif col == 7:
                    self.mov_table.setItem(row, col,
                        make_numeric_item(m.quantity, format_qty(m.quantity)))
                else:
                    self.mov_table.setItem(row, col, make_item(text))
        self.mov_table.setSortingEnabled(True)
        self.mov_info.setText(f"{len(movements)} hareket listelendi.")

    def _generate_stock_report(self):
        customer_id = self.stock_customer_filter.currentData()
        stocks      = self.report_service.get_stock_report(customer_id)
        self.stock_data = stocks

        self.stock_table.setSortingEnabled(False)
        self.stock_table.setRowCount(len(stocks))
        for row, s in enumerate(stocks):
            qty = float(s.quantity)
            qty_color = "#dc2626" if qty == 0 else "#d97706" if qty <= 10 else None
            values = [
                s.customer.name if s.customer else "",
                s.product.sku   if s.product  else "",
                s.product.name  if s.product  else "",
                s.location.code if s.location else "",
                format_qty(qty),
                s.product.unit  if s.product  else "",
            ]
            for col, text in enumerate(values):
                color = qty_color if col == 4 else None
                if col == 4:
                    self.stock_table.setItem(row, col,
                        make_numeric_item(s.quantity, format_qty(qty), color))
                else:
                    self.stock_table.setItem(row, col, make_item(text, color=color))
        self.stock_table.setSortingEnabled(True)
        self.stock_info.setText(f"{len(stocks)} stok kalemi listelendi.")

    def _generate_customer_report(self):
        customer_id = self.cust_filter.currentData()
        if not customer_id:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir müşteri seçin.")
            return
        start = self._get_date(self.cust_start)
        end   = self._get_date(self.cust_end)

        movements   = self.report_service.get_movement_report(start, end, customer_id=customer_id)
        self.cust_data = movements

        type_colors = {
            "IN":       ("#ffffff", "#16a34a"),
            "OUT":      ("#ffffff", "#dc2626"),
            "TRANSFER": ("#ffffff", "#d97706"),
        }
        self.cust_table.setSortingEnabled(False)
        self.cust_table.setRowCount(len(movements))
        for row, m in enumerate(movements):
            values = [
                str(m.id),
                str(m.movement_date),
                m.movement_type,
                m.product.name  if m.product  else "",
                m.from_loc.code if m.from_loc  else "-",
                m.to_loc.code   if m.to_loc    else "-",
                format_qty(m.quantity),
            ]
            for col, text in enumerate(values):
                if col == 2:
                    fg, bg = type_colors.get(text, ("#111111", "#ffffff"))
                    self.cust_table.setItem(row, col, make_item(text, color=fg, bg_color=bg))
                elif col == 6:
                    self.cust_table.setItem(row, col,
                        make_numeric_item(m.quantity, format_qty(m.quantity)))
                else:
                    self.cust_table.setItem(row, col, make_item(text))
        self.cust_table.setSortingEnabled(True)
        self.cust_info.setText(f"{len(movements)} hareket listelendi.")

    # ── PDF AKTARIM ────────────────────────────────────────
    def _export_movement_pdf(self):
        if not hasattr(self, "mov_data") or not self.mov_data:
            QMessageBox.warning(self, "Uyarı", "Önce raporu oluşturun.")
            return
        start  = self._get_date(self.mov_start).strftime("%d-%m-%Y")
        end    = self._get_date(self.mov_end).strftime("%d-%m-%Y")
        tip    = self.mov_type_filter.currentText()
        fname  = f"{start}_{end}_{tip}_HAREKET-RAPORU.pdf"
        path, _ = QFileDialog.getSaveFileName(
            self, "PDF Kaydet", fname, "PDF Files (*.pdf)")
        if path:
            try:
                self.report_service.export_movements_pdf(self.mov_data, path)
                QMessageBox.information(self, "Başarılı", f"PDF kaydedildi:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Hata", str(e))

    def _export_stock_pdf(self):
        if not hasattr(self, "stock_data") or not self.stock_data:
            QMessageBox.warning(self, "Uyarı", "Önce raporu oluşturun.")
            return
        musteri = self.stock_customer_filter.currentText()
        fname   = f"{musteri}_STOK-RAPORU.pdf"
        path, _ = QFileDialog.getSaveFileName(
            self, "PDF Kaydet", fname, "PDF Files (*.pdf)")
        if path:
            try:
                self.report_service.export_stock_pdf(self.stock_data, path)
                QMessageBox.information(self, "Başarılı", f"PDF kaydedildi:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Hata", str(e))

    def _export_customer_pdf(self):
        if not hasattr(self, "cust_data") or not self.cust_data:
            QMessageBox.warning(self, "Uyarı", "Önce raporu oluşturun.")
            return
        musteri = self.cust_filter.currentText()
        start   = self._get_date(self.cust_start).strftime("%d-%m-%Y")
        end     = self._get_date(self.cust_end).strftime("%d-%m-%Y")
        fname   = f"{musteri}_{start}_{end}_HAREKET-RAPORU.pdf"
        path, _ = QFileDialog.getSaveFileName(
            self, "PDF Kaydet", fname, "PDF Files (*.pdf)")
        if path:
            try:
                self.report_service.export_movements_pdf(self.cust_data, path)
                QMessageBox.information(self, "Başarılı", f"PDF kaydedildi:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Hata", str(e))
    
    # ── EXCEL AKTARIM ────────────────────────────────────────
    def _export_movement_excel(self):
        if not hasattr(self, "mov_data") or not self.mov_data:
            QMessageBox.warning(self, "Uyarı", "Önce raporu oluşturun.")
            return
        start  = self._get_date(self.mov_start).strftime("%d-%m-%Y")
        end    = self._get_date(self.mov_end).strftime("%d-%m-%Y")
        tip    = self.mov_type_filter.currentText()  # Tümü, IN, OUT, TRANSFER
        fname  = f"{start}_{end}_{tip}_HAREKET-RAPORU.xlsx"
        path, _ = QFileDialog.getSaveFileName(
            self, "Excel Kaydet", fname, "Excel Files (*.xlsx)")
        if path:
            try:
                self.report_service.export_movements_excel(self.mov_data, path)
                QMessageBox.information(self, "Başarılı", f"Dosya kaydedildi:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Hata", str(e))

    def _export_stock_excel(self):
        if not hasattr(self, "stock_data") or not self.stock_data:
            QMessageBox.warning(self, "Uyarı", "Önce raporu oluşturun.")
            return
        musteri = self.stock_customer_filter.currentText()
        fname   = f"{musteri}_STOK-RAPORU.xlsx"
        path, _ = QFileDialog.getSaveFileName(
            self, "Excel Kaydet", fname, "Excel Files (*.xlsx)")
        if path:
            try:
                self.report_service.export_stock_excel(self.stock_data, path)
                QMessageBox.information(self, "Başarılı", f"Dosya kaydedildi:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Hata", str(e))

    def _export_customer_excel(self):
        if not hasattr(self, "cust_data") or not self.cust_data:
            QMessageBox.warning(self, "Uyarı", "Önce raporu oluşturun.")
            return
        musteri = self.cust_filter.currentText()
        start   = self._get_date(self.cust_start).strftime("%d-%m-%Y")
        end     = self._get_date(self.cust_end).strftime("%d-%m-%Y")
        fname   = f"{musteri}_{start}_{end}_HAREKET-RAPORU.xlsx"
        path, _ = QFileDialog.getSaveFileName(
            self, "Excel Kaydet", fname, "Excel Files (*.xlsx)")
        if path:
            try:
                self.report_service.export_movements_excel(self.cust_data, path)
                QMessageBox.information(self, "Başarılı", f"Dosya kaydedildi:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Hata", str(e))

    def _lbl(self, text):
        l = QLabel(text)
        l.setStyleSheet("color: #111111; font-size: 13px;")
        return l

    def _make_summary_card(self, title, value, color):
        card = QFrame()
        card.setFixedHeight(80)
        card.setObjectName("kpiCard")
        card.setStyleSheet("""
            QFrame#kpiCard {
                background: white;
                border-radius: 8px;
                border: 1px solid #e5e7eb;
            }
        """)
        card_layout = QVBoxLayout(card)
        val_lbl = QLabel(value)
        val_lbl.setAlignment(Qt.AlignCenter)
        val_lbl.setStyleSheet(
            f"font-size: 24px; font-weight: bold; color: {color};"
        )
        title_lbl = QLabel(title)
        title_lbl.setAlignment(Qt.AlignCenter)
        title_lbl.setStyleSheet("font-size: 11px; color: #6b7280;")
        card_layout.addWidget(val_lbl)
        card_layout.addWidget(title_lbl)
        return card