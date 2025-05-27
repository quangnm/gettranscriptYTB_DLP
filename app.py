import streamlit as st
import yt_dlp
import os
import re

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

def download_subtitles(video_url):
    output_template = "subtitle_temp.%(ext)s"
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en'],
        'subtitlesformat': 'srt',
        'outtmpl': output_template,
        'quiet': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(video_url, download=True)
            video_title = sanitize_filename(info.get('title', 'video'))
            subtitle_file = "subtitle_temp.srt"
            if os.path.exists(subtitle_file):
                with open(subtitle_file, "r", encoding="utf-8") as f:
                    subtitles = f.read()
                os.rename(subtitle_file, f"{video_title}.srt")
                return video_title, subtitles, f"{video_title}.srt"
            else:
                return None, None, None
        except Exception as e:
            return None, str(e), None

st.set_page_config(page_title="YouTube Subtitle Downloader", layout="centered")

st.title("🎬 YouTube Subtitle Downloader")
st.markdown("Tải phụ đề tự động từ video YouTube (.srt)")

video_url = st.text_input("🔗 Dán link YouTube vào đây:")

if st.button("📥 Tải phụ đề"):
    if not video_url.strip():
        st.warning("Vui lòng dán link trước khi bấm.")
    else:
        with st.spinner("Đang xử lý..."):
            title, content, file_path = download_subtitles(video_url)
            if content and file_path:
                st.success(f"✅ Đã lấy phụ đề cho: *{title}*")
                st.text_area("📄 Nội dung phụ đề:", content, height=300)
                with open(file_path, "rb") as f:
                    st.download_button("📄 Tải về file .srt", f, file_name=file_path, mime="text/plain")
                os.remove(file_path)  # xóa sau khi hiển thị
            elif content is None:
                st.error("⚠ Không tìm thấy phụ đề.")
            else:
                st.error(f"Lỗi: {content}")
