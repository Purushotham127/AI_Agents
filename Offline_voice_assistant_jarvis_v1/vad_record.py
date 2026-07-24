import webrtcvad, pyaudio

vad = webrtcvad.Vad(2)
RATE = 16000
CHUNK = 480

pa = pyaudio.PyAudio()
stream = pa.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)

def record_speech():
    print("Listening...")
    frames = []
    silence = 0

    while True:
        data = stream.read(CHUNK)
        frames.append(data)

        if not vad.is_speech(data, RATE):
            silence += 1
        else:
            silence = 0

        if silence > 30:
            break

    return b''.join(frames)
