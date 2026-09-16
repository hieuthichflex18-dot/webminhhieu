import asyncio
import edge_tts
from pathlib import Path
import os


VOICES = {
    # Tiếng Việt
    "adam_vi": "vi-VN-NamMinhNeural",
    "hoaimy_vi": "vi-VN-HoaiMyNeural",

    # Anh-Mỹ Nam
    "adam_en": "en-US-GuyNeural",
    "andrew_en": "en-US-AndrewMultilingualNeural",
    "brian_en": "en-US-BrianNeural",
    "christopher_en": "en-US-ChristopherNeural",
    "eric_en": "en-US-EricNeural",
    "roger_en": "en-US-RogerNeural",
    "steffan_en": "en-US-SteffanNeural",

    # Anh-Mỹ Nữ
    "aria_en": "en-US-AriaNeural",
    "ava_en": "en-US-AvaMultilingualNeural",
    "emma_en": "en-US-EmmaMultilingualNeural",
    "jenny_en": "en-US-JennyNeural",
    "michelle_en": "en-US-MichelleNeural",
    "ana_en": "en-US-AnaNeural",

    # Anh-Anh / Anh-Úc
    "ryan_uk": "en-GB-RyanNeural",
    "sonia_uk": "en-GB-SoniaNeural",
    "william_au": "en-AU-WilliamNeural",
    "natasha_au": "en-AU-NatashaNeural",

    # Đa ngôn ngữ
    "xiaoxiao_zh": "zh-CN-XiaoxiaoNeural",
    "yunxi_zh": "zh-CN-YunxiNeural",
    "nanami_ja": "ja-JP-NanamiNeural",
    "keita_ja": "ja-JP-KeitaNeural",
    "sunhi_ko": "ko-KR-SunHiNeural",
    "injoon_ko": "ko-KR-InJoonNeural",
}


class TTSEngine:
    """Text-to-Speech engine với Adam và 20+ giọng khác."""

    def __init__(self, output_dir: str = "./audio"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def list_voices() -> dict:
        return VOICES

    async def _synthesize(self, text, voice, rate, volume, pitch, output_path):
        communicate = edge_tts.Communicate(
            text=text, voice=voice, rate=rate, volume=volume, pitch=pitch
        )
        await communicate.save(output_path)

    def text_to_speech(self, text: str, voice_key: str = "adam_vi",
                       rate: str = "+0%", volume: str = "+0%",
                       pitch: str = "+0Hz", output_path: str = None) -> str:
        voice_name = VOICES.get(voice_key)
        if not voice_name:
            raise ValueError(f"Không tìm thấy giọng: {voice_key}")

        if not output_path:
            output_path = str(self.output_dir / f"tts_{voice_key}.mp3")

        if len(text) > 3000:
            return self._synthesize_long(text, voice_name, rate, volume,
                                         pitch, output_path)

        asyncio.run(self._synthesize(text, voice_name, rate, volume,
                                     pitch, output_path))
        return output_path

    def _synthesize_long(self, text, voice, rate, volume, pitch, output_path):
        sentences = []
        current = ""
        for ch in text:
            current += ch
            if ch in ".!?\n" and len(current) > 200:
                sentences.append(current.strip())
                current = ""
        if current.strip():
            sentences.append(current.strip())

        chunks, chunk = [], ""
        for s in sentences:
            if len(chunk) + len(s) > 2500:
                chunks.append(chunk.strip())
                chunk = ""
            chunk += s + " "
        if chunk.strip():
            chunks.append(chunk.strip())

        temp_files = []
        for i, c in enumerate(chunks):
            temp_path = f"{output_path}.part{i}.mp3"
            asyncio.run(self._synthesize(c, voice, rate, volume, pitch, temp_path))
            temp_files.append(temp_path)

        self._merge_audio(temp_files, output_path)
        for f in temp_files:
            try:
                os.remove(f)
            except Exception:
                pass
        return output_path

    @staticmethod
    def _merge_audio(files: list, output: str):
        import subprocess
        list_file = output + ".list.txt"
        with open(list_file, "w", encoding="utf-8") as f:
            for path in files:
                f.write(f"file '{os.path.abspath(path)}'\n")
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
             "-i", list_file, "-c", "copy", output],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        try:
            os.remove(list_file)
        except Exception:
            pass

    def generate_multi_voice(self, script: list, output_path: str) -> str:
        temp_files = []
        for i, part in enumerate(script):
            tmp = f"{output_path}.scene{i}.mp3"
            self.text_to_speech(
                part["text"],
                voice_key=part.get("voice", "adam_vi"),
                output_path=tmp,
            )
            temp_files.append(tmp)
        self._merge_audio(temp_files, output_path)
        for f in temp_files:
            try:
                os.remove(f)
            except Exception:
                pass
        return output_path
