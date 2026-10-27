import sys
import time
from pathlib import Path
from src.config.paths import AppPaths
from src.platform.binary_manager import BinaryManager
from src.core.downloader import DownloadWorker
from src.core.queue_manager import QueueManager

def run_diagnostics():
    print("=== MstPull Otomatik Sistem Teşhisi Başlatılıyor ===")
    paths = AppPaths()
    bm = BinaryManager(paths)

    yt_ok, yt_ver = bm.check_yt_dlp()
    ff_ok, ff_ver = bm.check_ffmpeg()

    print(f"[1] Motor Durumları:")
    print(f"    - yt-dlp : {'OK' if yt_ok else 'HATA'} ({yt_ver})")
    print(f"    - FFmpeg : {'OK' if ff_ok else 'HATA'} ({ff_ver})")

    print(f"[2] Klasör İzinleri:")
    print(f"    - MP3 Dizin : {paths.mp3_download_dir} (Var mı: {paths.mp3_download_dir.exists()})")
    print(f"    - Video Dizin: {paths.video_download_dir} (Var mı: {paths.video_download_dir.exists()})")

    print(f"[3] İptal ve Kuyruk Mantık Testi:")
    qm = QueueManager(max_concurrent=2)
    test_worker = DownloadWorker(
        task_id="test_01",
        url="https://www.youtube.com/watch?v=ba36a282-3d84-4e20-94d3-066b16e1e813",
        target_dir=paths.mp3_download_dir,
        yt_dlp_path=paths.get_yt_dlp_path(),
        ffmpeg_path=paths.get_ffmpeg_path(),
        is_audio=True,
        quality="320 kbps"
    )

    qm.add_task(test_worker)
    time.sleep(1)
    print("    - Görev başlatıldı, güvenli iptal tetikleniyor...")
    qm.cancel_task("test_01")
    time.sleep(1)
    print(f"    - Aktif Görev Sayısı: {len(qm.active_workers)} (Beklenen: 0)")
    print("=== Teşhis Başarıyla Tamamlandı ===")

if __name__ == '__main__':
    run_diagnostics()
