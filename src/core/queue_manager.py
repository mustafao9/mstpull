from collections import deque
from typing import Dict
from PyQt6.QtCore import QObject, pyqtSignal
from src.core.downloader import DownloadWorker
from src.utils.logging_config import get_logger

class QueueManager(QObject):
    task_progress = pyqtSignal(str, float, str, str)
    task_finished = pyqtSignal(str, bool, str)

    def __init__(self, max_concurrent: int = 2):
        super().__init__()
        self.max_concurrent = max_concurrent
        self.pending_queue = deque()
        self.active_workers: Dict[str, DownloadWorker] = {}
        self.logger = get_logger()

    def set_max_concurrent(self, val: int):
        self.max_concurrent = val
        self.logger.info(f"Eşzamanlı indirme sayısı güncellendi: {val}")
        self.process_queue()

    def add_task(self, worker: DownloadWorker):
        worker.progress.connect(self._on_progress)
        worker.finished.connect(self._on_finished)
        self.pending_queue.append(worker)
        self.logger.info(f"Kuyruğa yeni görev eklendi: {worker.task_id}")
        self.process_queue()

    def process_queue(self):
        while len(self.active_workers) < self.max_concurrent and self.pending_queue:
            worker = self.pending_queue.popleft()
            self.active_workers[worker.task_id] = worker
            worker.start()
            self.logger.info(f"Kuyruktan görev başlatıldı: {worker.task_id}")

    def cancel_task(self, task_id: str):
        if task_id in self.active_workers:
            worker = self.active_workers[task_id]
            worker.cancel()
            del self.active_workers[task_id]
            self.logger.info(f"Aktif görev iptal edildi: {task_id}")
            self.process_queue()
        else:
            self.pending_queue = deque([w for w in self.pending_queue if w.task_id != task_id])

    def _on_progress(self, task_id: str, percent: float, speed: str, eta: str):
        self.task_progress.emit(task_id, percent, speed, eta)

    def _on_finished(self, task_id: str, success: bool, msg: str):
        if task_id in self.active_workers:
            del self.active_workers[task_id]
        self.task_finished.emit(task_id, success, msg)
        self.process_queue()
