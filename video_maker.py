from moviepy.editor import (
    VideoFileClip, AudioFileClip, ImageClip,
    CompositeVideoClip, TextClip, concatenate_videoclips, ColorClip,
)
import os
import random
import re
from pathlib import Path


class VideoMaker:
    """Tạo video hoàn chỉnh: background + voice + subtitle."""

    def __init__(self, config: dict):
        self.cfg = config["video"]
        self.output_dir = Path(config["paths"]["output"])
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.bg_dir = Path(config["paths"]["backgrounds"])

    def _get_random_background(self, duration, size):
        if not self.bg_dir.exists():
            return ColorClip(size=size, color=tuple(self.cfg["bg_color"]),
                             duration=duration)

        files = []
        for ext in ("*.mp4", "*.mov", "*.webm", "*.jpg", "*.jpeg", "*.png"):
            files.extend(self.bg_dir.glob(ext))

        if not files:
            return ColorClip(size=size, color=tuple(self.cfg["bg_color"]),
                             duration=duration)

        chosen = random.choice(files)
        if chosen.suffix.lower() in (".mp4", ".mov", ".webm"):
            clip = VideoFileClip(str(chosen))
            if clip.duration < duration:
                loops = int(duration / clip.duration) + 1
                clip = concatenate_videoclips([clip] * loops)
            clip = clip.subclip(0, duration)
            return clip.resize(size)
        else:
            return ImageClip(str(chosen)).set_duration(duration).resize(size)

    def _make_subtitle_clips(self, segments, size):
        clips = []
        font_path = self.cfg.get("font", "Arial")
        for seg in segments:
            text = seg.get("text", "").strip()
            if not text:
                continue
            try:
                txt = TextClip(
                    text,
                    fontsize=self.cfg.get("font_size", 60),
                    color=self.cfg.get("subtitle_color", "white"),
                    font=font_path,
                    stroke_color="black",
                    stroke_width=3,
                    method="caption",
                    size=(size[0] - 120, None),
                )
            except Exception:
                txt = TextClip(text, fontsize=60, color="white",
                               font="Arial", method="caption",
                               size=(size[0] - 120, None))
            txt = (txt.set_position(("center", "center"))
                      .set_start(seg.get("start", 0))
                      .set_duration(seg.get("end", 0) - seg.get("start", 0)))
            clips.append(txt)
        return clips

    def create_video(self, script_text, audio_path, segments=None,
                     output_name=None) -> str:
        size = (self.cfg["width"], self.cfg["height"])
        audio = AudioFileClip(audio_path)
        duration = audio.duration

        background = self._get_random_background(duration, size)
        layers = [background]

        if segments:
            sub_clips = self._make_subtitle_clips(segments, size)
        else:
            lines = self._split_text(script_text, duration)
            sub_clips = self._make_subtitle_clips(lines, size)
        layers.extend(sub_clips)

        final = CompositeVideoClip(layers, size=size).set_duration(duration)
        final = final.set_audio(audio)

        if not output_name:
            output_name = "video_output.mp4"
        output_path = str(self.output_dir / output_name)

        final.write_videofile(
            output_path, codec="libx264", audio_codec="aac",
            fps=self.cfg.get("fps", 30), preset="medium", threads=4,
            verbose=False, logger=None,
        )

        background.close()
        audio.close()
        return output_path

    @staticmethod
    def _split_text(text, total_duration):
        sentences = re.split(r"(?<=[.!?])\s+", text)
        sentences = [s.strip() for s in sentences if s.strip()]
        if not sentences:
            return []
        total_chars = sum(len(s) for s in sentences)
        segments = []
        current_time = 0.0
        for s in sentences:
            seg_dur = (len(s) / total_chars) * total_duration
            segments.append({
                "text": s, "start": current_time,
                "end": current_time + seg_dur,
            })
            current_time += seg_dur
        return segments
