from pathlib import Path
from vosk import Model, KaldiRecognizer


def get_voice_recognizer(model_name):
    script_path = Path(__file__).resolve()
    model = Model(str(script_path.parent / "models" / model_name))
    recognizer = KaldiRecognizer(model, 16000)
    print("Voice recognizer is loaded...")
    return recognizer