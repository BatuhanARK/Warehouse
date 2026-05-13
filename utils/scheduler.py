import threading
import time
import os
from datetime import date, timedelta
from services.report_service import ReportService


def get_reports_dir():
    """Raporlar ana klasörünü oluştur ve döndür."""
    base = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
    haftalik = os.path.join(base, "haftalik")
    aylik    = os.path.join(base, "aylik")
    os.makedirs(haftalik, exist_ok=True)
    os.makedirs(aylik,    exist_ok=True)
    return haftalik, aylik


def generate_weekly_report():
    """Bir önceki haftanın (Pazartesi-Pazar) raporunu oluştur."""
    try:
        haftalik_dir, _ = get_reports_dir()
        service         = ReportService()

        bugun      = date.today()
        # Bir önceki haftanın Pazartesi ve Pazar'ı
        gecen_pazartesi = bugun - timedelta(days=bugun.weekday() + 7)
        gecen_pazar     = gecen_pazartesi + timedelta(days=6)

        movements = service.get_movement_report(
            start_date=gecen_pazartesi,
            end_date=gecen_pazar
        )

        if movements:
            dosya_adi = f"haftalik_{gecen_pazartesi.strftime('%Y%m%d')}_{gecen_pazar.strftime('%Y%m%d')}.xlsx"
            dosya_yol = os.path.join(haftalik_dir, dosya_adi)
            service.export_movements_excel(movements, dosya_yol)
            print(f"[Scheduler] Haftalık rapor oluşturuldu: {dosya_yol}")
        else:
            print(f"[Scheduler] Haftalık rapor: {gecen_pazartesi} - {gecen_pazar} arasında hareket yok.")
    except Exception as e:
        print(f"[Scheduler] Haftalık rapor hatası: {e}")


def generate_monthly_report():
    """Bir önceki ayın raporunu oluştur."""
    try:
        _, aylik_dir = get_reports_dir()
        service      = ReportService()

        bugun       = date.today()
        # Bir önceki ayın ilk ve son günü
        ay_basi     = date(bugun.year, bugun.month, 1)
        onceki_ay_son = ay_basi - timedelta(days=1)
        onceki_ay_bas = date(onceki_ay_son.year, onceki_ay_son.month, 1)

        movements = service.get_movement_report(
            start_date=onceki_ay_bas,
            end_date=onceki_ay_son
        )
        stocks = service.get_stock_report()

        ay_label = onceki_ay_bas.strftime("%Y_%m")

        # Hareket raporu
        if movements:
            dosya_adi = f"aylik_hareketler_{ay_label}.xlsx"
            dosya_yol = os.path.join(aylik_dir, dosya_adi)
            service.export_movements_excel(movements, dosya_yol)
            print(f"[Scheduler] Aylık hareket raporu oluşturuldu: {dosya_yol}")

        # Stok raporu
        if stocks:
            dosya_adi = f"aylik_stok_{ay_label}.xlsx"
            dosya_yol = os.path.join(aylik_dir, dosya_adi)
            service.export_stock_excel(stocks, dosya_yol)
            print(f"[Scheduler] Aylık stok raporu oluşturuldu: {dosya_yol}")

    except Exception as e:
        print(f"[Scheduler] Aylık rapor hatası: {e}")


def _check_and_run():
    """Her dakika kontrol et, koşul sağlanırsa raporu oluştur."""
    son_haftalik = None
    son_aylik    = None

    while True:
        try:
            bugun = date.today()

            # Pazartesi günü ve daha önce oluşturulmadıysa haftalık rapor
            if bugun.weekday() == 0 and son_haftalik != bugun:
                generate_weekly_report()
                son_haftalik = bugun

            # Ayın 1'i ve daha önce oluşturulmadıysa aylık rapor
            if bugun.day == 1 and son_aylik != bugun:
                generate_monthly_report()
                son_aylik = bugun

        except Exception as e:
            print(f"[Scheduler] Kontrol hatası: {e}")

        # 1 saat bekle
        time.sleep(3600)


def start_scheduler():
    """Scheduler'ı arka planda başlat."""
    t = threading.Thread(target=_check_and_run, daemon=True)
    t.start()
    print("[Scheduler] Başlatıldı — Pazartesi günleri haftalık, ayın 1'i aylık rapor oluşturulacak.")