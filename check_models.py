import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("API Key not found")
else:
    genai.configure(api_key=api_key)
    print(f"Checking models for API Key ending in ...{api_key[-4:]}")
    
    print("\nAvailable Models:")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except Exception as e:
        print(f"Error listing models: {e}")

    print("\n--- Testing Generation ---")
    
    # Test standard models
    test_models = ['gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-1.0-pro', 'gemini-2.0-flash-exp']
    
    for model_name in test_models:
        print(f"\nTesting {model_name}...")
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hello")
            print(f"✅ Success! Response: {response.text.strip()}")
        except Exception as e:
            print(f"❌ Failed: {e}")
