import json


def get_audio_input(q, rec):
    print("Speak now (say 'exit' or 'quit' to stop)...")
    while True:
        data = q.get()
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result()).get("text", "")
            if result:
                print("\nYou said:", result)
                return result