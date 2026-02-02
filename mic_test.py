import speech_recognition as sr

r = sr.Recognizer()

with sr.Microphone() as source:
    print("Bir şey söyle...")
    r.adjust_for_ambient_noise(source)
    audio = r.listen(source)

print("Çözümleniyor...")

try:
    text = r.recognize_google(audio, language="tr-TR")
    print("Algılanan:", text)
except Exception as e:
    print("Hata:", e)
