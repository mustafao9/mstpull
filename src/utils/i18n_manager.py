import json
import sys
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal
from src.utils.logging_config import get_logger

TR_MAP = {
    "app_name": "MstPull - Video & Müzik İndirici",
    "url_placeholder": "Video veya Oynatma Listesi URL'si girin...",
    "paste_btn": "📋 Panodan Yapıştır",
    "add_queue_btn": "➕ Kuyruğa Ekle",
    "history_btn": "📜 İndirme Geçmişi",
    "chk_playlist": "Tüm Oynatma Listesini İndir",
    "video_quality": "Video Kalitesi",
    "audio_quality": "MP3 Kalitesi",
    "qual_best": "En Yüksek Kalite",
    "qual_lowest": "En Düşük Kalite",
    "target_folder": "Hedef Klasör",
    "browse_btn": "📁 Gözat",
    "queue_title": "İndirme Kuyruğu",
    "developer_credit": "Geliştirici: Mustafa Satılmış",
    "donate_btn": "☕ Geliştiriciye Destek Ol",
    "status_ready": "Sistem Hazır"
}

class I18nManager(QObject):
    language_changed = pyqtSignal()

    def __init__(self, locales_dir: Path = None, current_lang: str = "tr", default_lang: str = "tr"):
        super().__init__()
        self.current_lang = default_lang if default_lang else current_lang
        self.logger = get_logger()
        self.translations = dict(TR_MAP)
        
        possible_paths = [
            Path("/usr/share/mstpull/locales"),
            Path("/usr/share/mstpull/assets/locales"),
            Path(__file__).resolve().parent.parent.parent / "locales",
            Path(__file__).resolve().parent.parent.parent / "assets" / "locales"
        ]
        
        self.locales_dir = None
        for p in possible_paths:
            if p.exists():
                self.locales_dir = p
                break

        self.load_translations()

    def load_translations(self):
        if self.locales_dir and self.locales_dir.exists():
            file_path = self.locales_dir / f"{self.current_lang}.json"
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self.translations.update(data)
                except Exception as e:
                    self.logger.error(f"Dil dosyası yüklenemedi: {e}")

    def set_language(self, lang_code: str):
        if self.current_lang != lang_code:
            self.current_lang = lang_code
            self.translations = dict(TR_MAP)
            self.load_translations()
            self.language_changed.emit()

    def tr(self, key: str) -> str:
        return self.translations.get(key, TR_MAP.get(key, key))
