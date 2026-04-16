import os
import time
import speech_recognition as sr
import pyttsx3
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. SETUP & CONFIGURATION
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

try:
    engine = pyttsx3.init()
    engine.setProperty('rate', 160)
    HAS_AUDIO = True
except Exception:
    HAS_AUDIO = False

def speak_text(text):
    """Converts AI text to audible speech only if hardware exists."""
    if HAS_AUDIO:
        try:
            engine.say(text)
            engine.runAndWait()
        except:
            pass

def listen_to_user():
    """Captures audio from PC mic if available."""
    if not HAS_AUDIO:
        return None
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
            return recognizer.recognize_google(audio)
    except:
        return None

# 3. THE "SMART" PROMPT (Keeping your exact rules)
SYSTEM_RULES = """
You are CareBot, a specialized medical diagnostic assistant.

SCOPE CONSTRAINT:
- You ONLY answer queries related to health, symptoms, medicine, first aid, and wellness.
- If a user asks about general topics (e.g., coding, weather, sports, jokes, politics, or general history), you MUST politely refuse.
- Response for off-topic queries: "I am sorry, I am CareBot, a specialist for health-related queries. I cannot assist with general queries."

DIAGNOSTIC PROTOCOL:
1. NEVER diagnose in the first message.
2. If the user mentions a health symptom, you MUST ask 3-4 specific follow-up questions (duration, severity, location, etc.).
3. Suggest 3 possible conditions ONLY after enough detail is provided, always adding a medical disclaimer.
4. Keep language simple for rural users.
5. LANGUAGE RULE (STRICT):
You MUST respond in the same language as the user's input.
DO NOT default to English unless the user uses English.
DO NOT say "I can only respond in English".
If the user uses Hindi, Gujarati, or any regional language, respond in that language.
If multiple languages are used, respond in the dominant or simplest language.
"""

# 4. CORE AI LOGIC (With 2.5 Model Strings & Fast Retry)
def get_carebot_response(user_query, chat_history):
    """Handles 503 errors with a fast-retry mechanism."""
    max_retries = 2 
    retry_delay = 0.5 # Wait only half a second to keep it fast

    for attempt in range(max_retries):
        try:
            gemini_history = []
            for msg in chat_history[:-1]:
                role = "user" if msg["role"] == "user" else "model"
                gemini_history.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))

            chat = client.chats.create(
                model="gemini-2.5-flash-lite", 
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_RULES,
                    temperature=0.2
                ),
                history=gemini_history
            )
            
            response = chat.send_message(user_query)
            return response.text

        except Exception as e:
            err_msg = str(e).upper()
            if ("503" in err_msg or "UNAVAILABLE" in err_msg) and attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            return f"CareBot is a bit busy. Please try your message again. (Error: {str(e)})"

# 5. SIDEBAR LOGIC (Symptoms Summary)
def summarize_symptoms(chat_history):
    """Extremely lightweight summary to avoid lagging the main chat."""
    if not chat_history:
        return "Waiting for details..."
    
    user_text = " ".join([m["content"] for m in chat_history if m["role"] == "user"])
    prompt = f"List the medical symptoms mentioned in this text: {user_text}"
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite", 
            contents=prompt
        )
        return response.text
    except:
        return "Analyzing symptoms..."