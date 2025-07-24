# downloaded model from https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
# pip install vosk sounddevice

import sounddevice as sd
import queue
import json
from vosk import Model, KaldiRecognizer

q = queue.Queue()

def callback(indata, frames, time, status):
    q.put(bytes(indata))

model = Model(r"C:\Users\vsgsa\Desktop\V\Projects\LocalAssistant\Local-LLM-assistant\voice\models\vosk-model-small-en-us-0.15")
rec = KaldiRecognizer(model, 16000)

with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                       channels=1, callback=callback):
    print("Say something...")
    while True:
        data = q.get()
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            print("You said:", result.get("text", ""))
