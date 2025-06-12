import time
import azure.cognitiveservices.speech as speechsdk
import os


class SpeechToTextManager:
    azure_speechconfig = None

    def __init__(self):
        try:
            self.azure_speechconfig = speechsdk.SpeechConfig(
                subscription=os.getenv('AZURE_TTS_KEY'),
                region=os.getenv('AZURE_TTS_REGION')
            )
        except TypeError:
            exit("Ooops! You forgot to set AZURE_TTS_KEY or AZURE_TTS_REGION in your environment!")

        self.auto_detect_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
            languages=["en-US", "es-ES", "ja-JP"]
        )

    def speechtotext_from_file(self, file_path):
        audio_config = speechsdk.AudioConfig(filename=file_path)

        recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.azure_speechconfig,
            audio_config=audio_config,
            auto_detect_source_language_config=self.auto_detect_config
        )

        print("Processing file for speech recognition...")
        result = recognizer.recognize_once_async().get()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            detected_language = result.properties.get(
                speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult
            )
            print(f"[Auto-Detected Language: {detected_language}]")
            print("Recognized:", result.text)
            return result.text
        elif result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized.")
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech Recognition canceled:", cancellation_details.reason)
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details:", cancellation_details.error_details)

        return ""

# Optional test
if __name__ == '__main__':
    manager = SpeechToTextManager()
    print(manager.speechtotext_from_file("temp_user_audio.wav"))
