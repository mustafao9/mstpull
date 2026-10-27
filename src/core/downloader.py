import os
import sys
import subprocess
import json
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal
from src.utils.logging_config import get_logger

class PlaylistFetcher(QThread):
    playlist_fetched = pyqtSignal(str, list)
    error_occurred = pyqtSignal(str, str)

    def __init__(self, task_id: str, url: str, yt_dlp_path: Path, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.url = url
        self.yt_dlp_path = yt_dlp_path

    def run(self):
        cmd = [str(self.yt_dlp_path), "--flat-playlist", "--dump-single-json", self.url]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            if res.returncode == 0:
                data = json.loads(res.stdout)
                entries = data.get("entries", [])
                items = []
                for entry in entries:
                    items.append({
                        "title": entry.get("title", "Bilinmeyen Video"),
                        "url": entry.get("url") or f"https://www.youtube.com/watch?v={entry.get('id')}",
                        "duration": entry.get("duration_string", "N/A")
                    })
                self.playlist_fetched.emit(self.task_id, items)
            else:
                self.error_occurred.emit(self.task_id, "Oynatma listesi bilgisi alınamadı.")
        except Exception as e:
            self.error_occurred.emit(self.task_id, str(e))

class MediaInfoFetcher(QThread):
    info_fetched = pyqtSignal(str, dict)
    error_occurred = pyqtSignal(str, str)

    def __init__(self, task_id: str, url: str, yt_dlp_path: Path, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.url = url
        self.yt_dlp_path = yt_dlp_path

    def run(self):
        cmd = [str(self.yt_dlp_path), "--dump-json", "--no-playlist", self.url]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if res.returncode == 0:
                data = json.loads(res.stdout)
                info = {
                    "title": data.get("title", "Bilinmeyen Başlık"),
                    "duration": data.get("duration_string", "N/A"),
                    "thumbnail": data.get("thumbnail", "")
                }
                self.info_fetched.emit(self.task_id, info)
            else:
                self.error_occurred.emit(self.task_id, "Video bilgisi alınamadı.")
        except Exception as e:
            self.error_occurred.emit(self.task_id, str(e))

class DownloadWorker(QThread):
    progress = pyqtSignal(str, float, str, str)
    finished = pyqtSignal(str, bool, str)

    def __init__(self, task_id: str, url: str, target_dir: Path, yt_dlp_path: Path, ffmpeg_path: Path, is_audio: bool, quality: str, rate_limit: str = "Unlimited", download_playlist: bool = False, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.url = url
        self.target_dir = target_dir
        self.yt_dlp_path = yt_dlp_path
        self.ffmpeg_path = ffmpeg_path
        self.is_audio = is_audio
        self.quality = quality
        self.rate_limit = rate_limit
        self.download_playlist = download_playlist
        self.logger = get_logger()
        self._is_cancelled = False
        self.process = None

    def run(self):
        try:
            self.target_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.finished.emit(self.task_id, False, f"Klasör Hatası: {str(e)}")
            return

        cmd = [
            str(self.yt_dlp_path), 
            "--newline", 
            "--no-colors",
            "-P", str(self.target_dir)
        ]

        if self.ffmpeg_path and self.ffmpeg_path.exists():
            cmd.extend(["--ffmpeg-location", str(self.ffmpeg_path.parent)])

        if self.rate_limit and self.rate_limit not in ["Unlimited", "Sınırsız"]:
            cmd.extend(["--limit-rate", self.rate_limit])

        if not self.download_playlist:
            cmd.append("--no-playlist")

        if self.is_audio:
            cmd.extend([
                "-x", 
                "--audio-format", "mp3",
                "--embed-thumbnail",
                "--add-metadata"
            ])
            if "320" in self.quality:
                cmd.extend(["--audio-quality", "0"])
            else:
                cmd.extend(["--audio-quality", "4"])
        else:
            if "1080" in self.quality:
                cmd.extend(["-f", "bestvideo[height<=1080]+bestaudio/best"])
            elif "720" in self.quality:
                cmd.extend(["-f", "bestvideo[height<=720]+bestaudio/best"])
            else:
                cmd.extend(["-f", "bestvideo+bestaudio/best"])

            cmd.extend(["--merge-output-format", "mp4"])

        cmd.append(self.url)

        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                preexec_fn=os.setsid if sys.platform != "win32" else None
            )

            for line in iter(self.process.stdout.readline, ''):
                if self._is_cancelled:
                    self._safe_kill_process()
                    self.finished.emit(self.task_id, False, "İptal Edildi")
                    return

                line_str = line.strip()
                if "[download]" in line_str and "%" in line_str:
                    try:
                        parts = line_str.split()
                        for i, part in enumerate(parts):
                            if "%" in part:
                                pct_str = part.replace("%", "")
                                percent = float(pct_str)
                                speed = parts[i+2] if i+2 < len(parts) else "N/A"
                                eta = parts[i+4] if i+4 < len(parts) else "N/A"
                                self.progress.emit(self.task_id, percent, speed, eta)
                                break
                    except Exception:
                        pass

            self.process.wait()
            if self._is_cancelled:
                self.finished.emit(self.task_id, False, "İptal Edildi")
            elif self.process.returncode == 0:
                self.finished.emit(self.task_id, True, "Tamamlandı")
            else:
                self.finished.emit(self.task_id, False, "İndirme Hatası")

        except Exception as e:
            self.finished.emit(self.task_id, False, str(e))

    def _safe_kill_process(self):
        if self.process:
            try:
                if sys.platform != "win32":
                    import signal
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                else:
                    self.process.terminate()
            except Exception:
                pass

    def cancel(self):
        self._is_cancelled = True
        self._safe_kill_process()
