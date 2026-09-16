from moviepy.editor import (
    VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip,
)
from pathlib import Path


class VideoProcessor:
    """Xử lý video: crop 9:16, flip, speed, tách nhạc."""

    def __init__(self, output_dir: str = "./output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def crop_916(self, input_path, output_path=None):
        if not output_path:
            output_path = str(self.output_dir / f"916_{Path(input_path).name}")
        clip = VideoFileClip(input_path)
        w, h = clip.size
        target_ratio = 9 / 16
        if w / h > target_ratio:
            new_w = int(h * target_ratio)
            clip = clip.crop(x_center=w / 2, width=new_w)
        else:
            new_h = int(w / target_ratio)
            clip = clip.crop(y_center=h / 2, height=new_h)
        clip.write_videofile(output_path, codec="libx264",
                             audio_codec="aac", verbose=False, logger=None)
        clip.close()
        return output_path

    def flip_horizontal(self, input_path, output_path=None):
        if not output_path:
            output_path = str(self.output_dir / f"flip_{Path(input_path).name}")
        clip = VideoFileClip(input_path)
        flipped = clip.fx(lambda c: c.fl_image(lambda img: img[:, ::-1]))
        flipped.write_videofile(output_path, codec="libx264",
                                audio_codec="aac",
                                verbose=False, logger=None)
        clip.close()
        return output_path

    def change_speed(self, input_path, speed=1.1, output_path=None):
        if not output_path:
            output_path = str(self.output_dir / f"speed_{Path(input_path).name}")
        clip = VideoFileClip(input_path)
        new_clip = clip.fx(lambda c: c.fl_time(lambda t: t * speed,
                                               apply_to=["mask"]))
        new_clip = new_clip.set_duration(clip.duration / speed)
        new_clip.write_videofile(output_path, codec="libx264",
                                 audio_codec="aac",
                                 verbose=False, logger=None)
        clip.close()
        return output_path

    def extract_audio(self, input_path, output_path=None):
        if not output_path:
            output_path = str(self.output_dir / f"{Path(input_path).stem}.mp3")
        clip = VideoFileClip(input_path)
        clip.audio.write_audiofile(output_path, verbose=False, logger=None)
        clip.close()
        return output_path

    def replace_audio(self, video_path, audio_path, output_path=None):
        if not output_path:
            output_path = str(self.output_dir / f"newaudio_{Path(video_path).name}")
        video = VideoFileClip(video_path)
        audio = AudioFileClip(audio_path)
        final = video.set_audio(audio)
        final.write_videofile(output_path, codec="libx264",
                              audio_codec="aac",
                              verbose=False, logger=None)
        video.close()
        audio.close()
        return output_path

    def add_text_overlay(self, input_path, text, output_path=None):
        if not output_path:
            output_path = str(self.output_dir / f"text_{Path(input_path).name}")
        clip = VideoFileClip(input_path)
        txt = TextClip(text, fontsize=40, color="white", font="Arial",
                       stroke_color="black", stroke_width=2)
        txt = txt.set_position(("center", "bottom")).set_duration(clip.duration)
        final = CompositeVideoClip([clip, txt])
        final.write_videofile(output_path, codec="libx264",
                              audio_codec="aac",
                              verbose=False, logger=None)
        clip.close()
        return output_path

    def full_process(self, input_path, crop=True, flip=False,
                     speed=1.0, new_audio=None):
        current = input_path
        if crop:
            current = self.crop_916(current)
        if flip:
            current = self.flip_horizontal(current)
        if speed != 1.0:
            current = self.change_speed(current, speed)
        if new_audio:
            current = self.replace_audio(current, new_audio)
        return current
