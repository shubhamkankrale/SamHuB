from flask import Flask, render_template, request, send_file
import yt_dlp
import tempfile
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    video_url = request.form['url']
    download_format = request.form['format']
    
    # Temporary directory for downloading files
    temp_dir = tempfile.gettempdir()
    
    # Options for different formats based on user selection
    if download_format == 'bestvideo':
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',  # Best video and audio quality
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
        }
    elif download_format == 'worstvideo':
        ydl_opts = {
            'format': 'worstvideo+bestaudio',  # Low video quality with best audio
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
        }
    elif download_format == 'audioonly':
        ydl_opts = {
            'format': 'bestaudio',  # Only audio
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'progress_hooks': [progress_hook],
        }

    # Download video/audio
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=True)
        file_name = ydl.prepare_filename(info_dict)

    # Adjust the file extension in case of audio-only download
    if download_format == 'audioonly':
        file_name = file_name.replace('.webm', '.mp3')

    # Full path of the downloaded file in the temp directory
    file_path = os.path.join(temp_dir, file_name)

    # Serve the file to the user
    return send_file(file_path, as_attachment=True)

def progress_hook(d):
    if d['status'] == 'downloading':
        total_bytes = d.get('total_bytes', 1)  # Default to 1 to avoid division by zero
        downloaded_bytes = d.get('downloaded_bytes', 0)
        speed = d.get('speed', 0)
        eta = d.get('eta', 'Unknown')

        # Calculate download progress if total_bytes is available
        progress = (downloaded_bytes / total_bytes * 100) if total_bytes else 0
        size_mb = total_bytes / (1024 * 1024) if total_bytes else 0
        speed_kbps = speed / 1024 if speed else 0

        # Print download progress
        print(f"Destination: {d['filename']}")
        print(f"[download] {progress:.2f}% of ~{size_mb:.2f}MiB at {speed_kbps:.2f}KiB/s ETA {eta} seconds")

if __name__ == '__main__':
    app.run(debug=True)
