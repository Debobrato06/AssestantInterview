import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env if it exists
load_dotenv()

# 1. Configure the API key
# It's best to pull this from an environment variable for security
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("No API key found. Please set the GEMINI_API_KEY environment variable in your .env file.")

genai.configure(api_key=api_key)

# 2. Initialize the Model
# 'gemini-1.5-flash' or 'gemini-1.5-pro' are newer and more capable models.
# Using 'gemini-1.5-flash' for efficiency.
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. Start a Chat Session
# The history list tracks the conversation context
chat = model.start_chat(history=[])

def run_chat():
    print("--- Gemini Chatbot (Type 'quit' to exit) ---")
    
    while True:
        # Get user input
        user_input = input("You: ")
        
        # Exit condition
        if user_input.lower() in ['quit', 'exit']:
            print("Exiting chat...")
            break
            
        try:
            # 4. Send message to Gemini
            # stream=True allows the response to print as it's being generated
            response = chat.send_message(user_input, stream=True)
            
            print("Gemini: ", end="")
            for chunk in response:
                if chunk.text:
                    print(chunk.text, end="")
            print("\n")
            
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_chat()
