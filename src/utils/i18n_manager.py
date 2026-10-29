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
    "history_title": "İndirme Arşivi ve Geçmişi",
    "hist_date": "Tarih",
    "hist_url": "URL",
    "hist_mode": "Tür",
    "hist_path": "Kaydedilen Konum",
    "close": "Kapat",
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
    "status_ready": "Sistem Hazır",
    "disclaimer_text": "⚠️ YASAL UYARI: Bu programla telif hakkı olan içerikler indirilemez ve bu amaçla kullanılamaz. Tüm kullanım sorumluluğu son kullanıcıya aittir.",
    "open_folder": "Klasörü Aç",
    "buy_me_coffee": "Geliştiriciye Destek Ol",
    "confirm_title": "Telif Hakkı ve Sorumluluk Onayı",
    "confirm_msg": "İndirmek üzere olduğunuz içeriğin telif hakkı ihlali içermediğini ve tüm yasal sorumluluğun tarafınıza ait olduğunu kabul ediyor musunuz?",
    "cancel": "❌ İptal",
    "pause": "⏸ Duraklat",
    "resume": "▶ Devam Et",
    "retry": "🔄 Yeniden Dene",
    "mode_selection": "Mod Seçimi",
    "mode_video": "Video (MP4/MKV)",
    "mode_audio": "Sadece Ses (MP3)",
    "start_all": "▶ Tümünü Başlat",
    "stop_all": "⏸ Tümünü Duraklat",
    "github_btn": "💻 GitHub",
    "tray_show_hide": "MstPull'u Göster / Gizle",
    "tray_quit": "Çıkış",
    "tray_minimized": "Uygulama sistem tepsisine küçüldü.",
    "tray_new_link_title": "📋 Yeni Bağlantı Algılandı!",
    "tray_new_link_body": "Panodaki URL MstPull'a aktarıldı: {url}",
    "tray_download_done_title": "✅ İndirme Tamamlandı!",
    "tray_download_done_body": "Dosyanız indirildi: {title}",
    "clipboard_detected": "📋 Panodan yeni bağlantı algılandı: {url}",
    "analyzing_playlist": "🔍 Oynatma Listesi Analiz Ediliyor...",
    "playlist_empty": "Oynatma listesinde video bulunamadı.",
    "playlist_error": "Oynatma listesi bilgileri alınamadı.\n\n{err}",
    "info_error": "⚠️ Bilgi alınamadı: {err}",
    "cancelled": "❌ İptal Edildi",
    "background_question": "Arka planda çalışmaya devam etsin mi?",
    "concurrent_label": "⚡ Eşzamanlı İndirme:",
    "concurrent_1": "1 Dosya",
    "concurrent_2": "2 Dosya (Varsayılan)",
    "concurrent_3": "3 Dosya",
    "concurrent_5": "5 Dosya",
    "rate_limit_label": "🚀 Hız Limiti:",
    "rate_unlimited": "Sınırsız",
    "chk_clipboard": "📋 Panodan Otomatik Algıla",
    "playlist_error_status": "❌ Oynatma listesi analiz edilemedi.",
    "unknown": "Bilinmeyen",
}

class I18nManager(QObject):
    language_changed = pyqtSignal()

    def __init__(self, locales_dir: Path = None, current_lang: str = "tr", default_lang: str = "tr"):
        super().__init__()
        self.current_lang = default_lang if default_lang else current_lang
        self.logger = get_logger()
        self.translations = dict(TR_MAP)

        # Önce parametre olarak gelen yolu kullan
        if locales_dir and Path(locales_dir).exists():
            self.locales_dir = Path(locales_dir)
        else:
            # Fallback: sırayla dene
            possible_paths = [
                Path(__file__).resolve().parent.parent.parent / "locales",
                Path(__file__).resolve().parent.parent.parent / "assets" / "locales",
                Path("/usr/share/mstpull/locales"),
                Path("/usr/share/mstpull/assets/locales"),
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
