import sys
import os
import platform
import subprocess
from pathlib import Path
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMessageBox
from src.config.paths import AppPaths
from src.utils.logging_config import setup_logging, get_logger
from src.utils.i18n_manager import I18nManager
from src.bootstrapper import Bootstrapper
from src.ui.main_window import MainWindow

def setup_windows_app_id():
    """Windows görev çubuğunda uygulamanın kendi ikonunun doğru görünmesini sağlar."""
    if platform.system() == "Windows":
        try:
            import ctypes
            myappid = 'mustafao9.mstpull.downloader.1.1.4'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

def get_icon_path():
    """PyInstaller ve yerel geliştirme ortamıyla %100 uyumlu ikon yolu döndürür."""
    if hasattr(sys, '_MEIPASS'):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent

    ico = base_path / "icon.ico"
    png = base_path / "icon.png"

    if ico.exists():
        return str(ico)
    elif png.exists():
        return str(png)
    return None

def main():
    # 0. Windows AppUserModelID ayarını etkinleştir
    setup_windows_app_id()

    paths = AppPaths()
    logger = setup_logging(str(paths.logs_dir))
    logger.info("MstPull uygulaması başlatılıyor...")

    app = QApplication(sys.argv)

    # Uygulama genel ikonunu güvenli yoldan yükleme
    icon_path = get_icon_path()
    if icon_path and os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # 1. Bootstrapper Bağımlılık Kontrolü
    bootstrapper = Bootstrapper(paths)
    if not bootstrapper.run_checks():
        logger.critical("Bağımlılık kontrolleri başarısız oldu. Uygulama kapatılıyor.")
        QMessageBox.critical(
            None,
            "MstPull - Hata",
            "Gerekli medya motorları (yt-dlp/FFmpeg) hazırlanamadı. Lütfen internet bağlantınızı kontrol edip tekrar deneyin."
        )
        sys.exit(1)

    # 2. i18n Dil Yöneticisi
    i18n = I18nManager(paths.locales_dir, default_lang="tr")

    # 3. Ana Pencereyi Oluştur ve Göster
    window = MainWindow(paths, i18n)
    window.show()

    logger.info("MstPull ana penceresi başarıyla açıldı.")
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
