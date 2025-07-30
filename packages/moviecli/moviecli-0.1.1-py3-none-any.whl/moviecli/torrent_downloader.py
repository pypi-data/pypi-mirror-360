import asyncio
from torrentp import TorrentDownloader as TPDownloader

class TorrentDownloader:
    def __init__(self, file_path, save_path='.', port=6881):
        self.file_path = file_path
        self.save_path = save_path
        self.port = port
        self.progress = 0.0
        self.status = 'idle'

        self.torrent = TPDownloader(
            file_path=file_path,
            save_path=save_path,
            port=port
        )

    def start_download(self):
        if self.status == "downloading":
            print("Já está em progresso.")
            return

        self.status = "downloading"
        asyncio.run(self.torrent.start_download())

        self.status = "completed"

    def pause_download(self):
        self.torrent.pause_download()
        self.status = "paused"

    def resume_download(self):
        self.torrent.resume_download()
        self.status = "downloading"

    def stop_download(self):
        self.torrent.stop_download()
        self.status = "stopped"

    def get_progress(self):
        try:
            if hasattr(self.torrent, "_downloader"):
                return round(self.torrent._downloader._get_status_progress, 2)
        except Exception:
            pass
        return 0.0
