from models.base import create_tables
from utils.scheduler import start_scheduler

# SEED VERİ OLUŞTURMAK İÇİN:
from utils.scheduler import generate_weekly_report, generate_monthly_report
generate_weekly_report()
generate_monthly_report()

if __name__ == "__main__":
    create_tables()
    start_scheduler()

    from ui.main_window import MainWindow
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())