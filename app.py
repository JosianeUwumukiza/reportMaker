from flask import Flask, request, jsonify
import os
from openai import OpenAI
from dotenv import load_dotenv


app = Flask(__name__)

# Initialize OpenAI client with the API key
load_dotenv()
# Initialize OpenAI client with the API key from environment variables
OpenAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OpenAI_API_KEY:
    print("Error: OpenAI API Key is missing!")

client = OpenAI(api_key=OpenAI_API_KEY)


@app.route('/generate_report', methods=['POST'])
def generate_report():
    data = request.json.get("bullet_points", "")

    try:
        if client.api_key:
            # Use the new client interface for chat completions
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": "Generate a detailed report based on these bullet points: " + data}
                ]
            )
            report = response.choices[0].message.content.strip()
            return jsonify({"report": report})
        else:
            return jsonify({"error": "API key not found"}), 500
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
