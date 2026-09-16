import requests
import json
import random


REWRITE_PROMPTS = [
    """Bạn là chuyên gia viết content viral. Viết lại đoạn văn bản sau đây theo cách HOÀN TOÀN MỚI:
- Giữ nguyên ý chính và thông tin cốt lõi
- Đổi cấu trúc câu, từ vựng, cách diễn đạt
- Thêm hook hấp dẫn ở đầu
- Thêm CTA ở cuối
- Ngôn ngữ tự nhiên, phù hợp TikTok
- KHÔNG copy nguyên câu nào

Văn bản gốc:
\"\"\"{text}\"\"\"

Chỉ trả về văn bản đã viết lại.""",

    """Viết lại script video sau để tránh bản quyền, phong cách kể chuyện cuốn hút:
- Mở đầu bằng câu hỏi hoặc tình huống gây tò mò
- Đổi toàn bộ cách diễn đạt, giữ nguyên thông tin
- Chia thành các đoạn ngắn, dễ đọc thành voice
- Kết thúc bằng CTA tự nhiên

Nội dung:
\"\"\"{text}\"\"\"

Trả về duy nhất nội dung đã viết lại.""",

    """Bạn là biên kịch TikTok. Chuyển đoạn văn sau thành kịch bản video ngắn 60 giây:
- Hook 3 giây đầu cực mạnh
- Nội dung cô đọng, súc tích
- Ngôn ngữ đời thường, dễ nghe
- Đảm bảo KHÁC BIỆT hoàn toàn về câu chữ

Bản gốc:
\"\"\"{text}\"\"\"

Chỉ trả về script mới.""",
]


class ContentRewriter:
    """Viết lại nội dung bằng AI để tránh bản quyền."""

    def __init__(self, base_url: str, api_key: str, model: str = "gpt-4o-mini"):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    def rewrite(self, text: str, style: str = "viral") -> str:
        if not text.strip():
            return ""
        template = random.choice(REWRITE_PROMPTS)
        prompt = template.format(text=text[:6000])
        messages = [
            {"role": "system",
             "content": "Bạn là chuyên gia content TikTok, viết lách sáng tạo."},
            {"role": "user", "content": prompt},
        ]
        return self._call_api(messages)

    def generate_title(self, text: str) -> str:
        messages = [
            {"role": "system", "content": "Bạn chuyên viết tiêu đề viral TikTok."},
            {"role": "user",
             "content": f"Viết 1 tiêu đề TikTok hấp dẫn (tối đa 100 ký tự, "
                        f"có 1-2 emoji, không dấu ngoặc kép) cho nội dung sau:\n\n"
                        f"{text[:1500]}\n\nChỉ trả về tiêu đề."}
        ]
        return self._call_api(messages).strip().strip('"').strip("'")

    def generate_hashtags(self, text: str, count: int = 8) -> list:
        messages = [
            {"role": "user",
             "content": f"Tạo {count} hashtag TikTok tiếng Việt phù hợp cho nội dung sau. "
                        f"Trả về mỗi hashtag 1 dòng, có dấu #, không giải thích:\n\n"
                        f"{text[:1500]}"}
        ]
        result = self._call_api(messages)
        tags = [line.strip() for line in result.split("\n")
                if line.strip().startswith("#")]
        return tags[:count]

    def _call_api(self, messages: list) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.85,
        }
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=120)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[LỖI REWRITE] {e}")
            return messages[-1]["content"] if messages else ""
