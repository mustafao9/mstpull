import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from src.utils.logging_config import get_logger

class HistoryService:
    """Tamamlanan ve indirilen tüm içeriklerin geçmişini JSON olarak saklar."""
    def __init__(self, history_dir: Path):
        self.history_file = history_dir / "history.json"
        self.logger = get_logger()
        self.history: List[Dict[str, Any]] = self.load_history()

    def load_history(self) -> List[Dict[str, Any]]:
        if not self.history_file.exists():
            return []
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Geçmiş dosyası okunamadı: {str(e)}")
            return []

    def add_entry(self, url: str, mode: str, quality: str, target_path: str):
        entry = {
            "url": url,
            "mode": mode,
            "quality": quality,
            "target_path": target_path,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history.insert(0, entry)
        self.save_history()

    def save_history(self):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Geçmiş kaydedilemedi: {str(e)}")

    def get_history(self) -> List[Dict[str, Any]]:
        return self.history
