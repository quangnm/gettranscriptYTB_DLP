import streamlit as st
import yt_dlp
import os
import re

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

def download_any_subtitles(video_url):
    output_template = "subtitle_temp.%(ext)s"

    # Gọi yt-dlp để lấy info trước
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        try:
            info = ydl.extract_info(video_url, download=False)
        except Exception as e:
            return None, f"Lỗi không lấy được info video: {e}", None

    subtitles = info.get("subtitles", {})
    automatic_captions = info.get("automatic_captions", {})

    # Ưu tiên subtitles chính thức > auto captions
    available_subs = subtitles if subtitles else automatic_captions

    if not available_subs:
        return None, "Video không có phụ đề nào cả.", None

    # Lấy ngôn ngữ đầu tiên có trong danh sách
    selected_lang = list(available_subs.keys())[0]

    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': [selected_lang],
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
                return None, "Tải phụ đề thất bại.", None
        except Exception as e:
            return None, f"Lỗi khi tải phụ đề: {e}", None

# Streamlit UI
st.set_page_config(page_title="YouTube Subtitle Downloader", layout="centered")
st.title("🎬 YouTube Subtitle Downloader")
st.markdown("Tự động phát hiện và tải phụ đề có sẵn từ video YouTube (.srt)")

video_url = st.text_input("🔗 Dán link YouTube vào đây:")

if st.button("📥 Tải phụ đề"):
    if not video_url.strip():
        st.warning("Vui lòng dán link trước khi bấm.")
    else:
        with st.spinner("Đang xử lý..."):
            title, content, file_path = download_any_subtitles(video_url)
            if content and file_path:
                st.success(f"✅ Đã lấy phụ đề cho: *{title}*")
                st.text_area("📄 Nội dung phụ đề:", content, height=300)
                with open(file_path, "rb") as f:
                    st.download_button("📄 Tải về file .srt", f, file_name=file_path, mime="text/plain")
                os.remove(file_path)
            else:
                st.error(f"⚠ {content or 'Không tìm thấy phụ đề.'}
