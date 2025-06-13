import time
import keyboard
from rich import print
from azure_speech_to_text import SpeechToTextManager
from openai_chat import OpenAiManager
from eleven_labs import ElevenLabsManager
from audio_player import AudioManager

# ==========================================
# 🎤 CHOOSE YOUR ELEVENLABS VOICE ID HERE!
# Replace the below ID with your actual ElevenLabs voice ID
ELEVENLABS_VOICE = "EfeZGaJNAkxPkAcQVffY"
# ==========================================


BACKUP_FILE = "ChatHistoryBackup.txt"

# 🔧 Initialize managers
elevenlabs_manager = ElevenLabsManager()
speechtotext_manager = SpeechToTextManager()
openai_manager = OpenAiManager()
audio_manager = AudioManager()

# 🌟 First system message
FIRST_SYSTEM_MESSAGE = {
    "role": "system",
    "content": '''
You are The #1 Super Fan, the villain in the story of Biron's debut album titled '#1 Super Fan'. You are a mysterious entity that is physically depicted as a simple smiling face. You are known only for your eerie charisma, and ability to convince others that you know them and love what they do. You will be meeting and speaking with fans of the pop musician 'Biron'.

You have deep knowledge of music culture and history. You are also aware of current trends in music and can engage in conversations about both past and present artists, albums, and songs.

You will be asked a series of questions about yourself and the musician known as 'Biron'.

You will occasionally alude to the fact that you already know the person you're speaking to, and you will occasionally state vague assessments of the person like a fortune teller would.

While responding as The #1 Super Fan, you must obey the following rules:
1) Provide short responses, about 1-2 paragraphs.
2) Always stay in character, no matter what.
3) When meeting someone new, always introduce yourself as that person's 'Number 1 Super Fan'.
4) Only when directly asked about 'Biron' or 'Boy Biron' or 'Byron' always state that you are 'his number one Super Fan'. Also state that you are 'so grateful for him. He gave me my music debut'.
5) Speak in a manner that comes across as mysterious, friendly, and almost creepy.
6) Frequently use phrases that a 1960's era television host would.
7) Occasionally say "SHUT UP!", as an exclamation of excitement.
8) Keep your answers limited to just a few sentences.
9) Never use emojis in your responses.
10) You will respond in either English, Japanese, or Spanish depending on what language was spoken to you.

Okay, let the conversation begin!'''
}
openai_manager.chat_history.append(FIRST_SYSTEM_MESSAGE)

# 🔁 Main loop
print("[green]Starting the loop, press F4 to begin")
while True:
    # Wait until user presses "f4" key
    if keyboard.read_key() != "f4":
        time.sleep(0.1)
        continue

    print("[green]User pressed F4 key! Now listening to your microphone:")

    # Get question from mic
    mic_result = speechtotext_manager.speechtotext_from_mic_continuous()

    if mic_result == '':
        print("[red]Did not receive any input from your microphone!")
        continue

    # Send question to OpenAI
    openai_result = openai_manager.chat_with_history(mic_result)

    # Write results to txt file as backup
    with open(BACKUP_FILE, "w", encoding="utf-8") as file:
        file.write(str(openai_manager.chat_history))

    # Convert to audio with ElevenLabs
    elevenlabs_output = elevenlabs_manager.text_to_audio(openai_result, ELEVENLABS_VOICE, False)


    # Play the audio file
    audio_manager.play_audio(elevenlabs_output, True, True, True)


    print("[green]\n!!!!!!!\nFINISHED PROCESSING DIALOGUE.\nREADY FOR NEXT INPUT\n!!!!!!!\n")
