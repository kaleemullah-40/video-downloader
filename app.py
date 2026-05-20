from flask import Flask, render_template, request, send_file, after_this_request
import yt_dlp
import os

app = Flask(__name__)

DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    video_url = request.form.get('url')
    download_type = request.form.get('type')  # 'video' or 'audio'
    quality = request.form.get('quality')      # 'best', '1080', '720', '480'
    
    if not video_url:
        return "Please provide a valid URL", 400

    # Base configuration
    ydl_opts = {
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }

    # Audio Settings
    if download_type == 'audio':
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    # Video Settings based on quality
    else:
        if quality == '1080':
            ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best'
        elif quality == '720':
            ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best'
        elif quality == '480':
            ydl_opts['format'] = 'bestvideo[height<=480]+bestaudio/best'
        else:
            ydl_opts['format'] = 'bestvideo+bestaudio/best'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info_dict)
            
            # Agar audio download kiya hai to extension .mp3 ho chuki hogi
            if download_type == 'audio':
                file_path = os.path.splitext(file_path)[0] + '.mp3'

        # File send karne ke baad server se delete karne ka tareeqa
        @after_this_request
        def remove_file(response):
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as error:
                app.logger.error(f"Error removing file: {error}")
            return response

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return f"Error: {str(e)}. (Make sure FFmpeg is installed for high-quality merges)", 500

if __name__ == '__main__':
    app.run(debug=True)
