import os
from io import BytesIO
from elevenlabs import ElevenLabs
from rich import print

class ElevenLabsManager:
    def __init__(self):
        api_key = os.getenv('ELEVENLABS_API_KEY')
        if not api_key:
            exit("Ooops! You forgot to set ELEVENLABS_API_KEY in your environment!")

        # Initialize ElevenLabs client
        self.client = ElevenLabs(api_key=api_key)

        # Print available voices
        voices_client = self.client.voices
        available_voices = voices_client.get_all().voices
        print("Available voices:")
        for voice in available_voices:
            print(f" - {voice.name} (ID: {voice.voice_id})")

    def text_to_audio(self, input_text, voice="Default", save_as_wave=True, subdirectory=""):
        # Create audio data as a stream of bytes
        audio_stream = self.client.text_to_speech.convert(
            text=input_text,
            voice_id=voice
        )
        audio_data = b''.join(audio_stream)

        if save_as_wave:
            file_name = f"___Msg{str(hash(input_text))}.wav"
        else:
            file_name = f"___Msg{str(hash(input_text))}.mp3"

        tts_file = os.path.join(os.path.abspath(os.curdir), subdirectory, file_name)
        with open(tts_file, "wb") as f:
            f.write(audio_data)

        return tts_file

    def text_to_audio_stream(self, input_text, voice="Default"):
        """Return ElevenLabs audio response as an in-memory MP3 stream (for web response)."""
        audio_stream = self.client.text_to_speech.convert(
            text=input_text,
            voice_id=voice,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        audio_data = b''.join(audio_stream)
        return BytesIO(audio_data)

# Tests
if __name__ == '__main__':
    manager = ElevenLabsManager()
    file_path = manager.text_to_audio("This is a test message. SHUT UP! I'm alive!", voice="Default")
    print(f"Audio file saved at: {file_path}")
