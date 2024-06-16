import os
from flask import Flask, request, render_template
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Configure the generative AI with the API key
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Flask app
app = Flask(__name__)

# Initialize YouTube API client
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Search route
@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    search_response = youtube.search().list(
        q=query,
        part='id,snippet',
        maxResults=10
    ).execute()

    videos = []
    for item in search_response.get('items', []):
        if item['id']['kind'] == 'youtube#video':
            videos.append({
                'title': item['snippet']['title'],
                'videoId': item['id']['videoId']
            })
    
    return render_template('results.html', videos=videos)

# Get transcript and summarize route
@app.route('/summarize', methods=['POST'])
def summarize():
    video_id = request.form['videoId']

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([entry['text'] for entry in transcript])
    except Exception as e:
        return f"Error fetching transcript: {e}"

    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        system_instruction="Summarize the video as I shared its transcript in points",
    )

    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": ["hi"],
            },
            {
                "role": "model",
                "parts": [
                    "Please share the transcript of the video you want me to summarize. I'm ready to help! \n",
                ],
            },
        ]
    )

    response = chat_session.send_message(transcript_text)

    return render_template('summary.html', summary=response.text)

if __name__ == '__main__':
    app.run(debug=True)
