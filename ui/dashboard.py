from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from services.stock_service import StockService
from services.movement_service import MovementService
from utils.table_helper import setup_table, make_item, make_numeric_item, format_qty
from datetime import date
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton
)
from datetime import date, timedelta
from PySide6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from PySide6.QtGui import QColor, QPainter

class KpiCard(QFrame):
    def __init__(self, title, value, color="#2563EB"):
        super().__init__()
        self.setObjectName("kpiCard")
        self.setFixedHeight(100)
        layout = QVBoxLayout(self)
        val_label = QLabel(str(value))
        val_label.setAlignment(Qt.AlignCenter)
        val_label.setStyleSheet(
            f"font-size: 28px; font-weight: bold; color: {color};"
        )
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 12px; color: #6b7280;")
        layout.addWidget(val_label)
        layout.addWidget(title_label)
        self.setStyleSheet("""
            #kpiCard {
                background: white;
                border-radius: 8px;
                border: 1px solid #e5e7eb;
            }
        """)


class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.stock_service    = StockService()
        self.movement_service = MovementService()
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Başlık ve yenile butonu
        top = QHBoxLayout()
        title = QLabel("📊 Dashboard")
        title.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #1B3A6B;"
        )
        refresh_btn = QPushButton("🔄 Yenile")
        refresh_btn.setStyleSheet(
            "background:#2563EB; color:white; padding:8px 16px;"
            "border-radius:4px; font-size:13px;"
        )
        refresh_btn.clicked.connect(self.refresh)
        top.addWidget(title)
        top.addStretch()
        top.addWidget(refresh_btn)
        layout.addLayout(top)

        # KPI kartları
        self.kpi_layout = QHBoxLayout()
        self.kpi_layout.setSpacing(15)
        layout.addLayout(self.kpi_layout)

        # Grafik
        chart_frame = QFrame()
        chart_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 8px;
                border: 1px solid #e5e7eb;
            }
        """)
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(10, 10, 10, 0)
        chart_layout.setSpacing(5)

        chart_title = QLabel("Son 7 Günlük Hareket")
        chart_title.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #374151; border: none;"
        )
        chart_layout.addWidget(chart_title)

        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setFixedHeight(270)
        self.chart_view.setStyleSheet("border: none;")
        chart_layout.addWidget(self.chart_view)
        chart_frame.setFixedHeight(275)
        layout.addWidget(chart_frame)

        # Stok özeti tablosu
        table_frame = QFrame()
        table_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 8px;
                border: 1px solid #e5e7eb;
            }
        """)
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(10, 10, 10, 10)

        table_title = QLabel("Stok Özeti")
        table_title.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #374151; border: none;"
        )
        table_layout.addWidget(table_title)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Müşteri", "Ürün", "SKU", "Miktar", "Birim"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        setup_table(self.table)
        table_layout.addWidget(self.table)
        layout.addWidget(table_frame)

    def refresh(self):
        # KPI kartlarını temizle
        while self.kpi_layout.count():
            item = self.kpi_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Verileri çek
        all_stock   = self.stock_service.get_all_stock()
        low_stock   = self.stock_service.get_low_stock()
        bugun_giris = self.movement_service.get_movements(
            start_date=date.today(), movement_type="IN")
        bugun_cikis = self.movement_service.get_movements(
            start_date=date.today(), movement_type="OUT")

        # KPI kartları
        cards = [
            ("Toplam Stok Kalemi", len(all_stock),   "#2563EB"),
            ("Bugün Giriş",        len(bugun_giris), "#16a34a"),
            ("Bugün Çıkış",        len(bugun_cikis), "#dc2626"),
            ("Düşük Stok Uyarısı", len(low_stock),  "#d97706"),
        ]
        for title, value, color in cards:
            self.kpi_layout.addWidget(KpiCard(title, value, color))

        # Grafik
        self._draw_chart()

        # Tabloyu doldur
        summary = self.stock_service.get_stock_summary()
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(summary))
        for row, item in enumerate(summary):
            self.table.setItem(row, 0, make_item(item.musteri))
            self.table.setItem(row, 1, make_item(item.urun))
            self.table.setItem(row, 2, make_item(item.sku))
            self.table.setItem(row, 3, make_numeric_item(
                item.toplam_miktar, format_qty(item.toplam_miktar)))
            self.table.setItem(row, 4, make_item(item.birim))
        self.table.setSortingEnabled(True)

    def _draw_chart(self):
        bugun      = date.today()
        gunler     = [bugun - timedelta(days=i) for i in range(6, -1, -1)]
        gun_etiket = [g.strftime("%d/%m") for g in gunler]

        giris_list    = []
        cikis_list    = []
        transfer_list = []

        for g in gunler:
            girisler   = self.movement_service.get_movements(
                start_date=g, end_date=g, movement_type="IN")
            cikislar   = self.movement_service.get_movements(
                start_date=g, end_date=g, movement_type="OUT")
            transferler = self.movement_service.get_movements(
                start_date=g, end_date=g, movement_type="TRANSFER")
            giris_list.append(sum(float(m.quantity) for m in girisler))
            cikis_list.append(sum(float(m.quantity) for m in cikislar))
            transfer_list.append(sum(float(m.quantity) for m in transferler))

        # Bar setleri
        giris_set = QBarSet("Giriş")
        giris_set.setColor(QColor("#16a34a"))
        for v in giris_list:
            giris_set.append(v)

        cikis_set = QBarSet("Çıkış")
        cikis_set.setColor(QColor("#dc2626"))
        for v in cikis_list:
            cikis_set.append(v)

        transfer_set = QBarSet("Transfer")
        transfer_set.setColor(QColor("#d97706"))
        for v in transfer_list:
            transfer_set.append(v)

        series = QBarSeries()
        series.append(giris_set)
        series.append(cikis_set)
        series.append(transfer_set)

        # Chart
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setBackgroundBrush(QColor("white"))
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        # X ekseni
        axis_x = QBarCategoryAxis()
        axis_x.append(gun_etiket)
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)

        # Y ekseni
        axis_y = QValueAxis()
        max_val = max(
            max(giris_list),
            max(cikis_list),
            max(transfer_list),
            1
        )
        axis_y.setRange(0, max_val * 1.2)
        axis_y.setLabelFormat("%d")
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)

        self.chart_view.setChart(chart)