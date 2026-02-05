import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

test_models = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-1.0-pro', 'gemini-pro']

for model_name in test_models:
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("test")
        print(f"SUCCESS: {model_name}")
        break
    except Exception as e:
        print(f"FAILED: {model_name} - {e}")
