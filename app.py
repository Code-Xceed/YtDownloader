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
        quality = request.form.get("quality")  # Get selected quality

        if url:
            try:
                # Define quality options
                quality_options = {
                    "best": "bestvideo+bestaudio/best",
                    "1080p": "bestvideo[height<=1080]+bestaudio/best",
                    "720p": "bestvideo[height<=720]+bestaudio/best",
                    "480p": "bestvideo[height<=480]+bestaudio/best",
                    "360p": "bestvideo[height<=360]+bestaudio/best",
                }
                selected_quality = quality_options.get(quality, "best")

                ydl_opts = {
                    'format': selected_quality,
                    'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    file_path = ydl.prepare_filename(info)

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

        else:
            return "Please provide a valid YouTube URL."

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
    port = int(os.environ.get("PORT", 5000))  # Use PORT from environment, default to 5000
    app.run(host="0.0.0.0", port=port, debug=False)  # Bind to 0.0.0.0 for public access
