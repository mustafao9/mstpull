import json
from pathlib import Path
from typing import Dict, Any
from src.utils.logging_config import get_logger

class SettingsManager:
    """Kullanıcı tercihlerini (Pop-up gizleme vb.) JSON olarak saklar ve yönetir."""
    def __init__(self, config_dir: Path):
        self.settings_file = config_dir / "settings.json"
        self.logger = get_logger()
        self.defaults = {
            "show_download_start_popup": True
        }
        self.settings = self.load_settings()

    def load_settings(self) -> Dict[str, Any]:
        if not self.settings_file.exists():
            return self.defaults.copy()
        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                merged = self.defaults.copy()
                merged.update(data)
                return merged
        except Exception as e:
            self.logger.error(f"Ayar dosyası okunamadı: {str(e)}")
            return self.defaults.copy()

    def save_settings(self):
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Ayarlar kaydedilemedi: {str(e)}")

    def get(self, key: str, default=None):
        return self.settings.get(key, default)

    def set(self, key: str, value: Any):
        self.settings[key] = value
        self.save_settings()
