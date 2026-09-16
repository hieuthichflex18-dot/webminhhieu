import streamlit as st
import os
from pathlib import Path
from config import CONFIG
from tts_engine import TTSEngine, VOICES
from pipeline import ReupPipeline

st.set_page_config(page_title="Reup AI Tool", page_icon="🎬", layout="wide")

st.title("🎬 Tool Reup Video AI")
st.caption("Link → Text → Rewrite → Voice → Video → Upload")

with st.sidebar:
    st.header("⚙️ Cấu hình")
    voice_key = st.selectbox(
        "🎙️ Giọng nói",
        list(VOICES.keys()),
        index=list(VOICES.keys()).index("adam_vi"),
    )
    auto_upload = st.checkbox("📤 Tự động đăng TikTok", value=False)
    visibility = st.selectbox("Chế độ", ["public", "private", "friends"])
    st.divider()
    st.caption(f"Model: {CONFIG['api']['default_model']}")

tab1, tab2, tab3 = st.tabs(["🚀 Reup tự động", "🎙️ TTS", "🎬 Tạo video"])

with tab1:
    url = st.text_input("🔗 Nhập link video")
    if st.button("🚀 Bắt đầu", type="primary", use_container_width=True):
        if not url:
            st.error("Vui lòng nhập link!")
        else:
            with st.status("Đang xử lý...", expanded=True) as status:
                pipeline = ReupPipeline(CONFIG)
                try:
                    result = pipeline.run(url, voice_key=voice_key,
                                          auto_upload=auto_upload,
                                          visibility=visibility)
                    if result["success"]:
                        status.update(label="✅ Hoàn tất!", state="complete")
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            st.subheader("📹 Video")
                            vp = result.get("video_path")
                            if vp and os.path.exists(vp):
                                st.video(vp)
                                with open(vp, "rb") as f:
                                    st.download_button(
                                        "⬇️ Tải video", f,
                                        file_name=Path(vp).name,
                                        mime="video/mp4",
                                    )
                        with col2:
                            st.subheader("📝 Thông tin")
                            st.write(f"**Tiêu đề:** {result.get('title')}")
                            st.write(f"**Hashtag:** {' '.join(result.get('hashtags', []))}")
                            with st.expander("📄 Transcript"):
                                st.write(result.get("transcript"))
                            with st.expander("✍️ Bản rewrite"):
                                st.write(result.get("rewritten"))
                    else:
                        status.update(label="❌ Lỗi", state="error")
                        st.error("Xử lý thất bại!")
                except Exception as e:
                    status.update(label="❌ Lỗi", state="error")
                    st.exception(e)

with tab2:
    text = st.text_area("📝 Văn bản", height=200)
    voice2 = st.selectbox("🎙️ Giọng", list(VOICES.keys()), key="tts_voice")
    rate = st.slider("Tốc độ (%)", -50, 50, 0, 5)
    if st.button("🎙️ Tạo giọng nói", use_container_width=True):
        if text:
            try:
                tts = TTSEngine(CONFIG["paths"]["audio"])
                out = tts.text_to_speech(text, voice_key=voice2,
                                         rate=f"{rate:+d}%")
                st.success("Đã tạo xong!")
                st.audio(out)
                with open(out, "rb") as f:
                    st.download_button("⬇️ Tải MP3", f,
                                       file_name=Path(out).name,
                                       mime="audio/mpeg")
            except Exception as e:
                st.exception(e)

with tab3:
    prompt = st.text_area("📝 Nội dung/prompt", height=200)
    use_ai = st.checkbox("🤖 AI viết lại", value=True)
    voice3 = st.selectbox("🎙️ Giọng", list(VOICES.keys()), key="vid_voice")
    if st.button("🎬 Tạo video", use_container_width=True):
        if prompt:
            with st.spinner("Đang tạo..."):
                try:
                    if use_ai:
                        from rewriter import ContentRewriter
                        rw = ContentRewriter(
                            CONFIG["api"]["base_url"],
                            CONFIG["api"]["api_key"],
                            CONFIG["api"]["default_model"],
                        )
                        prompt = rw.rewrite(prompt)

                    tts = TTSEngine(CONFIG["paths"]["audio"])
                    audio = tts.text_to_speech(prompt, voice_key=voice3)

                    from video_maker import VideoMaker
                    maker = VideoMaker(CONFIG)
                    video = maker.create_video(prompt, audio)

                    st.success("Đã tạo video!")
                    st.video(video)
                    with open(video, "rb") as f:
                        st.download_button("⬇️ Tải video", f,
                                           file_name=Path(video).name,
                                           mime="video/mp4")
                except Exception as e:
                    st.exception(e)
