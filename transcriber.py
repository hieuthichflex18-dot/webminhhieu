import whisper
import os
from pathlib import Path


class Transcriber:
    """Trích xuất văn bản từ video bằng Whisper AI (offline, miễn phí)."""

    _model_cache = {}

    def __init__(self, model_name: str = "base", language: str = "vi"):
        self.model_name = model_name
        self.language = language
        if model_name not in Transcriber._model_cache:
            print(f"[INFO] Đang load Whisper model: {model_name}...")
            Transcriber._model_cache[model_name] = whisper.load_model(model_name)
        self.model = Transcriber._model_cache[model_name]

    def transcribe(self, video_path: str) -> dict:
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Không tìm thấy: {video_path}")

        result = self.model.transcribe(
            video_path,
            language=self.language,
            task="transcribe",
            verbose=False,
        )

        return {
            "text": result["text"].strip(),
            "segments": result.get("segments", []),
            "language": result.get("language", self.language),
        }

    def transcribe_to_srt(self, video_path: str, output_path: str = None) -> str:
        if not output_path:
            output_path = str(Path(video_path).with_suffix(".srt"))

        result = self.transcribe(video_path)
        with open(output_path, "w", encoding="utf-8") as f:
            for i, seg in enumerate(result["segments"], 1):
                start = self._format_time(seg["start"])
                end = self._format_time(seg["end"])
                f.write(f"{i}\n{start} --> {end}\n{seg['text'].strip()}\n\n")
        return output_path

    @staticmethod
    def _format_time(seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds - int(seconds)) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
