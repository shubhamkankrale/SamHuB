from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import yt_dlp
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

# Home route to render the index page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle video/audio download requests
@app.route('/download', methods=['POST'])
def download_video():
    try:
        video_url = request.form['url']
        download_format = request.form['format']

        # Configure download options based on the selected format
        ydl_opts = {
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'format': 'bestvideo+bestaudio/best' if download_format == 'bestvideo' else
                      'worstvideo+bestaudio' if download_format == 'worstvideo' else
                      'bestaudio',
        }

        if download_format == 'audioonly':
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        # Download the video/audio
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            file_name = ydl.prepare_filename(info_dict)

        # Adjust the file name if audio-only
        if download_format == 'audioonly':
            file_name = file_name.replace('.webm', '.mp3')

        return send_file(file_name, as_attachment=True)

    except Exception as e:
        flash(f"Error: {str(e)}")
        return redirect(url_for('index'))

# Clean up downloaded files after use
@app.route('/cleanup', methods=['GET'])
def cleanup():
    try:
        files = os.listdir('downloads')
        for file in files:
            os.remove(os.path.join('downloads', file))
        flash("Temporary files cleaned successfully!")
    except Exception as e:
        flash(f"Cleanup failed: {str(e)}")
    return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    app.run(debug=True)
