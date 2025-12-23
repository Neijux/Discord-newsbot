import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

models_to_test = [
    'gemini-3-pro-preview',
    'gemini-3-flash-preview',
    'gemini-2.5-flash',
    'gemini-2.0-flash-exp',
    'gemini-1.5-pro'
]

print("--- Model Availability Test ---")
for model_name in models_to_test:
    print(f"\nTesting: {model_name}")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hi", request_options={"timeout": 10})
        print(f"✅ Success! (Response: {response.text.strip()})")
    except Exception as e:
        print(f"❌ Failed: {e}")
