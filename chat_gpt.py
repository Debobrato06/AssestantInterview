import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

import google.generativeai as genai_stable
import ollama

class ChatGPTAssistant:
    def __init__(self):
        self._init_openai(os.getenv("OPENAI_API_KEY"))
        self._init_gemini(os.getenv("GEMINI_API_KEY"))
        self.provider = "gemini" # Set Gemini as default
        self.system_prompt = """
        You are an Elite Real-Time Meeting & Interview Assistant. You are listening to a live conversation.
        
        Your Role:
        - Continuously analyze the conversation.
        - If someone asks a question: Provide a perfect, high-impact answer for the user.
        - If the user is speaking: Provide improvements, missing keywords, or corrections.
        - If there is general discussion: Provide tactical talking points and key takeaways.
        - Keep responses concise, professional, and strategic.
        
        Input Format: Context from either 'Interviewer/Host' or 'Candidate/User'.

        Output JSON Format:
        {
            "main_answer": "Direct answer or strategic advice (2-3 sentences max).",
            "star_expansion": "Detailed explanation or technical deep-dive if needed.",
            "talking_points": ["Ongoing tip 1", "Key takeaway 1"],
            "keywords": ["Required Skill", "Industry Term", "Key Concept"],
            "interviewer_question": "Anticipated next question or a clever follow-up the user should ask."
        }
        """
    def _init_openai(self, api_key):
        self.openai_client = OpenAI(api_key=api_key)

    def _init_gemini(self, api_key):
        if api_key and "your_gemini_api_key" not in api_key:
            try:
                genai_stable.configure(api_key=api_key)
                
                # Auto-detect available models
                available_models = [m.name for m in genai_stable.list_models() if 'generateContent' in m.supported_generation_methods]
                print(f"Available Gemini Models: {available_models}")
                
                # Priority list
                priority = [
                    'models/gemini-1.5-flash',
                    'models/gemini-1.5-flash-latest',
                    'models/gemini-2.0-flash-exp',
                    'models/gemini-1.0-pro',
                    'models/gemini-pro'
                ]
                
                selected_model = None
                for p in priority:
                    if p in available_models:
                        selected_model = p
                        break
                
                if not selected_model and available_models:
                    selected_model = available_models[0]
                
                if selected_model:
                    print(f"Selected Gemini Model: {selected_model}")
                    self.gemini_model = genai_stable.GenerativeModel(selected_model)
                else:
                    print("No suitable Gemini model found!")
                    self.gemini_model = None
            except Exception as e:
                print(f"Gemini Init Error: {e}")
                self.gemini_model = None
        else:
            self.gemini_model = None

    def update_key(self, new_key, provider="openai"):
        if provider == "openai":
            self._init_openai(new_key)
            self.provider = "openai"
        elif provider == "gemini":
            self._init_gemini(new_key)
            self.provider = "gemini"
        elif provider == "ollama":
            self.provider = "ollama"

    def get_answer(self, question, source="Interviewer"):
        if self.provider == "gemini" and self.gemini_model:
            return self._get_gemini_answer(question, source)
        elif self.provider == "ollama":
            return self._get_ollama_answer(question, source)
        return self._get_openai_answer(question, source)

    def _get_openai_answer(self, question, source):
        try:
            print(f"Querying OpenAI ({source})...")
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Source: {source}\nContent: {question}"}
                ],
                response_format={"type": "json_object"},
                max_tokens=800
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"!!! OpenAI Error: {e}")
            return {"main_answer": f"OpenAI Error: {str(e)}", "talking_points": [], "keywords": [], "interviewer_question": ""}

    def _get_gemini_answer(self, question, source):
        try:
            print(f"Querying Gemini 1.5 Stable ({source})...")
            response = self.gemini_model.generate_content(
                f"{self.system_prompt}\n\nSource: {source}\nContent: {question}",
                generation_config=genai_stable.types.GenerationConfig(
                    response_mime_type="application/json",
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"!!! Gemini Error: {e}")
            return {"main_answer": f"Gemini Error: {str(e)}", "talking_points": [], "keywords": [], "interviewer_question": ""}

    def _get_ollama_answer(self, question, source):
        try:
            print(f"Querying Ollama Local ({source})...")
            response = ollama.chat(
                model='llama3',
                messages=[
                    {'role': 'system', 'content': self.system_prompt},
                    {'role': 'user', 'content': f"Source: {source}\nContent: {question}"}
                ],
                format='json'
            )
            return json.loads(response['message']['content'])
        except Exception as e:
            print(f"!!! Ollama Error: {e}")
            return {"main_answer": "Local LLM Error. Ensure Ollama is running and Llama3 is pulled (`ollama pull llama3`).", "talking_points": [], "keywords": [], "interviewer_question": ""}

    def transcribe_audio(self, audio_bytes):
        """Transcribes audio bits using OpenAI Whisper API for maximum accuracy."""
        try:
            import tempfile
            # Whisper supports webm, mp3, wav, etc.
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name
            
            try:
                with open(tmp_path, "rb") as audio_file:
                    transcript = self.openai_client.audio.transcriptions.create(
                        model="whisper-1", 
                        file=audio_file
                    )
                return transcript.text
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        except Exception as e:
            print(f"Whisper Error: {e}")
            return None
