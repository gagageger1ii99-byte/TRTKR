import sys
import os
import json
import yt_dlp
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def download_video(url):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'downloaded_video.%(ext)s',
        'merge_output_format': 'mp4',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        base, _ = os.path.splitext(filename)
        final_file = f"{base}.mp4"
        return final_file if os.path.exists(final_file) else filename

def upload_to_youtube(video_path, title, description):
    creds_json = os.environ.get('YOUTUBE_CREDENTIALS')
    if not creds_json:
        raise Exception("YOUTUBE_CREDENTIALS Secret is missing!")
        
    creds_data = json.loads(creds_json)
    creds = Credentials.from_authorized_user_info(creds_data)
    
    youtube = build('youtube', 'v3', credentials=creds)
    
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'categoryId': '20' # Gaming Category
        },
        'status': {
            'privacyStatus': 'public' # يمكنك تغييرها إلى 'unlisted' أو 'private'
        }
    }
    
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part='snippet,status',
        body=body,
        media_body=media
    )
    
    response = None
    print("Uploading to YouTube...")
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded: {int(status.progress() * 100)}%")
            
    print(f"✅ Upload Complete! Video ID: {response.get('id')}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python process.py <URL> <TITLE> <DESCRIPTION>")
        sys.exit(1)
        
    video_url = sys.argv[1]
    title = sys.argv[2]
    description = sys.argv[3]
    
    print(f"▶ Processing URL: {video_url}")
    downloaded_file = download_video(video_url)
    
    print(f"▶ Uploading Video: {title}")
    upload_to_youtube(downloaded_file, title, description)

