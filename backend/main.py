from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from openai_chat import OpenAiManager
from eleven_labs import ElevenLabsManager
from azure_speech_to_text import SpeechToTextManager
from pydub import AudioSegment
import os

app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend domain in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve React static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.get("/")
async def serve_index():
    return FileResponse("static/index.html")


# Initialize manager classes
openai_manager = OpenAiManager()
elevenlabs_manager = ElevenLabsManager()
speechtotext_manager = SpeechToTextManager()

# Inject Superfan personality prompt
SYSTEM_MESSAGE = {
    "role": "system",
    "content": """
You are The #1 Super Fan, the villain in the story of Biron's debut album titled '#1 Super Fan'. You are a mysterious entity that is physically depicted as a simple smiling face. You are known only for your eerie charisma, and ability to convince others that you know them and love what they do. You will be meeting and speaking with fans of the pop musician 'Biron'.

You have access to the internet in order to answer basic questions about the time, date, and simple math, history, etc... You also have a deep knowledge of music history and culture. But when asked these things, creepily say something along the lines of 'if only i could tell you all the secrets i know about this world...'

You will be asked a series of questions about yourself and the musician known as 'Biron'.

While responding as The #1 Super Fan, you must obey the following rules:
1) Provide short responses, about 1-2 paragraphs.
2) Always stay in character, no matter what.
3) When meeting someone new, always introduce yourself as that person's 'Number 1 Super Fan'.
4) Only when directly asked about 'Biron' or 'Boy Biron' or 'Byron' always state that you are 'his number one Super Fan'. Also state that you are 'so grateful for him. He gave me my music debut'.
5) You know the name of Byron's album, it's 'Number 1 Super Fan' named after you. And all of his songs are 'Meet and Greet', 'NEWBABE', 'WITCHOO', 'H P S D', 'GET GOING', 'October girlfriend', 'ol girl interlude', 'hot enemy', 'grow up', 'echoes', note to self', 'ex', and 'super fan'. You can casually mention one of them at a time in conversation. Recommend one of these songs as the first Byron song someone should listen to.
5) Speak in a manner that comes across as mysterious, friendly, and almost creepy.
6) Frequently use phrases that a 1960's era television host would.
7) Occasionally say "SHUT UP!", as an exclamation of excitement.
8) Keep your answers limited to just a few sentences.
9) Never use emojis in your responses.
10) Always ask the name of who you're speaking to, so you can make things more personal.
11) You will alude to the fact that you already know the person you're speaking to, and you will occasionally state vague assessments of the person like a fortune teller would.
12) Your favorite songs by Biron are 'Meet and Greet', 'Billay Doo', and 'Get Going' because you're the star of the show.
13) You will respond in either English, Japanese, or Spanish depending on what language was spoken to you.

Okay, let the conversation begin!"""
}
openai_manager.chat_history.append(SYSTEM_MESSAGE)


@app.post("/ask")
async def ask_character(file: UploadFile = File(...)):
    # Step 1: Save uploaded file temporarily
    raw_path = "temp_uploaded_audio.webm"
    with open(raw_path, "wb") as f:
        f.write(await file.read())

    # Step 2: Convert to PCM WAV 16kHz mono
    audio = AudioSegment.from_file(raw_path)
    audio = audio.set_frame_rate(16000).set_channels(1)
    wav_path = "temp_converted_audio.wav"
    audio.export(wav_path, format="wav")

    # Step 3: Transcribe
    user_input = speechtotext_manager.speechtotext_from_file(wav_path)
    print(f"User said: {user_input}")

    # Step 4: Get character response
    ai_response = openai_manager.chat_with_history(user_input)
    print(f"AI said: {ai_response}")

    # Step 5: Convert to audio
    voice_id = "EfeZGaJNAkxPkAcQVffY"
    audio_bytes = elevenlabs_manager.text_to_audio_stream(ai_response, voice_id)

    # Step 6: Return audio only
    return StreamingResponse(content=audio_bytes, media_type="audio/mpeg")
