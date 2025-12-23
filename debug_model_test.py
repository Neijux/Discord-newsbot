import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("API Key not found")
else:
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content("Hello, can you hear me?")
        print(f"Success! Response: {response.text}")
    except Exception as e:
        print(f"Error with gemini-2.5-flash: {e}")
