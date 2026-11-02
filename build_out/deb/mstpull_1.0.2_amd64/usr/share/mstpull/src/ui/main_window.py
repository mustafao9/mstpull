import sys
import uuid
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QRadioButton, QComboBox, QLabel, QScrollArea,
    QFrame, QFileDialog, QStatusBar, QApplication, QCheckBox, QMessageBox,
    QSystemTrayIcon, QMenu
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QIcon, QAction
from src.ui.widgets import DownloadItemWidget, LocalizedLineEdit
from src.core.downloader import DownloadWorker, MediaInfoFetcher, PlaylistFetcher
from src.core.queue_manager import QueueManager
from src.services.history_service import HistoryService
from src.services.clipboard_monitor import ClipboardMonitor
from src.config.settings_manager import SettingsManager
from src.ui.dialogs import HistoryDialog, PlaylistDialog

class MainWindow(QMainWindow):
    def __init__(self, paths, i18n_manager):
        super().__init__()
        self.paths = paths
        self.i18n = i18n_manager
        self.settings_manager = SettingsManager(self.paths.config_dir)
        self.queue_manager = QueueManager(max_concurrent=2)
        self.history_service = HistoryService(self.paths.history_dir)
        
        self.active_widgets = {}
        self.completed_widgets = {}
        self.fetchers = {}

        self.i18n.language_changed.connect(self.retranslate_ui)
        self.queue_manager.task_progress.connect(self.on_task_progress)
        self.queue_manager.task_finished.connect(self.on_task_finished)

        self.resize(1050, 680)
        icon_path = self.paths.assets_dir / "icons" / "app.png"
        if not icon_path.exists():
            icon_path = Path("/usr/share/mstpull/assets/icons/app.png")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.apply_theme()
        self.init_ui()
        self.init_tray_icon()
        
        self.clipboard_monitor = ClipboardMonitor(self)
        self.clipboard_monitor.url_detected.connect(self.on_clipboard_url_detected)
        self.clipboard_monitor.start()

        self.retranslate_ui()
        self.status_bar.showMessage(self.i18n.tr("status_ready"))

    def apply_theme(self):
        qss_path = self.paths.assets_dir / "styles" / "dark.qss"
        if qss_path.exists():
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        master_layout = QVBoxLayout(main_widget)
        master_layout.setContentsMargins(14, 14, 14, 14)
        master_layout.setSpacing(12)

        # 1. ÜST PANEL
        top_box = QFrame()
        top_layout = QHBoxLayout(top_box)

        self.url_input = LocalizedLineEdit(self.i18n)

        self.paste_btn = QPushButton(self.i18n.tr("paste_btn"))
        self.paste_btn.clicked.connect(self.paste_from_clipboard)

        self.add_queue_btn = QPushButton(self.i18n.tr("add_queue_btn"))
        self.add_queue_btn.setStyleSheet("background-color: #7aa2f7; color: #15161e; font-weight: bold; border: none;")
        self.add_queue_btn.clicked.connect(self.add_to_queue)

        self.history_btn = QPushButton(self.i18n.tr("history_btn"))
        self.history_btn.clicked.connect(self.open_history_dialog)

        self.lang_combo = QComboBox()
        self.lang_combo.setMinimumWidth(110)
        self.lang_combo.addItem("🇹🇷 TR", "tr")
        self.lang_combo.addItem("🇬🇧 EN", "en")
        self.lang_combo.currentIndexChanged.connect(self.change_language)

        top_layout.addWidget(self.url_input, stretch=4)
        top_layout.addWidget(self.paste_btn)
        top_layout.addWidget(self.add_queue_btn)
        top_layout.addWidget(self.history_btn)
        top_layout.addWidget(self.lang_combo)
        master_layout.addWidget(top_box)

        # 2. ORTA GOVDE
        body_layout = QHBoxLayout()

        # SOL PANEL: AYARLAR
        left_panel = QFrame()
        left_layout = QVBoxLayout(left_panel)

        self.lbl_video_qual = QLabel(self.i18n.tr("video_quality"))
        self.lbl_video_qual.setStyleSheet("font-weight: bold; color: #7aa2f7; font-size: 13px;")
        self.combo_video_qual = QComboBox()
        self.combo_video_qual.addItems([
            self.i18n.tr("qual_best"), "1080p (Full HD)", "720p (HD)", "480p", self.i18n.tr("qual_lowest")
        ])
        left_layout.addWidget(self.lbl_video_qual)
        left_layout.addWidget(self.combo_video_qual)

        left_layout.addSpacing(6)
        self.lbl_audio_qual = QLabel(self.i18n.tr("audio_quality"))
        self.lbl_audio_qual.setStyleSheet("font-weight: bold; color: #7aa2f7; font-size: 13px;")
        self.combo_audio_qual = QComboBox()
        self.combo_audio_qual.addItems(["320 kbps", "256 kbps", "192 kbps", "128 kbps"])
        left_layout.addWidget(self.lbl_audio_qual)
        left_layout.addWidget(self.combo_audio_qual)

        left_layout.addSpacing(6)
        self.lbl_concurrent = QLabel(self.i18n.tr("concurrent_label"))
        self.lbl_concurrent.setStyleSheet("font-weight: bold; color: #7aa2f7; font-size: 13px;")
        self.combo_concurrent = QComboBox()
        self.combo_concurrent.addItems([
            self.i18n.tr("concurrent_1"),
            self.i18n.tr("concurrent_2"),
            self.i18n.tr("concurrent_3"),
            self.i18n.tr("concurrent_5"),
        ])
        self.combo_concurrent.setCurrentIndex(1)
        self.combo_concurrent.currentIndexChanged.connect(self.on_concurrent_changed)
        left_layout.addWidget(self.lbl_concurrent)
        left_layout.addWidget(self.combo_concurrent)

        left_layout.addSpacing(6)
        self.lbl_rate_limit = QLabel(self.i18n.tr("rate_limit_label"))
        self.lbl_rate_limit.setStyleSheet("font-weight: bold; color: #7aa2f7; font-size: 13px;")
        self.combo_rate_limit = QComboBox()
        self.combo_rate_limit.addItem(self.i18n.tr("rate_unlimited"), "Unlimited")
        self.combo_rate_limit.addItem("1 MB/s", "1M")
        self.combo_rate_limit.addItem("2 MB/s", "2M")
        self.combo_rate_limit.addItem("5 MB/s", "5M")
        self.combo_rate_limit.addItem("10 MB/s", "10M")
        left_layout.addWidget(self.lbl_rate_limit)
        left_layout.addWidget(self.combo_rate_limit)

        self.chk_clipboard = QCheckBox(self.i18n.tr("chk_clipboard"))
        self.chk_clipboard.setChecked(True)
        self.chk_clipboard.setStyleSheet("color: #7aa2f7; font-weight: 500; margin-top: 6px;")
        self.chk_clipboard.toggled.connect(self.toggle_clipboard_monitor)
        left_layout.addWidget(self.chk_clipboard)

        self.chk_playlist = QCheckBox(self.i18n.tr("chk_playlist"))
        self.chk_playlist.setStyleSheet("color: #e0af68; font-weight: 500; margin-top: 4px;")
        left_layout.addWidget(self.chk_playlist)

        left_layout.addSpacing(6)
        self.lbl_target_folder = QLabel(self.i18n.tr("target_folder"))
        self.lbl_target_folder.setStyleSheet("font-weight: bold; color: #7aa2f7; font-size: 13px;")
        folder_layout = QHBoxLayout()
        self.folder_input = LocalizedLineEdit(self.i18n)
        self.folder_input.setText(str(self.paths.default_download_dir))
        self.browse_btn = QPushButton(self.i18n.tr("browse_btn"))
        self.browse_btn.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(self.browse_btn)
        left_layout.addWidget(self.lbl_target_folder)
        left_layout.addLayout(folder_layout)

        left_layout.addStretch()
        body_layout.addWidget(left_panel, stretch=1)

        # SAĞ PANEL: İNDİRME LİSTESİ
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)

        queue_header_layout = QHBoxLayout()
        self.lbl_queue_title = QLabel(self.i18n.tr("queue_title"))
        self.lbl_queue_title.setStyleSheet("font-weight: bold; color: #7aa2f7; font-size: 14px;")
        queue_header_layout.addWidget(self.lbl_queue_title)
        right_layout.addLayout(queue_header_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("scroll_content")
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.scroll_content)

        right_layout.addWidget(self.scroll_area)
        body_layout.addWidget(right_panel, stretch=2)

        master_layout.addLayout(body_layout)

        # 15pt Sade Yasal Uyarı Metni
        disc_txt = self.i18n.tr("disclaimer_text")
        if disc_txt == "disclaimer_text" or not disc_txt:
            disc_txt = "⚠️ YASAL UYARI: Bu programla telif hakkı olan içerikler indirilemez ve bu amaçla kullanılamaz. Tüm kullanım sorumluluğu son kullanıcıya aittir."
        self.disclaimer_label = QLabel(disc_txt)
        self.disclaimer_label.setStyleSheet("color: #f7768e; font-size: 15px; font-weight: bold; margin-top: 6px; margin-bottom: 4px; background: transparent;")
        self.disclaimer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.disclaimer_label.setWordWrap(True)
        master_layout.addWidget(self.disclaimer_label)

        # 3. ALT DURUM ÇUBUĞU
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.dev_label = QLabel(self.i18n.tr("developer_credit"))
        self.dev_label.setStyleSheet("color: #787c99; font-weight: bold; margin-right: 10px;")

        self.github_btn = QPushButton("💻 GitHub")
        self.github_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b4261;
                color: #c0caf5;
                font-size: 11px;
                padding: 3px 8px;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                background-color: #7aa2f7;
                color: #15161e;
            }
        """)
        self.github_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/mustafao9")))

        self.footer_donate_btn = QPushButton(self.i18n.tr("donate_btn"))
        self.footer_donate_btn.setStyleSheet("background-color: #e0af68; color: #15161e; font-weight: bold; padding: 4px 12px; border: none;")
        self.footer_donate_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://buymeacoffee.com/mustafasatilmis")))

        self.status_bar.addPermanentWidget(self.dev_label)
        self.status_bar.addPermanentWidget(self.github_btn)
        self.status_bar.addPermanentWidget(self.footer_donate_btn)

    def init_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        icon_path = self.paths.assets_dir / "icons" / "app.png"
        if icon_path.exists():
            self.tray_icon.setIcon(QIcon(str(icon_path)))
        else:
            self.tray_icon.setIcon(self.style().standardIcon(QApplication.instance().style().StandardPixmap.SP_ComputerIcon))

        tray_menu = QMenu()
        self.action_toggle_window = QAction(self.i18n.tr("tray_show_hide"), self)
        self.action_toggle_window.triggered.connect(self.toggle_window_visibility)

        self.action_quit = QAction(self.i18n.tr("tray_quit"), self)
        self.action_quit.triggered.connect(self.force_quit_app)

        tray_menu.addAction(self.action_toggle_window)
        tray_menu.addSeparator()
        tray_menu.addAction(self.action_quit)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()

    def toggle_window_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.showNormal()
            self.activateWindow()

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.toggle_window_visibility()

    def closeEvent(self, event):
        if self.tray_icon.isVisible():
            reply = QMessageBox.question(
                self,
                self.i18n.tr("app_name"),
                self.i18n.tr("background_question"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.hide()
                self.tray_icon.showMessage(
                    "MstPull",
                    self.i18n.tr("tray_minimized"),
                    QSystemTrayIcon.MessageIcon.Information,
                    2000
                )
                event.ignore()
                return
        self.tray_icon.hide()
        event.accept()

    def force_quit_app(self):
        self.tray_icon.hide()
        QApplication.quit()

    def toggle_clipboard_monitor(self, checked: bool):
        self.clipboard_monitor.is_enabled = checked

    def on_clipboard_url_detected(self, url: str):
        if self.url_input.text().strip():
            return
        self.url_input.setText(url)
        self.status_bar.showMessage(
            self.i18n.tr("clipboard_detected").format(url=url[:35] + "...")
        )
        if not self.isVisible():
            self.tray_icon.showMessage(
                self.i18n.tr("tray_new_link_title"),
                self.i18n.tr("tray_new_link_body").format(url=url[:40] + "..."),
                QSystemTrayIcon.MessageIcon.Information,
                2500
            )

    def on_concurrent_changed(self, index):
        val_map = {0: 1, 1: 2, 2: 3, 3: 5}
        val = val_map.get(index, 2)
        self.queue_manager.set_max_concurrent(val)

    def change_language(self, index=None):
        if index is None:
            index = self.lang_combo.currentIndex()
        lang_code = self.lang_combo.itemData(index)
        if lang_code:
            self.i18n.set_language(lang_code)

    def retranslate_ui(self):
        self.setWindowTitle(self.i18n.tr("app_name"))
        self.url_input.setPlaceholderText(self.i18n.tr("url_placeholder"))
        self.paste_btn.setText(self.i18n.tr("paste_btn"))
        self.add_queue_btn.setText(self.i18n.tr("add_queue_btn"))
        self.history_btn.setText(self.i18n.tr("history_btn"))

        self.chk_playlist.setText(self.i18n.tr("chk_playlist"))
        self.lbl_video_qual.setText(self.i18n.tr("video_quality"))
        current_v_idx = self.combo_video_qual.currentIndex()
        self.combo_video_qual.blockSignals(True)
        self.combo_video_qual.clear()
        self.combo_video_qual.addItems([self.i18n.tr("qual_best"), "1080p (Full HD)", "720p (HD)", "480p", self.i18n.tr("qual_lowest")])
        if current_v_idx >= 0:
            self.combo_video_qual.setCurrentIndex(current_v_idx)
        else:
            self.combo_video_qual.setCurrentIndex(0)
        self.combo_video_qual.blockSignals(False)

        self.lbl_audio_qual.setText(self.i18n.tr("audio_quality"))
        current_a_idx = self.combo_audio_qual.currentIndex()
        self.combo_audio_qual.blockSignals(True)
        self.combo_audio_qual.clear()
        self.combo_audio_qual.addItems(["320 kbps", "256 kbps", "192 kbps", "128 kbps"])
        if current_a_idx >= 0:
            self.combo_audio_qual.setCurrentIndex(current_a_idx)
        else:
            self.combo_audio_qual.setCurrentIndex(0)
        self.combo_audio_qual.blockSignals(False)

        self.lbl_target_folder.setText(self.i18n.tr("target_folder"))
        self.browse_btn.setText(self.i18n.tr("browse_btn"))
        self.lbl_queue_title.setText(self.i18n.tr("queue_title"))

        self.lbl_concurrent.setText(self.i18n.tr("concurrent_label"))
        current_c_idx = self.combo_concurrent.currentIndex()
        self.combo_concurrent.blockSignals(True)
        self.combo_concurrent.clear()
        self.combo_concurrent.addItems([
            self.i18n.tr("concurrent_1"),
            self.i18n.tr("concurrent_2"),
            self.i18n.tr("concurrent_3"),
            self.i18n.tr("concurrent_5"),
        ])
        if current_c_idx >= 0:
            self.combo_concurrent.setCurrentIndex(current_c_idx)
        else:
            self.combo_concurrent.setCurrentIndex(1)
        self.combo_concurrent.blockSignals(False)
        val_map = {0: 1, 1: 2, 2: 3, 3: 5}
        self.queue_manager.set_max_concurrent(val_map.get(self.combo_concurrent.currentIndex(), 2))

        self.lbl_rate_limit.setText(self.i18n.tr("rate_limit_label"))
        current_r_idx = self.combo_rate_limit.currentIndex()
        self.combo_rate_limit.blockSignals(True)
        self.combo_rate_limit.clear()
        self.combo_rate_limit.addItem(self.i18n.tr("rate_unlimited"), "Unlimited")
        self.combo_rate_limit.addItem("1 MB/s", "1M")
        self.combo_rate_limit.addItem("2 MB/s", "2M")
        self.combo_rate_limit.addItem("5 MB/s", "5M")
        self.combo_rate_limit.addItem("10 MB/s", "10M")
        if current_r_idx >= 0:
            self.combo_rate_limit.setCurrentIndex(current_r_idx)
        else:
            self.combo_rate_limit.setCurrentIndex(0)
        self.combo_rate_limit.blockSignals(False)

        self.chk_clipboard.setText(self.i18n.tr("chk_clipboard"))

        self.dev_label.setText(self.i18n.tr("developer_credit"))
        self.footer_donate_btn.setText(self.i18n.tr("donate_btn"))
        self.github_btn.setText(self.i18n.tr("github_btn"))
        if hasattr(self, "action_toggle_window"):
            self.action_toggle_window.setText(self.i18n.tr("tray_show_hide"))
        if hasattr(self, "action_quit"):
            self.action_quit.setText(self.i18n.tr("tray_quit"))

        disc_txt = self.i18n.tr("disclaimer_text")
        if disc_txt == "disclaimer_text" or not disc_txt:
            disc_txt = "⚠️ YASAL UYARI: Bu programla telif hakkı olan içerikler indirilemez ve bu amaçla kullanılamaz. Tüm kullanım sorumluluğu son kullanıcıya aittir."
        self.disclaimer_label.setText(disc_txt)

        for widget in self.active_widgets.values():
            widget.retranslate_ui()
        for widget in self.completed_widgets.values():
            widget.retranslate_ui()

    def paste_from_clipboard(self):
        clipboard = QApplication.clipboard()
        self.url_input.setText(clipboard.text().strip())

    def select_folder(self):
        current_dir = self.folder_input.text().strip()
        start_dir = current_dir if current_dir and Path(current_dir).exists() else str(self.paths.default_download_dir)
        folder = QFileDialog.getExistingDirectory(self, self.i18n.tr("target_folder"), start_dir)
        if folder:
            self.folder_input.setText(folder)

    def add_to_queue(self):
        url = self.url_input.text().strip()
        if not url:
            return

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(self.i18n.tr("confirm_title"))
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setText(self.i18n.tr("confirm_msg"))
        msg_box.setInformativeText(self.i18n.tr("disclaimer_text"))
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        msg_box.setMinimumWidth(500)
        reply = msg_box.exec()
        if reply != QMessageBox.StandardButton.Yes:
            self.status_bar.showMessage(self.i18n.tr("status_ready"))
            return

        if self.chk_playlist.isChecked():
            self._last_playlist_url = url
            self.status_bar.showMessage(self.i18n.tr("analyzing_playlist"))
            task_id = str(uuid.uuid4())[:8]

            fetcher = PlaylistFetcher(task_id, url, self.paths.get_yt_dlp_path(), self)
            fetcher.playlist_fetched.connect(self.on_playlist_fetched)
            fetcher.error_occurred.connect(lambda tid, err: self.on_playlist_error(tid, err))
            self.fetchers[task_id] = fetcher
            fetcher.start()
            self.url_input.clear()
            return

        task_id = str(uuid.uuid4())[:8]
        item = DownloadItemWidget(task_id, url, self.i18n)
        
        item.btn_dl_video.clicked.connect(lambda checked=False, tid=task_id, u=url: self.start_single_download(tid, u, is_audio=False))
        item.btn_dl_audio.clicked.connect(lambda checked=False, tid=task_id, u=url: self.start_single_download(tid, u, is_audio=True))
        item.btn_switch_mode.clicked.connect(lambda checked=False, tid=task_id, u=url: self.switch_and_re_download(tid, u))
        item.cancel_btn.clicked.connect(lambda checked=False, tid=task_id: self.cancel_task(tid))
        
        self.active_widgets[task_id] = item
        self.scroll_layout.addWidget(item)

        fetcher = MediaInfoFetcher(task_id, url, self.paths.get_yt_dlp_path(), self)
        fetcher.info_fetched.connect(self.on_info_fetched)
        fetcher.error_occurred.connect(self.on_info_error)
        self.fetchers[task_id] = fetcher
        fetcher.start()

        self.url_input.clear()

    def on_playlist_fetched(self, task_id: str, items: list):
        self.status_bar.showMessage(self.i18n.tr("status_ready"))
        self.fetchers.pop(task_id, None)

        if not items:
            reply = QMessageBox.question(
                self, "MstPull",
                self.i18n.tr("playlist_empty_single"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.chk_playlist.setChecked(False)
                self.url_input.setText(getattr(self, "_last_playlist_url", ""))
                self.add_to_queue()
            return

        dialog = PlaylistDialog(items, self.i18n, self)
        if dialog.exec() == PlaylistDialog.DialogCode.Accepted:
            selected = getattr(dialog, "selected_items", None) or []
            for item, is_audio in selected:
                item_url = item.get("url")
                sub_task_id = str(uuid.uuid4())[:8]
                widget = DownloadItemWidget(sub_task_id, item_url, self.i18n)
                widget.set_media_info(item.get("title", ""), item.get("duration", ""))

                widget.btn_dl_video.clicked.connect(lambda checked=False, tid=sub_task_id, u=item_url: self.start_single_download(tid, u, is_audio=False))
                widget.btn_dl_audio.clicked.connect(lambda checked=False, tid=sub_task_id, u=item_url: self.start_single_download(tid, u, is_audio=True))
                widget.btn_switch_mode.clicked.connect(lambda checked=False, tid=sub_task_id, u=item_url: self.switch_and_re_download(tid, u))
                widget.cancel_btn.clicked.connect(lambda checked=False, tid=sub_task_id: self.cancel_task(tid))

                self.active_widgets[sub_task_id] = widget
                self.scroll_layout.addWidget(widget)

                self.start_single_download(sub_task_id, item_url, is_audio=is_audio)

    def on_playlist_error(self, task_id: str, err_msg: str):
        self.status_bar.showMessage(self.i18n.tr("playlist_error_status"))
        QMessageBox.warning(
            self, "MstPull",
            self.i18n.tr("playlist_error").format(err=err_msg[:200])
        )
        self.fetchers.pop(task_id, None)

    def on_info_fetched(self, task_id: str, info: dict):
        if task_id in self.active_widgets:
            widget = self.active_widgets[task_id]
            widget.set_media_info(info.get("title", ""), info.get("duration", ""))
        self.fetchers.pop(task_id, None)

    def on_info_error(self, task_id: str, err_msg: str):
        if task_id in self.active_widgets:
            widget = self.active_widgets[task_id]
            fallback_title = getattr(widget, "url", self.i18n.tr("unknown"))[:35]
            widget.set_media_info(fallback_title, "")
            widget.info_label.setText(
                self.i18n.tr("info_error").format(err=err_msg[:80])
            )
        self.fetchers.pop(task_id, None)

    def start_single_download(self, task_id: str, url: str, is_audio: bool):
        # Tamamlanan listede ise tekrar aktif listeye al
        if task_id not in self.active_widgets:
            if task_id in self.completed_widgets:
                self.active_widgets[task_id] = self.completed_widgets.pop(task_id)
            else:
                return

        widget = self.active_widgets[task_id]
        user_folder = self.folder_input.text().strip()
        if user_folder and Path(user_folder).exists() and Path(user_folder) != self.paths.default_download_dir:
            base_dir = Path(user_folder)
            target_dir = base_dir / ("mp3" if is_audio else "video")
        else:
            target_dir = self.paths.mp3_download_dir if is_audio else self.paths.video_download_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        widget.is_audio_mode = is_audio
        widget.start_download_ui(is_audio, target_dir)

        quality = self.combo_audio_qual.currentText() if is_audio else self.combo_video_qual.currentText()
        rate_limit = self.combo_rate_limit.currentData() or "Unlimited"
        yt_dlp_path = self.paths.get_yt_dlp_path()
        ffmpeg_path = self.paths.get_ffmpeg_path()
        download_playlist = self.chk_playlist.isChecked()

        mode_str = "MP3" if is_audio else "VIDEO"
        self.history_service.add_entry(url, mode_str, quality, str(target_dir))

        worker = DownloadWorker(
            task_id, url, target_dir, yt_dlp_path, ffmpeg_path, 
            is_audio, quality, rate_limit, download_playlist
        )
        self.queue_manager.add_task(worker)

    def switch_and_re_download(self, old_task_id: str, url: str):
        old_widget = self.active_widgets.get(old_task_id) or self.completed_widgets.get(old_task_id)
        if not old_widget:
            return

        new_is_audio = not getattr(old_widget, "is_audio_mode", False)
        old_title = getattr(old_widget, "raw_title", "")
        old_duration = getattr(old_widget, "raw_duration", "")

        self.queue_manager.cancel_task(old_task_id)
        self.scroll_layout.removeWidget(old_widget)
        old_widget.deleteLater()
        self.active_widgets.pop(old_task_id, None)
        self.completed_widgets.pop(old_task_id, None)

        new_task_id = str(uuid.uuid4())[:8]
        item = DownloadItemWidget(new_task_id, url, self.i18n)
        item.set_media_info(old_title, old_duration)
        
        item.btn_dl_video.clicked.connect(lambda checked=False, tid=new_task_id, u=url: self.start_single_download(tid, u, is_audio=False))
        item.btn_dl_audio.clicked.connect(lambda checked=False, tid=new_task_id, u=url: self.start_single_download(tid, u, is_audio=True))
        item.btn_switch_mode.clicked.connect(lambda checked=False, tid=new_task_id, u=url: self.switch_and_re_download(tid, u))
        item.cancel_btn.clicked.connect(lambda checked=False, tid=new_task_id: self.cancel_task(tid))

        self.active_widgets[new_task_id] = item
        self.scroll_layout.addWidget(item)

        self.start_single_download(new_task_id, url, is_audio=new_is_audio)

    def open_history_dialog(self):
        dialog = HistoryDialog(self.history_service, self.i18n, self)
        dialog.exec()

    def cancel_task(self, task_id: str):
        self.queue_manager.cancel_task(task_id)
        widget = self.active_widgets.pop(task_id, None) or self.completed_widgets.pop(task_id, None)
        if widget:
            widget.info_label.setText(self.i18n.tr("cancelled"))
            self.scroll_layout.removeWidget(widget)
            widget.deleteLater()

    def on_task_progress(self, task_id: str, percent: float, speed: str, eta: str):
        if task_id in self.active_widgets:
            widget = self.active_widgets[task_id]
            if getattr(widget, "is_completed", False):
                return
            widget.update_progress(percent, speed, eta)

    def on_task_finished(self, task_id: str, success: bool, msg: str):
        if task_id in self.active_widgets:
            widget = self.active_widgets[task_id]
            if success:
                widget.mark_as_completed()
                if not self.isVisible():
                    raw_title = getattr(widget, "raw_title", "") or getattr(widget, "url", "")
                    self.tray_icon.showMessage(
                        self.i18n.tr("tray_download_done_title"),
                        self.i18n.tr("tray_download_done_body").format(title=raw_title[:35] + "..."),
                        QSystemTrayIcon.MessageIcon.Information,
                        3000
                    )
            else:
                widget.info_label.setText(f"❌ {msg}")
                if hasattr(widget, "retry_btn"):
                    try:
                        widget.retry_btn.clicked.disconnect()
                    except TypeError:
                        pass
                    widget.retry_btn.clicked.connect(
                        lambda checked=False, tid=task_id, u=widget.url, a=getattr(widget, "is_audio_mode", False):
                            self.start_single_download(tid, u, is_audio=a)
                    )
                return
            self.completed_widgets[task_id] = widget
            self.active_widgets.pop(task_id, None)
