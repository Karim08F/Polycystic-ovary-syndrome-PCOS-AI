
import os
import africastalking
import google.generativeai as genai
from flask import Flask, request
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="C:/Users/MWANGOLO/Desktop/BuildWithAI/key.env")

# Africa's Talking configuration
username = os.getenv("AFRICASTALKING_USERNAME", "sandbox")
api_key = os.getenv("AFRICASTALKING_API_KEY")
shortcode = os.getenv("AFRICASTALKING_SHORTCODE", "94906")
keyword = "PCOS AI"

# Initialize Africa's Talking
africastalking.initialize(username, api_key)
sms = africastalking.SMS

# Gemini AI configuration
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

generation_config = {
    "temperature": 0.2,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 60,
}

# Gemini model setup
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash-lite",
    generation_config=generation_config,
    system_instruction=(
        "You are PCOS AI, a friendly and knowledgeable assistant that educates and advises "
        "girls and women about Polycystic Ovary Syndrome (PCOS). "
        "Your responses must be factual, clear, supportive, and under 160 characters."
    ),
)

# Flask app setup
app = Flask(__name__)

# Function to send SMS
def send_sms(recipient, message):
    try:
        # Split long messages into 160-character chunks
        for part in [message[i:i+160] for i in range(0, len(message), 160)]:
            response = sms.send(part, [recipient])
            print("Message sent:", response)
    except Exception as e:
        print(f"Failed to send message: {str(e)}")

# Gemini AI response
def get_gemini_response(query):
    try:
        response = model.generate_content(query)
        if hasattr(response, "text"):
            return response.text.strip()
        else:
            return "I'm not sure how to respond to that yet."
    except Exception as e:
        print("Gemini error:", e)
        return "Sorry, I couldn't process your question right now."

## Flask route to handle incoming SMS
@app.route("/incoming_sms", methods=["POST"])
def incoming_sms():
    # Debug: confirm webhook hit
    print("Webhook hit!")

    # Access incoming data
    data = request.form
    print("Full data received:", data)  # See all fields Africa's Talking sends

    sender = data.get("from")
    message = data.get("text", "").strip()

    print(f"Incoming SMS from {sender}: {message}")

    # Check if message starts with the keyword
    if message.lower().startswith(keyword.lower()):
        query = message[len(keyword):].strip()  # Remove keyword
        if not query:
            reply = "Hi! Please include your question after 'PCOS AI'."
            send_sms(sender, reply)
            print(f"Sent reply: {reply}")
        else:
            ai_reply = get_gemini_response(query)
            send_sms(sender, ai_reply)
            print(f"Sent AI reply: {ai_reply}")
    else:
        reply = f"Please start your message with '{keyword}'. Example: PCOS AI what are symptoms?"
        send_sms(sender, reply)
        print(f"Sent reply for missing keyword: {reply}")

    return "OK", 200


# Optional home route
@app.route("/")
def home():
    return " PCOS AI SMS Advisor is running and ready to educate!"

# Run Flask app
if __name__ == "__main__":
    app.run(port=5000, debug=True)
