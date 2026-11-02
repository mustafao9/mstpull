from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, 
    QPushButton, QHeaderView, QCheckBox, QLabel
)
from PyQt6.QtCore import Qt

class PlaylistDialog(QDialog):
    """Oynatma listesindeki videoları listeleyip seçtiren şık diyalog ekranı."""
    def __init__(self, playlist_items, i18n_manager, parent=None):
        super().__init__(parent)
        self.items = playlist_items
        self.i18n = i18n_manager
        self.selected_items = []

        self.setWindowTitle("📋 Oynatma Listesi Seçimi")
        self.resize(780, 520)

        layout = QVBoxLayout(self)

        self.info_lbl = QLabel(f"Toplam {len(self.items)} adet video bulundu. İndirmek istediklerinizi seçin:")
        self.info_lbl.setStyleSheet("font-weight: bold; color: #7aa2f7; font-size: 13px;")
        layout.addWidget(self.info_lbl)

        # Tablo Oluşturma (4 Sütunlu Temiz Yapı)
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Seç", "#", "Video Başlığı", "Süre"])
        
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.table)

        # Seçim Butonları Satırı
        sel_layout = QHBoxLayout()
        self.btn_select_all = QPushButton("☑️ Tümünü Seç")
        self.btn_select_all.setStyleSheet("font-size: 11px; padding: 4px 8px;")
        self.btn_select_all.clicked.connect(self.select_all)
        
        self.btn_deselect_all = QPushButton("🔲 Seçimi Kaldır")
        self.btn_deselect_all.setStyleSheet("font-size: 11px; padding: 4px 8px;")
        self.btn_deselect_all.clicked.connect(self.deselect_all)
        
        sel_layout.addWidget(self.btn_select_all)
        sel_layout.addWidget(self.btn_deselect_all)
        sel_layout.addStretch()
        layout.addLayout(sel_layout)

        # Alt Eylem Butonları (Video / MP3)
        btn_layout = QHBoxLayout()
        
        self.btn_add_video = QPushButton("🎬 Seçilenleri Video Olarak Ekle")
        self.btn_add_video.setStyleSheet("background-color: #7aa2f7; color: #15161e; font-weight: bold; padding: 8px 14px;")
        self.btn_add_video.clicked.connect(lambda: self.confirm_selection(is_audio=False))

        self.btn_add_audio = QPushButton("🎵 Seçilenleri MP3 Olarak Ekle")
        self.btn_add_audio.setStyleSheet("background-color: #bb9af7; color: #15161e; font-weight: bold; padding: 8px 14px;")
        self.btn_add_audio.clicked.connect(lambda: self.confirm_selection(is_audio=True))

        self.btn_cancel = QPushButton("❌ İptal")
        self.btn_cancel.setStyleSheet("padding: 8px 14px;")
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_add_video)
        btn_layout.addWidget(self.btn_add_audio)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)
        self.populate_table()

    def populate_table(self):
        self.table.setRowCount(len(self.items))

        for row, item in enumerate(self.items):
            # Checkbox
            chk = QCheckBox()
            chk.setChecked(True)

            self.table.setCellWidget(row, 0, chk)
            self.table.setItem(row, 1, QTableWidgetItem(str(row + 1)))
            self.table.setItem(row, 2, QTableWidgetItem(item.get("title", "")))
            
            dur_str = item.get("duration", "")
            if not dur_str or dur_str == "N/A":
                dur_str = "-"
            self.table.setItem(row, 3, QTableWidgetItem(dur_str))

    def select_all(self):
        for row in range(self.table.rowCount()):
            chk = self.table.cellWidget(row, 0)
            if chk:
                chk.setChecked(True)

    def deselect_all(self):
        for row in range(self.table.rowCount()):
            chk = self.table.cellWidget(row, 0)
            if chk:
                chk.setChecked(False)

    def confirm_selection(self, is_audio: bool):
        self.selected_items = []
        for row, item in enumerate(self.items):
            chk = self.table.cellWidget(row, 0)
            if chk and chk.isChecked():
                self.selected_items.append((item, is_audio))
        self.accept()

class HistoryDialog(QDialog):
    """İndirme Geçmişini Gösteren Diyalog Penceresi"""
    def __init__(self, history_service, i18n_manager, parent=None):
        super().__init__(parent)
        self.history_service = history_service
        self.i18n = i18n_manager

        self.setWindowTitle(self.i18n.tr("history_title"))
        self.resize(750, 400)

        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            self.i18n.tr("hist_date"),
            self.i18n.tr("hist_url"),
            self.i18n.tr("hist_mode"),
            self.i18n.tr("hist_path")
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        self.close_btn = QPushButton(self.i18n.tr("close"))
        self.close_btn.clicked.connect(self.accept)
        layout.addWidget(self.close_btn)

        self.load_data()

    def load_data(self):
        records = self.history_service.get_history()
        self.table.setRowCount(len(records))
        for row, rec in enumerate(records):
            self.table.setItem(row, 0, QTableWidgetItem(rec.get("date", "")))
            self.table.setItem(row, 1, QTableWidgetItem(rec.get("url", "")))
            self.table.setItem(row, 2, QTableWidgetItem(rec.get("mode", "")))
            self.table.setItem(row, 3, QTableWidgetItem(rec.get("target_path", "")))
