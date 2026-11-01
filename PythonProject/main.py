import re
import webbrowser
import subprocess
from datetime import datetime
from urllib.parse import quote_plus

import speech_recognition as sr
import pyttsx3
from google import genai
from google.genai import types
from google.genai import errors

from config import apikey

# ================= SETTINGS =================

USER_NAME = "Raksham"
MODEL = "gemini-3-flash-preview"

client = genai.Client(api_key=apikey)

INSTRUCTIONS = f"""
You are RAXAM AI, a helpful personal assistant for {USER_NAME}.
Answer general questions, explain topics, and write complete letters.
Remember conversation context and answer follow-up questions.
Respond in Hindi when the user speaks Hindi.
Keep ordinary answers concise and natural for speech.
Use the name Raksham in letters. Do not invent missing details.
Avoid unnecessary markdown and decorative symbols.
"""

chat = client.chats.create(
    model=MODEL,
    config=types.GenerateContentConfig(
        system_instruction=INSTRUCTIONS,
        temperature=0.7,
    ),
)

# ================= VOICE =================

engine = pyttsx3.init("sapi5")
engine.setProperty("rate", 145)
engine.setProperty("volume", 1.0)

voices = engine.getProperty("voices")
if voices:
    engine.setProperty("voice", voices[0].id)

recognizer = sr.Recognizer()
recognizer.pause_threshold = 1.0
recognizer.dynamic_energy_threshold = True


def speak(text):
    """Print and speak the same complete response."""
    if not text:
        return

    text = str(text).strip()
    print(f"\nRAXAM AI: {text}\n")

    # Remove basic markdown for clearer speech.
    spoken = re.sub(r"```.*?```", "Code omitted.", text, flags=re.S)
    spoken = re.sub(r"`([^`]*)`", r"\1", spoken)
    spoken = re.sub(r"\*\*(.*?)\*\*", r"\1", spoken)
    spoken = re.sub(r"(?m)^#{1,6}\s*", "", spoken)

    try:
        engine.stop()
        engine.setProperty("rate", 145)
        engine.setProperty("volume", 1.0)
        engine.say(spoken)
        engine.runAndWait()
    except Exception as exc:
        print("Voice output error:", exc)


# ================= LISTEN =================

def listen():
    try:
        with sr.Microphone() as source:
            print("Listening... Speak your question.")
            audio = recognizer.listen(
                source, timeout=10, phrase_time_limit=20
            )

        print("Recognizing your question...")

        try:
            question = recognizer.recognize_google(
                audio, language="en-IN"
            )
        except sr.UnknownValueError:
            print("I couldn't understand that. Please try again.")
            return ""

        question = question.strip()
        if question:
            print(f"\n{USER_NAME}: {question}\n")
        return question

    except sr.WaitTimeoutError:
        print("No speech detected. Waiting again...")
        return ""
    except sr.RequestError:
        speak("Sorry, sir. Speech recognition needs an internet connection.")
        return ""
    except Exception as exc:
        print("Microphone error:", exc)
        speak("Sorry, sir. I could not access the microphone.")
        return ""


# ================= GEMINI CHAT =================

def ask_ai(question):
    try:
        response = chat.send_message(question)
        answer = response.text

        if answer and answer.strip():
            speak(answer)
        else:
            speak("Sorry, sir. I could not generate an answer.")

    except errors.APIError as exc:
        error_text = str(exc)
        print("Gemini API error:", error_text)

        if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
            speak(
                "Sorry, sir. My Gemini daily request limit has been reached. "
                "Please wait until the limit resets, or check your available "
                "quota in Google AI Studio."
            )
        else:
            speak(
                "Sorry, sir. I could not reach the AI service. "
                "Please try again later."
            )

    except Exception as exc:
        print("AI error:", exc)
        speak("Sorry, sir. Something went wrong while answering.")


# ================= WEBSITES =================

def open_website(command):
    websites = {
        "open youtube": ("https://www.youtube.com", "YouTube"),
        "youtube": ("https://www.youtube.com", "YouTube"),
        "open google": ("https://www.google.com", "Google"),
        "open chatgpt": ("https://chatgpt.com", "ChatGPT"),
        "open gmail": ("https://mail.google.com", "Gmail"),
        "open github": ("https://github.com", "GitHub"),
        "open wikipedia": ("https://www.wikipedia.org", "Wikipedia"),
        "open my college website": ("https://liet.in/", "your college website"),
        "open college website": ("https://liet.in/", "your college website"),
        "open liet": ("https://liet.in/", "your college website"),
    }

    if command in websites:
        url, name = websites[command]
        speak(f"Opening {name}, sir.")
        webbrowser.open(url)
        return True

    prefix = "search wikipedia for "
    if command.startswith(prefix):
        topic = command[len(prefix):].strip()
        if topic:
            url = "https://en.wikipedia.org/w/index.php?search=" + quote_plus(topic)
            speak(f"Searching Wikipedia for {topic}, sir.")
            webbrowser.open(url)
        return True

    if command.endswith(" wikipedia"):
        topic = command[:-len(" wikipedia")].strip()
        if topic:
            url = "https://en.wikipedia.org/w/index.php?search=" + quote_plus(topic)
            speak(f"Searching Wikipedia for {topic}, sir.")
            webbrowser.open(url)
        return True

    prefixes = [
        "play music on youtube ",
        "play a song on youtube ",
        "play song on youtube ",
        "search youtube for ",
        "search youtube ",
        "find on youtube ",
        "play on youtube ",
        "play music ",
        "play a song ",
        "play song ",
        "play ",
    ]

    for prefix in prefixes:
        if command.startswith(prefix):
            query = command[len(prefix):].strip()
            if query:
                url = "https://www.youtube.com/results?search_query=" + quote_plus(query)
                speak(f"Searching YouTube for {query}, sir.")
                webbrowser.open(url)
            else:
                speak("What would you like to play, sir?")
                webbrowser.open("https://www.youtube.com")
            return True

    return False


# ================= WINDOWS APPS =================

def open_application(command):
    apps = {
        "open notepad": ("notepad.exe", "Notepad"),
        "open calculator": ("calc.exe", "Calculator"),
        "open calculator app": ("calc.exe", "Calculator"),
        "open file explorer": ("explorer.exe", "File Explorer"),
        "open explorer": ("explorer.exe", "File Explorer"),
    }

    if command not in apps:
        return False

    program, name = apps[command]
    try:
        speak(f"Opening {name}, sir.")
        subprocess.Popen(program)
    except Exception as exc:
        print("Application error:", exc)
        speak(f"Sorry, sir. I could not open {name}.")
    return True


# ================= COMMANDS =================

def process_command(question):
    global chat

    if not question:
        return True

    command = question.lower().strip().rstrip(".!?")

    if command in {
        "exit", "quit", "close now", "close raxam",
        "close raxam ai", "stop raxam", "stop raxam ai",
        "exit raxam ai", "bye", "goodbye", "bye bye",
    }:
        speak("Goodbye, sir! Thank you for using RAXAM AI. Have a wonderful day!")
        return False

    if command in {
        "reset conversation", "clear conversation",
        "start a new conversation",
    }:
        chat = client.chats.create(
            model=MODEL,
            config=types.GenerateContentConfig(
                system_instruction=INSTRUCTIONS,
                temperature=0.7,
            ),
        )
        speak("Our conversation has been reset, sir.")
        return True

    if command in {"what time is it", "tell me the time", "current time"}:
        speak("Sir, the current time is " + datetime.now().strftime("%I:%M %p"))
        return True

    if command in {"what is the date", "what is today's date", "tell me the date"}:
        speak("Sir, today's date is " + datetime.now().strftime("%A, %d %B %Y"))
        return True

    if open_website(command):
        return True

    if open_application(command):
        return True

    ask_ai(question)
    return True


# ================= MAIN =================

def main():
    print("=" * 45)
    print("          RAXAM AI ASSISTANT")
    print("       Your Personal Desktop AI")
    print("=" * 45)

    speak("Hello Raksham sir! RAXAM AI is ready. Ask me anything.")

    try:
        while True:
            question = listen()
            if question and not process_command(question):
                break
    except KeyboardInterrupt:
        speak("Goodbye, sir! Thank you for using RAXAM AI.")
    finally:
        engine.stop()
        print("\nRAXAM AI has shut down.")


if __name__ == "__main__":
    main()
