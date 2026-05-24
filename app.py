from flask import Flask, render_template, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    video_url = request.form.get('url')
    download_type = request.form.get('type')
    
    if not video_url:
        return jsonify({'error': 'Please provide a valid URL'}), 400

    # Smart TV/Android VR client emulator parameters (Bypasses "Sign in to confirm you're not a bot")
    ydl_opts = {
        'format': 'bestaudio/best' if download_type == 'audio' else 'best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        # Force system to use TV HTML5 and embedded clients (Zero bot verification check)
        'extractor_args': {
            'youtube': {
                'player_client': ['tvhtml5', 'android_embedded', 'ios'],
                'skip': ['webpage', 'authcheck']
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (SmartHub; SMART-TV; Windows; U; Windows NT 6.1; x64) AppleWebKit/537.4 (KHTML, like Gecko) SmartTV Safari/537.4',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            direct_url = info_dict.get('url')
            
            # Fallback format checking
            if not direct_url and 'formats' in info_dict:
                valid_formats = [f for f in info_dict['formats'] if f.get('url') and (f.get('acodec') != 'none' and f.get('vcodec') != 'none')]
                if not valid_formats:
                    valid_formats = [f for f in info_dict['formats'] if f.get('url')]
                if valid_formats:
                    direct_url = valid_formats[-1]['url']

            if not direct_url:
                return jsonify({'error': 'Unable to find proper stream URL. Try another video.'}), 500

            title = "".join([c for c in info_dict.get('title', 'video') if c.isalpha() or c.isdigit() or c==' ']).rstrip()
            ext = 'mp3' if download_type == 'audio' else 'mp4'
            
            return jsonify({
                'success': True,
                'download_url': direct_url,
                'filename': f"{title}.{ext}"
            })

    except Exception as e:
        # Emergency Flat Fallback Strategy
        try:
            flat_opts = {
                'quiet': True, 
                'extract_flat': True, 
                'extractor_args': {'youtube': {'player_client': ['tv']}}
            }
            with yt_dlp.YoutubeDL(flat_opts) as ydl_flat:
                info_flat = ydl_flat.extract_info(video_url, download=False)
                fallback_url = info_flat.get('url') or (info_flat.get('formats') and info_flat['formats'][0]['url'])
                if fallback_url:
                    return jsonify({
                        'success': True,
                        'download_url': fallback_url,
                        'filename': "video.mp4"
                    })
        except:
            pass
            
        return jsonify({'error': f"YouTube System Overload. Please paste a link from Facebook, TikTok or Instagram reels for instant high speed downloads."}), 500

application = app
