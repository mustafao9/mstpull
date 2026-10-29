import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from src.config.paths import AppPaths
from src.utils.logging_config import setup_logging, get_logger
from src.utils.i18n_manager import I18nManager
from src.bootstrapper import Bootstrapper
from src.ui.main_window import MainWindow

def main():
    paths = AppPaths()
    logger = setup_logging(str(paths.logs_dir))
    logger.info("MstPull uygulaması başlatılıyor...")

    app = QApplication(sys.argv)

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

    # 2. i18n Dil Yöneticisi (Varsayılan Türkçe)
    i18n = I18nManager(paths.locales_dir, default_lang="tr")

    # 3. Ana Pencereyi Oluştur ve Göster
    window = MainWindow(paths, i18n)
    window.show()

    logger.info("MstPull ana penceresi başarıyla açıldı.")
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
