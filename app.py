from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import yt_dlp
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    try:
        video_url = request.form['url']
        download_quality = request.form['format']  # 'best', 'worst', or 'audioonly'

        ydl_opts = {
            'cookiefile': 'cookies.txt',  # Pass cookies to authenticate requests
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'postprocessors': [{'key': 'FFmpegMetadata'}],
        }



        if download_quality == 'audioonly':
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'].append({
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            })
        elif download_quality == 'best':
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
            ydl_opts['merge_output_format'] = 'mp4'
        elif download_quality == 'worst':
            ydl_opts['format'] = 'worst'  # Downloads the worst quality available

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            file_name = ydl.prepare_filename(info_dict)

        # Adjust the file name if audio-only
        if download_quality == 'audioonly':
            file_name = file_name.replace('.webm', '.mp3')

        return send_file(file_name, as_attachment=True)

    except Exception as e:
        flash(f"Error: {str(e)}")
        return redirect(url_for('index'))

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
