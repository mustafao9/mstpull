import os
import sys
import platform
from pathlib import Path

class AppPaths:
    """Çapraz platform dosya ve dizin yollarını merkezi olarak yönetir."""

    def __init__(self, app_name: str = "mstpull"):
        self.app_name = app_name
        self.system = platform.system().lower()
        
        self.project_root = Path(__file__).resolve().parent.parent.parent
        
        if self.system == "windows":
            appdata = os.getenv("APPDATA", os.path.expanduser("~"))
            self.user_data_dir = Path(appdata) / self.app_name
            base_download = Path(os.path.expanduser("~")) / "Downloads"
        else:
            xdg_data = os.getenv("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
            self.user_data_dir = Path(xdg_data) / self.app_name
            
            xdg_download = os.getenv("XDG_DOWNLOAD_DIR")
            if xdg_download:
                base_download = Path(xdg_download)
            else:
                base_download = Path(os.path.expanduser("~")) / "İndirilenler"
                if not base_download.exists():
                    base_download = Path(os.path.expanduser("~")) / "Downloads"

        # Ana İndirme Klasörü: ~/Downloads/mstpull-downloads
        self.default_download_dir = base_download / "mstpull-downloads"
        self.mp3_download_dir = self.default_download_dir / "mp3"
        self.video_download_dir = self.default_download_dir / "video"

        self.config_dir = self.user_data_dir / "config"
        self.logs_dir = self.user_data_dir / "logs"
        self.cache_dir = self.user_data_dir / "cache"
        self.history_dir = self.user_data_dir / "history"
        
        self.platform_bin_dir = self.project_root / "bin" / ("windows" if self.system == "windows" else "linux")
        self.user_bin_dir = self.user_data_dir / "bin"

        self.assets_dir = self.project_root / "assets"
        self.locales_dir = self.project_root / "locales"

        self.ensure_directories()

    def ensure_directories(self) -> None:
        for directory in [
            self.user_data_dir, self.config_dir, self.logs_dir, 
            self.cache_dir, self.history_dir, self.user_bin_dir, 
            self.platform_bin_dir, self.default_download_dir,
            self.mp3_download_dir, self.video_download_dir
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    def get_yt_dlp_path(self) -> Path:
        binary_name = "yt-dlp.exe" if self.system == "windows" else "yt-dlp"
        user_bin = self.user_bin_dir / binary_name
        if user_bin.exists():
            return user_bin
        return self.platform_bin_dir / binary_name

    def get_ffmpeg_path(self) -> Path:
        binary_name = "ffmpeg.exe" if self.system == "windows" else "ffmpeg"
        user_bin = self.user_bin_dir / binary_name
        if user_bin.exists():
            return user_bin
        return self.platform_bin_dir / binary_name
