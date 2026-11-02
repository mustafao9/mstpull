from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from PyQt6.QtWidgets import QApplication

class ClipboardMonitor(QObject):
    """Panoya kopyalanan geçerli video bağlantılarını arka planda izleyen servis."""
    url_detected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.last_url = ""
        self.timer = QTimer(self)
        self.timer.setInterval(1000) # Her 1 saniyede panoyu kontrol et
        self.timer.timeout.connect(self.check_clipboard)
        self.is_enabled = True

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()

    def check_clipboard(self):
        if not self.is_enabled:
            return

        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()

        if text and text != self.last_url:
            if self.is_valid_url(text):
                self.last_url = text
                self.url_detected.emit(text)

    def is_valid_url(self, text: str) -> bool:
        valid_domains = ["youtube.com/", "youtu.be/", "vimeo.com/", "dailymotion.com/"]
        return any(domain in text.lower() for domain in valid_domains)
