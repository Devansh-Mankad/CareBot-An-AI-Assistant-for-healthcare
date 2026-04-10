import os
import speech_recognition as sr
import pyttsx3
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

engine = pyttsx3.init()
engine.setProperty('rate', 160) # Speaking speed

def speak_text(text):
    """Converts AI text to audible speech."""
    engine.say(text)
    engine.runAndWait()

def listen_to_user():
    """Captures audio from the PC microphone and returns text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source,timeout=10,phrase_time_limit=15)
            text = recognizer.recognize_google(audio)
            return text
        except:
            return None

# THE "SMART" PROMPT
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
"""

def get_carebot_response(user_query, chat_history):
    try:
        gemini_history = []
        for msg in chat_history[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))

        chat = client.chats.create(
            model="gemini-2.5-flash",
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
    """Parallel NLP call to extract symptoms for the sidebar."""
    if not chat_history:
        return "Waiting for details..."
    
    # Extract only user inputs to find symptoms
    user_text = " ".join([m["content"] for m in chat_history if m["role"] == "user"])
    prompt = f"List the medical symptoms mentioned in this text as a brief bulleted list. If no symptoms, say 'Analyzing...': {user_text}"
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite", 
            contents=prompt
        )
        return response.text
    except:
        return "Gathering symptoms..."