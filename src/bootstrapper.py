import sys
from typing import Tuple
from src.config.paths import AppPaths
from src.platform.binary_manager import BinaryManager
from src.utils.logging_config import get_logger

class Bootstrapper:
    """Uygulama açılışında bağımlılıkları doğrulayan ve eksik motorları otomatik kuran ön yükleyici."""

    def __init__(self, paths: AppPaths):
        self.paths = paths
        self.logger = get_logger()
        self.binary_manager = BinaryManager(paths)

    def run_checks(self, status_callback=None) -> bool:
        """Tüm bağımlılıkları kontrol eder, eksik olanları indirir."""
        self.logger.info("Bootstrapper kontrolleri başlatılıyor...")

        # 1. FFmpeg Kontrolü
        if status_callback:
            status_callback("FFmpeg kontrol ediliyor...")
        ff_ok, ff_msg = self.binary_manager.check_ffmpeg()
        if not ff_ok:
            self.logger.warning(f"FFmpeg uyarısı: {ff_msg}")
            # İleride ffmpeg indirme yedeği eklenebilir, şimdilik logluyoruz

        # 2. yt-dlp Kontrolü ve Otomatik İndirme
        if status_callback:
            status_callback("yt-dlp kontrol ediliyor...")
        yt_ok, yt_msg = self.binary_manager.check_yt_dlp()

        if not yt_ok:
            self.logger.info("yt-dlp eksik, indirme işlemi başlatılıyor...")
            if status_callback:
                status_callback("yt-dlp indiriliyor, lütfen bekleyin...")
            
            download_success = self.binary_manager.download_yt_dlp()
            if not download_success:
                self.logger.error("yt-dlp otomatik indirilemedi!")
                return False

            # İndirme sonrası tekrar doğrula
            yt_ok, yt_msg = self.binary_manager.check_yt_dlp()
            if not yt_ok:
                self.logger.error(f"yt-dlp indirildi ancak doğrulanamadı: {yt_msg}")
                return False

        self.logger.info(f"Bootstrapper başarıyla tamamlandı. yt-dlp sürümü: {yt_msg}")
        return True
