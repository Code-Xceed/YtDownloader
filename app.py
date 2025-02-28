from flask import Flask, render_template, request, send_file, after_this_request
import os
import yt_dlp

app = Flask(__name__)

# Folder to store downloaded videos
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        quality = request.form.get("quality")

        if url:
            try:
                # Set yt-dlp options with cookies
                ydl_opts = {
                    'format': quality,
                    'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
                    'cookiefile': 'youtube.com_cookies.txt',  # Uses Chrome cookies to avoid bot detection
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    file_path = ydl.prepare_filename(info)

                # Return the file for download
                @after_this_request
                def remove_file(response):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Error deleting file: {e}")
                    return response

                return send_file(file_path, as_attachment=True)

            except Exception as e:
                return f"An error occurred: {e}"

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
