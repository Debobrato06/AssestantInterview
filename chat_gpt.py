import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

from google import genai
import ollama

class ChatGPTAssistant:
    def __init__(self):
        self._init_openai(os.getenv("OPENAI_API_KEY"))
        self._init_gemini(os.getenv("GEMINI_API_KEY"))
        self.provider = "openai" # default
        self.system_prompt = """
        You are an Elite Real-Time Interview Copilot. You are listening to a live conversation between an Interviewer and a Candidate.
        
        Your Role:
        - Continuously analyze the conversation.
        - If the Interviewer asks a question: Provide a perfect, high-impact answer for the Candidate.
        - If the Candidate is speaking: Provide improvements, missing keywords, or corrections to their answer.
        - If there is general discussion: Provide tactical talking points to help the Candidate stand out.
        - Keep responses concise, professional, and strategic.
        
        Input Format: Context from either 'Interviewer' or 'Candidate'.

        Output JSON Format:
        {
            "main_answer": "Direct answer or strategic advice (2-3 sentences max).",
            "star_expansion": "STAR details or technical deep-dive if needed.",
            "talking_points": ["Ongoing tip 1", "Ongoing tip 2"],
            "keywords": ["Required Skill", "Industry Term"],
            "interviewer_question": "Anticipated next question or a clever follow-up the candidate should ask."
        }
        """
    def _init_openai(self, api_key):
        self.openai_client = OpenAI(api_key=api_key)

    def _init_gemini(self, api_key):
        if api_key and "your_gemini_api_key" not in api_key:
            self.gemini_client = genai.Client(api_key=api_key)
        else:
            self.gemini_client = None

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
        if self.provider == "gemini" and self.gemini_client:
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
            print(f"Querying Gemini 2.0 ({source})...")
            # Using the newest model gemini-2.0-flash-preview
            response = self.gemini_client.models.generate_content(
                model='gemini-2.0-flash-preview',
                contents=f"{self.system_prompt}\n\nSource: {source}\nContent: {question}",
                config={
                    'response_mime_type': 'application/json',
                }
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
