import streamlit as st
import yt_dlp
import os
import re

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

def get_available_languages(video_url):
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(video_url, download=False)
            subs = info.get("subtitles", {})
            auto_subs = info.get("automatic_captions", {})
            combined = {**subs, **auto_subs}
            return combined, info.get('title', 'video')
    except Exception as e:
        return None, None

def download_subtitle(video_url, language_code):
    output_template = "subtitle_temp.%(ext)s"
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': [language_code],
        'subtitlesformat': 'srt',
        'outtmpl': output_template,
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            video_title = sanitize_filename(info.get('title', 'video'))
            subtitle_file = "subtitle_temp.srt"
            if os.path.exists(subtitle_file):
                with open(subtitle_file, "r", encoding="utf-8") as f:
                    subtitles = f.read()
                final_path = f"{video_title}_{language_code}.srt"
                os.rename(subtitle_file, final_path)
                return video_title, subtitles, final_path
            else:
                return None, None, None
    except Exception as e:
        return None, str(e), None

# Streamlit UI
st.set_page_config(page_title="YouTube Subtitle Downloader", layout="centered")
st.title("🎬 YouTube Subtitle Downloader")
st.markdown("Tự động phát hiện phụ đề và cho phép chọn ngôn ngữ để tải (.srt)")

video_url = st.text_input("🔗 Dán link YouTube vào đây:")

if video_url:
    langs, title = get_available_languages(video_url)
    if langs:
        lang_codes = list(langs.keys())
        lang_names = [f"{code} – {langs[code][0]['ext'].upper()}" for code in lang_codes]
        lang_dict = dict(zip(lang_names, lang_codes))
        selected_lang = st.selectbox("🌍 Chọn ngôn ngữ phụ đề:", options=lang_names)

        if st.button("📥 Tải phụ đề"):
            with st.spinner("Đang tải phụ đề..."):
                code = lang_dict[selected_lang]
                title, content, file_path = download_subtitle(video_url, code)
                if content and file_path:
                    st.success(f"✅ Đã lấy phụ đề: {selected_lang}")
                    st.text_area("📄 Nội dung phụ đề:", content, height=300)
                    with open(file_path, "rb") as f:
                        st.download_button("📄 Tải về file .srt", f, file_name=file_path, mime="text/plain")
                    os.remove(file_path)
                else:
                    st.error(f"⚠ Lỗi khi tải phụ đề.")
    else:
        st.warning("❌ Không tìm thấy phụ đề nào cho video này.")
