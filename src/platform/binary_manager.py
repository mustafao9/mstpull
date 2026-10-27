import os
import sys
import stat
import urllib.request
import subprocess
from pathlib import Path
from typing import Tuple, Optional
from src.config.paths import AppPaths
from src.utils.logging_config import get_logger

class BinaryManager:
    """yt-dlp ve FFmpeg bağımsız ikililerinin varlığını, çalıştırılabilirliğini ve güncellenmesini yönetir."""

    YTDLP_OFFICIAL_URL_LINUX = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp"
    YTDLP_OFFICIAL_URL_WIN = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"

    def __init__(self, paths: AppPaths):
        self.paths = paths
        self.logger = get_logger()
        self.system = paths.system

    def ensure_executable_permission(self, file_path: Path) -> None:
        """Linux ve POSIX sistemlerde kullanıcı alanındaki dosyaya çalıştırma izni verir."""
        if self.system != "windows" and file_path.exists():
            # Yalnızca yazma iznimiz olan kullanıcı/proje dizinlerindeki dosyalara chmod uygula
            try:
                if os.access(file_path, os.W_OK):
                    current_permissions = file_path.stat().st_mode
                    file_path.chmod(current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            except PermissionError as e:
                self.logger.debug(f"Chmod izin atlama (sistem ikilisi): {file_path} - {str(e)}")

    def check_yt_dlp(self) -> Tuple[bool, str]:
        """yt-dlp ikilisinin varlığını ve çalışabilirliğini doğrular."""
        binary_path = self.paths.get_yt_dlp_path()
        if not binary_path.exists():
            return False, "yt-dlp bulunamadı."

        self.ensure_executable_permission(binary_path)

        try:
            result = subprocess.run(
                [str(binary_path), "--version"],
                capture_output=True,
                text=True,
                check=True,
                timeout=5
            )
            version_str = result.stdout.strip()
            self.logger.info(f"yt-dlp doğrulandı. Sürüm: {version_str}")
            return True, version_str
        except Exception as e:
            self.logger.error(f"yt-dlp çalıştırılamadı: {str(e)}")
            return False, f"Çalıştırma hatası: {str(e)}"

    def check_ffmpeg(self) -> Tuple[bool, str]:
        """FFmpeg ikilisinin varlığını ve çalışabilirliğini doğrular."""
        binary_path = self.paths.get_ffmpeg_path()
        
        # Sistem yolunda arama yedeği (which ffmpeg)
        if not binary_path.exists():
            import shutil
            sys_ffmpeg = shutil.which("ffmpeg")
            if sys_ffmpeg:
                binary_path = Path(sys_ffmpeg)

        if not binary_path.exists():
            return False, "ffmpeg bulunamadı."

        self.ensure_executable_permission(binary_path)

        try:
            result = subprocess.run(
                [str(binary_path), "-version"],
                capture_output=True,
                text=True,
                check=True,
                timeout=5
            )
            first_line = result.stdout.splitlines()[0] if result.stdout else "FFmpeg OK"
            self.logger.info(f"FFmpeg doğrulandı: {first_line}")
            return True, first_line
        except Exception as e:
            self.logger.error(f"FFmpeg çalıştırılamadı: {str(e)}")
            return False, f"Çalıştırma hatası: {str(e)}"

    def download_yt_dlp(self, progress_callback=None) -> bool:
        """yt-dlp bağımsız ikilisini resmi kaynaktan atomik olarak indirir."""
        target_name = "yt-dlp.exe" if self.system == "windows" else "yt-dlp"
        target_path = self.paths.user_bin_dir / target_name
        temp_path = self.paths.user_bin_dir / f"{target_name}.tmp"

        download_url = self.YTDLP_OFFICIAL_URL_WIN if self.system == "windows" else self.YTDLP_OFFICIAL_URL_LINUX
        self.logger.info(f"yt-dlp indiriliyor: {download_url}")

        try:
            def _reporthook(blocknum, blocksize, totalsize):
                if progress_callback and totalsize > 0:
                    percent = int((blocknum * blocksize / totalsize) * 100)
                    progress_callback(min(percent, 100))

            urllib.request.urlretrieve(download_url, temp_path, _reporthook if progress_callback else None)
            
            self.ensure_executable_permission(temp_path)
            if target_path.exists():
                target_path.unlink()
            temp_path.rename(target_path)
            
            self.logger.info(f"yt-dlp başarıyla indirildi ve kaydedildi: {target_path}")
            return True
        except Exception as e:
            self.logger.error(f"yt-dlp indirme hatası: {str(e)}")
            if temp_path.exists():
                temp_path.unlink()
            return False
