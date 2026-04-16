# CareBot-An-AI-Assistant-for-healthcare
CareBot is a voice-enabled AI medical assistant designed to help users understand symptoms, ask health-related questions, and receive guided responses using a structured diagnostic protocol.

It uses:
🎤 Speech Recognition for voice input
🔊 Text-to-Speech for audio responses
🤖 Google Gemini API for AI-powered medical assistance
🌐 Streamlit for an interactive frontend

Features:
✅ Voice input using microphone
✅ AI-generated medical responses
✅ Smart diagnostic questioning (no instant diagnosis)
✅ Symptom tracking and summarization
✅ Handles API errors with retry mechanism
✅ Works even without audio hardware (fallback to text)

🧠 How It Works
1. Initialization
-->Loads environment variables using dotenv
-->Connects to Gemini API
-->Initializes Text-to-Speech engine safely
2. Voice Handling
-->listen_to_user() captures speech input
-->speak_text() converts AI response to audio
3. AI Processing
-->Uses Gemini 2.5 Flash Lite model
-->Applies strict system rules:
Only health-related queries allowed
No immediate diagnosis
Asks follow-up questions first
4. Retry Mechanism
-->Automatically retries API calls on:
503 errors : Temporary service unavailability
5. Symptom Summary
-->Extracts symptoms from chat history
-->Displays lightweight summary in sidebar

Dependencies:
streamlit
speechrecognition
pyttsx3
python-dotenv
google-generativeai
pyaudio
