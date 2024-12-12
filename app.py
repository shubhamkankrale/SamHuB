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
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'merge_output_format': 'mp4',
        }

        if download_quality == 'audioonly':
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        elif download_quality == 'bestvideo':
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
        elif download_quality == 'worstvideo':
            ydl_opts['format'] = 'worstvideo/worstaudio/worst'

        # Check available formats to handle errors gracefully
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)  # Extract without downloading
            formats = info_dict.get('formats', None)

            # Validate if the requested format exists
            if not formats:
                raise Exception("No formats available for the given video.")

            # Download the video
            info_dict = ydl.extract_info(video_url, download=True)
            file_name = ydl.prepare_filename(info_dict)

        # Adjust file name if audio-only
        if download_quality == 'audioonly':
            file_name = file_name.replace('.webm', '.mp3')

        return send_file(file_name, as_attachment=True)

    except yt_dlp.DownloadError as e:
        flash(f"Error: {str(e)}. Please try another video or format.")
        return redirect(url_for('index'))
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

@app.route('/about')
def aboutus():
    return render_template('about.html')

@app.route('/instagram')
def insta():
    return render_template('Instagram.html')

@app.route('/howtouse')
def howtouse():
    return render_template('howtouse.html')

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    app.run(debug=True)
