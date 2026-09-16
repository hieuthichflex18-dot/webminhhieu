from rich.console import Console
from rich.panel import Panel
from pathlib import Path

from downloader import TikTokDownloader
from transcriber import Transcriber
from rewriter import ContentRewriter
from tts_engine import TTSEngine
from video_maker import VideoMaker
from uploader import TikTokUploader

console = Console()


class ReupPipeline:
    """Pipeline: Link → Text → Rewrite → Voice → Video → Upload."""

    def __init__(self, config: dict, progress_cb=None):
        self.cfg = config
        self.progress_cb = progress_cb
        self.downloader = TikTokDownloader(config["paths"]["downloads"])
        self.transcriber = None
        self.rewriter = ContentRewriter(
            config["api"]["base_url"],
            config["api"]["api_key"],
            config["api"]["default_model"],
        )
        self.tts = TTSEngine(config["paths"]["audio"])
        self.maker = VideoMaker(config)

    def _log(self, step, msg):
        console.print(f"[cyan]{step}[/cyan] {msg}")
        if self.progress_cb:
            self.progress_cb(step, msg)

    def run(self, url, voice_key="adam_vi", auto_upload=False,
            visibility="public") -> dict:
        result = {"success": False}

        # BƯỚC 1: Tải video
        self._log("BƯỚC 1/6:", "Tải video gốc...")
        video_path = self.downloader.download(url)
        if not video_path:
            return result
        self._log("✅", f"Đã tải: {video_path}")
        result["original_video"] = video_path

        # BƯỚC 2: Transcript
        self._log("BƯỚC 2/6:", "Trích xuất văn bản (Whisper)...")
        if self.transcriber is None:
            self.transcriber = Transcriber(
                self.cfg["whisper"]["model"],
                self.cfg["whisper"]["language"],
            )
        transcript_data = self.transcriber.transcribe(video_path)
        original_text = transcript_data["text"]
        self._log("✅", f"Văn bản gốc ({len(original_text)} ký tự)")
        result["transcript"] = original_text

        if not original_text.strip():
            return result

        # BƯỚC 3: Rewrite
        self._log("BƯỚC 3/6:", "AI viết lại tránh bản quyền...")
        rewritten = self.rewriter.rewrite(original_text)
        title = self.rewriter.generate_title(rewritten)
        hashtags = self.rewriter.generate_hashtags(rewritten)
        self._log("✅", f"Tiêu đề: {title}")
        result["rewritten"] = rewritten
        result["title"] = title
        result["hashtags"] = hashtags

        # BƯỚC 4: TTS
        self._log("BƯỚC 4/6:", f"Tạo giọng nói ({voice_key})...")
        audio_path = str(Path(self.cfg["paths"]["audio"]) / "voice.mp3")
        self.tts.text_to_speech(rewritten, voice_key=voice_key,
                                output_path=audio_path)
        result["audio"] = audio_path

        # BƯỚC 5: Tạo video
        self._log("BƯỚC 5/6:", "Tạo video mới...")
        new_video = self.maker.create_video(
            script_text=rewritten,
            audio_path=audio_path,
            output_name=f"reup_{Path(video_path).stem}.mp4",
        )
        self._log("✅", f"Video: {new_video}")
        result["video_path"] = new_video
        result["success"] = True

        # BƯỚC 6: Upload
        if auto_upload:
            self._log("BƯỚC 6/6:", "Đăng TikTok...")
            uploader = TikTokUploader(self.cfg["tiktok_cookies"])
            upload_result = uploader.upload_video(
                new_video, title, hashtags, visibility
            )
            result["upload"] = upload_result
            if upload_result.get("success"):
                self._log("✅", f"Đã đăng! ID: {upload_result.get('post_id')}")
            else:
                self._log("❌", f"Upload lỗi: {upload_result.get('error')}")

        return result
