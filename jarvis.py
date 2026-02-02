import requests
import speech_recognition as sr
import pyttsx3
import os
import webbrowser

# ---------- SES MOTORU ----------
engine = pyttsx3.init()
engine.setProperty('rate', 170)

# Türkçe ses bulmaya çalış
for voice in engine.getProperty('voices'):
    if "zira" in voice.name.lower() or "turkish" in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break

def speak(text):
    print("Jarvis:", text)
    chunks = [text[i:i+120] for i in range(0, len(text), 120)]
    for chunk in chunks:
        engine.say(chunk)
        engine.runAndWait()

# ---------- YAPAY ZEKA (OLLAMA) ----------
def ask_llama(prompt):
    system_rules = """
    Sen Türkçe konuşan bir yapay zeka asistanısın.
    ASLA İngilizce cevap verme.
    Cevapların kısa, net ve günlük Türkçe olsun.
    """

    full_prompt = system_rules + "\nKullanıcı: " + prompt + "\nAsistan:"

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": full_prompt,
            "stream": False,
            "options": {"temperature": 0.4}
        }
    )

    text = response.json()["response"].strip()

    # İngilizce kaçarsa Türkçeye çevirt
    if any(word in text.lower() for word in ["the ", "is ", "are ", "and ", "you "]):
        translate_prompt = f"Şunu doğal Türkçeye çevir:\n{text}"
        tr_response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3", "prompt": translate_prompt, "stream": False}
        )
        text = tr_response.json()["response"].strip()

    return text[:500]

# ---------- KOMUTLAR ----------
def run_command(text):
    text = text.lower()

    if "youtube aç" in text:
        speak("YouTube açılıyor")
        webbrowser.open("https://youtube.com")

    elif "spotify aç" in text:
        speak("Spotify açılıyor")
        os.system("start spotify")

    elif "belgeler klasörünü aç" in text:
        speak("Belgeler açılıyor")
        os.startfile(os.path.expanduser("~/Documents"))

    elif "bilgisayarı kapat" in text:
        speak("Bilgisayarı kapatmamı onaylıyor musun?")
        return "shutdown_confirm"

    else:
        return "ai"

# ---------- MİKROFON ----------
recognizer = sr.Recognizer()

def listen():
    with sr.Microphone() as source:
        print("Dinliyorum...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source, timeout=10, phrase_time_limit=12)

    try:
        text = recognizer.recognize_google(audio, language="tr-TR")
        print("Sen:", text)
        return text.lower()
    except sr.WaitTimeoutError:
        speak("Seni duyamadım")
        return ""
    except sr.UnknownValueError:
        speak("Anlayamadım, tekrar eder misin?")
        return ""
    except Exception as e:
        print("Hata:", e)
        speak("Bir hata oluştu")
        return ""

# ---------- ANA DÖNGÜ ----------
speak("Jarvis başlatıldı. Seni dinliyorum.")

while True:
    command = listen()

    if command == "":
        continue

    result = run_command(command)

    if result == "shutdown_confirm":
        confirm = listen()
        if "evet" in confirm:
            speak("Bilgisayar kapatılıyor")
            os.system("shutdown /s /t 5")
        else:
            speak("İptal edildi")

    elif result == "ai":
        answer = ask_llama(command)
        speak(answer)
