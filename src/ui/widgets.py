from pathlib import Path
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QPushButton, QLineEdit
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices

class LocalizedLineEdit(QLineEdit):
    def __init__(self, i18n_manager, parent=None):
        super().__init__(parent)
        self.i18n = i18n_manager

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        for action in menu.actions():
            text = action.text().replace("&", "")
            if "Undo" in text or "Geri Al" in text:
                action.setText("Geri Al" if self.i18n.current_lang == "tr" else "Undo")
            elif "Redo" in text or "Yinele" in text:
                action.setText("Yinele" if self.i18n.current_lang == "tr" else "Redo")
            elif "Cut" in text or "Kes" in text:
                action.setText("Kes" if self.i18n.current_lang == "tr" else "Cut")
            elif "Copy" in text or "Kopyala" in text:
                action.setText("Kopyala" if self.i18n.current_lang == "tr" else "Copy")
            elif "Paste" in text or "Yapıştır" in text:
                action.setText("Yapıştır" if self.i18n.current_lang == "tr" else "Paste")
            elif "Delete" in text or "Sil" in text:
                action.setText("Sil" if self.i18n.current_lang == "tr" else "Delete")
            elif "Select All" in text or "Tümünü Seç" in text:
                action.setText("Tümünü Seç" if self.i18n.current_lang == "tr" else "Select All")
        menu.exec(event.globalPos())

class DownloadItemWidget(QFrame):
    """Kendi indirme türünü (MP3/Video) ve yolunu hafızasında tutan dinamik kart."""
    def __init__(self, task_id: str, url: str, i18n_manager, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.url = url
        self.i18n = i18n_manager
        self.saved_target_dir = None
        self.is_completed = False
        self.is_audio_mode = False  # İndirme türü hafızası
        self.raw_title = url[:45]
        self.raw_duration = ""

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            DownloadItemWidget {
                background-color: #1f2335;
                border: 1px solid #414868;
                border-radius: 6px;
                margin-bottom: 6px;
                padding: 8px;
            }
        """)

        layout = QVBoxLayout(self)

        self.title_label = QLabel(f"📹 {self.raw_title}...")
        self.title_label.setStyleSheet("font-weight: bold; color: #c0caf5;")
        layout.addWidget(self.title_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #414868;
                border-radius: 4px;
                text-align: center;
                color: #c0caf5;
                background-color: #1a1b26;
            }
            QProgressBar::chunk {
                background-color: #7aa2f7;
            }
        """)
        layout.addWidget(self.progress_bar)

        self.info_label = QLabel(self.i18n.tr("status_ready"))
        self.info_label.setStyleSheet("color: #787c99; font-size: 11px;")
        layout.addWidget(self.info_label)

        self.btn_layout = QHBoxLayout()
        
        self.btn_dl_video = QPushButton("🎬 Video İndir")
        self.btn_dl_video.setStyleSheet("background-color: #7aa2f7; color: #15161e; font-weight: bold;")
        
        self.btn_dl_audio = QPushButton("🎵 Ses (MP3) İndir")
        self.btn_dl_audio.setStyleSheet("background-color: #bb9af7; color: #15161e; font-weight: bold;")

        self.btn_switch_mode = QPushButton()
        self.btn_switch_mode.setStyleSheet("background-color: #9ece6a; color: #15161e; font-weight: bold;")
        self.btn_switch_mode.setVisible(False)

        self.cancel_btn = QPushButton(self.i18n.tr("cancel"))
        
        self.folder_btn = QPushButton(self.i18n.tr("open_folder"))
        self.folder_btn.setVisible(False)
        self.folder_btn.clicked.connect(self.open_own_folder)

        self.donate_btn = QPushButton(self.i18n.tr("buy_me_coffee"))
        self.donate_btn.setStyleSheet("background-color: #e0af68; color: #15161e; font-weight: bold;")
        self.donate_btn.setVisible(False)
        self.donate_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://buymeacoffee.com/mustafasatilmis")))

        self.btn_layout.addWidget(self.btn_dl_video)
        self.btn_layout.addWidget(self.btn_dl_audio)
        self.btn_layout.addWidget(self.btn_switch_mode)
        self.btn_layout.addWidget(self.cancel_btn)
        self.btn_layout.addWidget(self.folder_btn)
        self.btn_layout.addWidget(self.donate_btn)

        layout.addLayout(self.btn_layout)

    def set_media_info(self, title: str, duration: str):
        self.raw_title = title
        self.raw_duration = duration
        self.update_title_display()

    def update_title_display(self):
        dur = f" [{self.raw_duration}]" if self.raw_duration else ""
        if self.is_completed:
            tag = "🎵 [MP3]" if self.is_audio_mode else "🎬 [VIDEO]"
        else:
            tag = "📹"
        self.title_label.setText(f"{tag} {self.raw_title}{dur}")

    def start_download_ui(self, is_audio: bool, target_dir: Path):
        self.is_audio_mode = is_audio
        self.saved_target_dir = target_dir
        self.btn_dl_video.setVisible(False)
        self.btn_dl_audio.setVisible(False)
        self.update_title_display()
        
        mode_str = "MP3" if is_audio else "VIDEO"
        self.info_label.setText(f"🚀 {mode_str} İndirme Başlatılıyor...")

    def update_progress(self, percent: float, speed: str, eta: str):
        self.progress_bar.setValue(int(percent))
        self.info_label.setText(f"%{percent:.1f} | Hız: {speed} | Kalan: {eta}")

    def mark_as_completed(self):
        self.is_completed = True
        self.progress_bar.setValue(100)
        self.info_label.setText(f"✅ {self.i18n.tr('status_ready')}")
        self.cancel_btn.setVisible(False)
        self.folder_btn.setVisible(True)
        self.donate_btn.setVisible(True)
        self.update_title_display()

        # Mantıklı Buton Metni: Ses indiyse Video teklif et, Video indiyse Ses teklif et!
        if self.is_audio_mode:
            self.btn_switch_mode.setText("🎬 Şimdi de Video Olarak İndir")
        else:
            self.btn_switch_mode.setText("🎵 Şimdi de MP3 Olarak İndir")
        
        self.btn_switch_mode.setVisible(True)

    def open_own_folder(self):
        if self.saved_target_dir and self.saved_target_dir.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.saved_target_dir)))

    def retranslate_ui(self):
        self.cancel_btn.setText(self.i18n.tr("cancel"))
        self.folder_btn.setText(self.i18n.tr("open_folder"))
        self.donate_btn.setText(self.i18n.tr("buy_me_coffee"))
