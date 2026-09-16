import requests
import os
from pathlib import Path


class TikTokUploader:
    """Đăng video TikTok bằng cookie (không cần API chính thức)."""

    def __init__(self, cookies: dict, proxy: str = None):
        self.session = requests.Session()
        self.session.cookies.update(cookies)
        self.proxy = proxy
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.tiktok.com/",
            "Origin": "https://www.tiktok.com",
        })

    def upload_video(self, video_path, title="", tags=None,
                     visibility="public", schedule_time=None) -> dict:
        if tags:
            title += " " + " ".join(f"#{t.lstrip('#')}" for t in tags)

        upload_params = self._get_upload_params()
        if not upload_params:
            return {"success": False, "error": "Không lấy được upload params"}

        video_id = self._upload_file(video_path, upload_params)
        if not video_id:
            return {"success": False, "error": "Upload file thất bại"}

        return self._create_post(video_id, title, visibility, schedule_time)

    def _get_upload_params(self):
        try:
            url = "https://www.tiktok.com/api/v1/video/upload/auth/"
            params = {"aid": "1988", "scene": "1",
                      "version_code": "1.0.0", "app_name": "tiktok_web"}
            r = self.session.get(url, params=params, timeout=30)
            if r.status_code == 200:
                return r.json()
            return None
        except Exception as e:
            print(f"[LỖI] Lấy upload params: {e}")
            return None

    def _upload_file(self, video_path, params):
        try:
            upload_url = params.get("upload_url", "")
            if not upload_url:
                return None
            file_size = os.path.getsize(video_path)
            with open(video_path, "rb") as f:
                files = {"video": (Path(video_path).name, f, "video/mp4")}
                data = {"upload_id": params.get("upload_id", ""),
                        "size": file_size}
                r = self.session.post(upload_url, files=files,
                                      data=data, timeout=300)
            if r.status_code in (200, 201):
                result = r.json()
                return result.get("video_id") or result.get("uri")
            return None
        except Exception as e:
            print(f"[LỖI] Upload file: {e}")
            return None

    def _create_post(self, video_id, title, visibility, schedule_time=None):
        try:
            url = "https://www.tiktok.com/api/v1/video/create/"
            visibility_map = {"public": 0, "private": 1, "friends": 2}
            data = {
                "video_id": video_id,
                "text": title[:2200],
                "visibility": visibility_map.get(visibility, 0),
                "allow_comment": 1,
                "allow_duet": 1,
                "allow_stitch": 1,
            }
            if schedule_time:
                data["schedule_time"] = schedule_time
            r = self.session.post(url, data=data, timeout=60)
            if r.status_code == 200:
                result = r.json()
                return {"success": True, "post_id": result.get("item_id"),
                        "message": "Đăng thành công!"}
            return {"success": False,
                    "error": f"HTTP {r.status_code}: {r.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def check_login(self) -> bool:
        try:
            r = self.session.get(
                "https://www.tiktok.com/passport/web/account/info/",
                timeout=15,
            )
            return r.status_code == 200 and "user_id" in r.text
        except Exception:
            return False
