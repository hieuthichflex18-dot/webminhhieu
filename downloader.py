import yt_dlp
import os
from pathlib import Path


class TikTokDownloader:
    """Tải video đa nền tảng không watermark bằng yt-dlp."""

    def __init__(self, output_dir: str = "./downloads"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def download(self, url: str, cookies_file: str = None) -> str | None:
        ydl_opts = {
            "format": "bestvideo+bestaudio/best",
            "outtmpl": str(self.output_dir / "%(id)s.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
            "merge_output_format": "mp4",
        }
        if cookies_file and os.path.exists(cookies_file):
            ydl_opts["cookiefile"] = cookies_file

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                mp4_path = Path(filename).with_suffix(".mp4")
                if mp4_path.exists():
                    return str(mp4_path)
                return filename
        except Exception as e:
            print(f"[LỖI] Không tải được video: {e}")
            return None

    def download_batch(self, urls: list, cookies_file: str = None) -> list:
        results = []
        for i, url in enumerate(urls, 1):
            print(f"[{i}/{len(urls)}] Đang tải: {url[:60]}...")
            path = self.download(url, cookies_file)
            if path:
                results.append(path)
        return results

    def extract_info(self, url: str) -> dict | None:
        ydl_opts = {"quiet": True, "no_warnings": True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)
        except Exception as e:
            print(f"[LỖI] {e}")
            return None
