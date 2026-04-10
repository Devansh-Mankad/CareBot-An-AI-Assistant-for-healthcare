import os
from flask import Flask, request, jsonify
from brain import get_carebot_response
from dotenv import load_dotenv

# 1. Initialize Environment
load_dotenv()
app = Flask(__name__)

@app.route('/', methods=['GET'])
def server_status():
    """Verify backend is live for faculties."""
    return "CareBot WhatsApp Backend (Python 3.13) is Live!", 200

@app.route('/whatsapp', methods=['POST'])
def handle_whatsapp_request():
    """Main Webhook for WhatsApp integration."""
    try:
        data = request.json
        
        # 2. Extract user input from the bridge (Evolution API format)
        user_input = data.get("message", {}).get("conversation") or data.get("body")
        sender_id = data.get("key", {}).get("remoteJid") or data.get("from")

        if user_input:
            response_generator = get_carebot_response(user_input, [])
            final_reply = "".join(list(response_generator))

            # 4. Success Response
            return jsonify({
                "status": "success",
                "sender": sender_id,
                "reply": final_reply
            }), 200
        
        return jsonify({"status": "error", "message": "Empty message"}), 400

    except Exception as e:
        # Important for debugging during the exhibition
        print(f"Server Error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    # Render binds to this port automatically
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)