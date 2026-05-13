from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QPushButton, QStackedWidget,
    QLabel, QFrame
)
from PySide6.QtCore import Qt

from ui.dashboard import DashboardWidget
from ui.customers import CustomersWidget
from ui.products import ProductsWidget
from ui.locations import LocationsWidget
from ui.movements import MovementsWidget
from ui.stock_view import StockViewWidget
from ui.reports import ReportsWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Warehouse Management System")
        self.setMinimumSize(1200, 750)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = self._build_sidebar()
        main_layout.addWidget(sidebar)

        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setStyleSheet("color: #e0e0e0;")
        main_layout.addWidget(line)

        self.stack = QStackedWidget()

        # Widget'ları oluştur
        self.dashboard_w  = DashboardWidget()
        self.stock_w      = StockViewWidget()
        self.movements_w  = MovementsWidget()
        self.customers_w  = CustomersWidget()
        self.products_w   = ProductsWidget()
        self.locations_w  = LocationsWidget()
        self.reports_w    = ReportsWidget()

        self.stack.addWidget(self.dashboard_w)   # 0
        self.stack.addWidget(self.stock_w)        # 1
        self.stack.addWidget(self.movements_w)    # 2
        self.stack.addWidget(self.customers_w)    # 3
        self.stack.addWidget(self.products_w)     # 4
        self.stack.addWidget(self.locations_w)    # 5
        self.stack.addWidget(self.reports_w)      # 6

        # Hareket kaydedilince diğer ekranları yenile
        self.movements_w.movement_saved.connect(self._on_movement_saved)

        main_layout.addWidget(self.stack, 1)
        self._apply_styles()

    def _on_movement_saved(self):
        """Hareket kaydedildiğinde ilgili ekranları yenile."""
        self.dashboard_w.refresh()
        self.stock_w.load_data()
        self.reports_w.refresh()

    def _build_sidebar(self):
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setObjectName("sidebar")
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        title = QLabel("🏭 WMS")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("sidebarTitle")
        title.setFixedHeight(70)
        layout.addWidget(title)

        self.nav_buttons = []
        menu_items = [
            ("📊  Dashboard",   0),
            ("📦  Stok",        1),
            ("🔄  Hareketler",  2),
            ("👥  Müşteriler",  3),
            ("🛒  Ürünler",     4),
            ("📍  Lokasyonlar", 5),
            ("📈  Raporlar",    6),
        ]

        for label, index in menu_items:
            btn = QPushButton(label)
            btn.setObjectName("navButton")
            btn.setFixedHeight(50)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, i=index: self._navigate(i))
            layout.addWidget(btn)
            self.nav_buttons.append(btn)

        layout.addStretch()

        version = QLabel("v1.0.0")
        version.setAlignment(Qt.AlignCenter)
        version.setObjectName("versionLabel")
        layout.addWidget(version)

        return sidebar

    def _navigate(self, index):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setProperty("active", i == index)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
            #sidebar {
                background-color: #1B3A6B;
            }
            #sidebarTitle {
                color: white;
                font-size: 20px;
                font-weight: bold;
                background-color: #152d54;
                padding: 10px;
            }
            #navButton {
                background-color: transparent;
                color: #a0b4d0;
                border: none;
                text-align: left;
                padding-left: 20px;
                font-size: 14px;
            }
            #navButton:hover {
                background-color: #244f8f;
                color: white;
            }
            #navButton[active=true] {
                background-color: #2563EB;
                color: white;
                font-weight: bold;
                border-left: 4px solid #60a5fa;
            }
            #versionLabel {
                color: #5a7a9f;
                font-size: 11px;
                padding: 10px;
            }
        """)