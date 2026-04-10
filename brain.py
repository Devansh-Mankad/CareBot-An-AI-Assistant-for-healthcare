import os
import speech_recognition as sr
import pyttsx3
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# 🛡️ CLOUD FIX: Try to initialize audio, but don't crash if it fails (like on Render)
try:
    engine = pyttsx3.init()
    engine.setProperty('rate', 160)
    HAS_AUDIO = True
except Exception:
    print("Running in Headless/Cloud Mode (No Audio Hardware)")
    HAS_AUDIO = False

def speak_text(text):
    """Converts AI text to audible speech only if hardware exists."""
    if HAS_AUDIO and engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except:
            pass
    else:
        print(f"Speech skipped (Cloud Mode): {text}")

def listen_to_user():
    """Captures audio if microphone exists, otherwise returns None."""
    if not HAS_AUDIO:
        return None
        
    recognizer = sr.Recognizer()
    try:
        # This will fail on Render/Cloud because there is no 'Microphone()'
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
            text = recognizer.recognize_google(audio)
            return text
    except Exception:
        return None

# --- REST OF YOUR CODE (SYSTEM_RULES, get_carebot_response, etc.) REMAINS THE SAME ---

SYSTEM_RULES = """
You are CareBot, a specialized medical diagnostic assistant...
"""

def get_carebot_response(user_query, chat_history):
    # (Keep your existing get_carebot_response logic here)
    try:
        gemini_history = []
        for msg in chat_history[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))

        chat = client.chats.create(
            model="gemini-2.0-flash", # Note: Check if you meant 2.0 or 2.5
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_RULES,
                temperature=0.7
            ),
            history=gemini_history
        )
        
        response = chat.send_message(user_query)
        return response.text
    except Exception as e:
        return f"System Error: {str(e)}"

def summarize_symptoms(chat_history):
    # (Keep your existing summarize_symptoms logic here)
    if not chat_history:
        return "Waiting for details..."
    user_text = " ".join([m["content"] for m in chat_history if m["role"] == "user"])
    prompt = f"List the medical symptoms mentioned in this text as a brief bulleted list: {user_text}"
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        return response.text
    except:
        return "Gathering symptoms..."