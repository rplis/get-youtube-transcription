import os
import subprocess
import traceback
from flask import Flask, request, jsonify
import yt_dlp as youtube_dl

app = Flask(__name__)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        print("Transcription request received")
        youtube_url = request.json['url']
        print(f"YouTube URL: {youtube_url}")
        
        # Check model file
        model_path = '/whisper.cpp/models/ggml-base.en.bin'
        print(f"Checking model file: {model_path}")
        if not os.path.exists(model_path):
            print(f"Model file not found. Contents of /whisper.cpp/models:")
            print(subprocess.run(['ls', '-l', '/whisper.cpp/models'], capture_output=True, text=True).stdout)
            raise Exception(f"Model file not found: {model_path}")
        print(f"Model file size: {os.path.getsize(model_path)} bytes")
        print(subprocess.run(['file', model_path], capture_output=True, text=True).stdout)
        print(subprocess.run(['md5sum', model_path], capture_output=True, text=True).stdout)
        
        # Download audio from YouTube
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
            }],
            'outtmpl': 'audio.%(ext)s'
        }
        print("Downloading audio from YouTube")
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        
        # Print file info
        print("Audio file info:")
        print(subprocess.run(['file', 'audio.wav'], capture_output=True, text=True).stdout)
        print(subprocess.run(['ls', '-l', 'audio.wav'], capture_output=True, text=True).stdout)
        
        # Transcribe audio using whisper.cpp
        whisper_command = [
            '/whisper.cpp/main',
            '-m', model_path,
            '-f', 'audio.wav',
            '-otxt'
        ]
        print("Running whisper command:", ' '.join(whisper_command))
        result = subprocess.run(whisper_command, capture_output=True, text=True)
        print("Whisper return code:", result.returncode)
        print("Whisper stdout:", result.stdout)
        print("Whisper stderr:", result.stderr)
        
        # Check for output file
        print("Checking for output file:")
        print(subprocess.run(['ls', '-l'], capture_output=True, text=True).stdout)
        
        if result.returncode != 0:
            raise Exception(f"Whisper command failed with return code {result.returncode}")
        
        # Read transcription
        output_file = 'audio.wav.txt'
        print(f"Reading transcription from {output_file}")
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                transcription = f.read()
            print("Transcription read successfully")
        else:
            raise Exception(f"Output file {output_file} not found")
        
        # Clean up
        print("Cleaning up files")
        if os.path.exists('audio.wav'):
            os.remove('audio.wav')
        if os.path.exists(output_file):
            os.remove(output_file)
        
        print("Transcription successful")
        return jsonify({'transcription': transcription})
    except Exception as e:
        print("Error:", str(e))
        print("Traceback:", traceback.format_exc())
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)