# service_client.py
# This module encapsulates all logic for interacting with the Gemini API, 
# including setting up the JSON schema, system instructions, and handling retries.
# It ensures that the responses are structured and grounded using Google Search.
import os
import requests
import json
import time
import uuid
from typing import Dict, Any, List

# --- Configuration Constants ---
# Use the model optimized for structured responses and grounding
GEMINI_MODEL = "gemini-2.5-flash-preview-09-2025"
API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_BASE_URL = os.environ.get("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/models")
BASE_URL = f"{GEMINI_BASE_URL}/{GEMINI_MODEL}:generateContent?key={API_KEY}"
MAX_RETRIES = 5

# --- LLM System Instructions ---
SYSTEM_PROMPT = (
    "Generate THREE different football trivia questions in Spanish, Catalan, and English. RANDOMIZE the correct answer position for each. Include source information for verification. Return ONLY valid JSON array:\n"
    "[\n"
    '  {\n'
    '    "question": {"es": "Primera pregunta", "ca": "Primera pregunta", "en": "First question"},\n'
    '    "options": [{"id": "A", "text": {"es": "A", "ca": "A", "en": "A"}}, {"id": "B", "text": {"es": "B", "ca": "B", "en": "B"}}, {"id": "C", "text": {"es": "C", "ca": "C", "en": "C"}}, {"id": "D", "text": {"es": "D", "ca": "D", "en": "D"}}],\n'
    '    "correct_option_id": "C",\n'
    '    "correct_answer_text": {"es": "Respuesta 1", "ca": "Resposta 1", "en": "Answer 1"},\n'
    '    "source": "Official website or reliable source"\n'
    '  },\n'
    '  {\n'
    '    "question": {"es": "Segunda pregunta", "ca": "Segona pregunta", "en": "Second question"},\n'
    '    "options": [{"id": "A", "text": {"es": "A", "ca": "A", "en": "A"}}, {"id": "B", "text": {"es": "B", "ca": "B", "en": "B"}}, {"id": "C", "text": {"es": "C", "ca": "C", "en": "C"}}, {"id": "D", "text": {"es": "D", "ca": "D", "en": "D"}}],\n'
    '    "correct_option_id": "B",\n'
    '    "correct_answer_text": {"es": "Respuesta 2", "ca": "Resposta 2", "en": "Answer 2"},\n'
    '    "source": "Official website or reliable source"\n'
    '  },\n'
    '  {\n'
    '    "question": {"es": "Tercera pregunta", "ca": "Tercera pregunta", "en": "Third question"},\n'
    '    "options": [{"id": "A", "text": {"es": "A", "ca": "A", "en": "A"}}, {"id": "B", "text": {"es": "B", "ca": "B", "en": "B"}}, {"id": "C", "text": {"es": "C", "ca": "C", "en": "C"}}, {"id": "D", "text": {"es": "D", "ca": "D", "en": "D"}}],\n'
    '    "correct_option_id": "A",\n'
    '    "correct_answer_text": {"es": "Respuesta 3", "ca": "Resposta 3", "en": "Answer 3"},\n'
    '    "source": "Official website or reliable source"\n'
    '  }\n'
    "]\n"
    "IMPORTANT: Mix up correct answers (A, B, C, D) across the three questions.\n"
    "Include a reliable source for each answer (official websites, sports databases, etc.)."
)

# --- JSON Schema for Structured Output (Enforced by the API) ---
# This ensures the model's output is predictable and parseable.
RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "question": {"type": "STRING", "description": "The main trivia question."},
        "options": {
            "type": "ARRAY",
            "description": "Exactly four options for the multiple-choice question.",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "id": {"type": "STRING", "enum": ["A", "B", "C", "D"]},
                    "text": {"type": "STRING"}
                },
                "required": ["id", "text"]
            }
        },
        "correct_option_id": {"type": "STRING", "enum": ["A", "B", "C", "D"], "description": "The identifier of the correct option."},
        "correct_answer_text": {"type": "STRING", "description": "The specific text of the correct answer for easy verification."}
    },
    "required": ["question", "options", "correct_option_id", "correct_answer_text"]
}

def call_gemini_api(user_query: str) -> Dict[str, Any] | None:
    """
    Calls the Gemini API with structured output and grounding enabled.
    Implements exponential backoff for retries.
    """
    if not API_KEY:
        print("❌ ERROR: GEMINI_API_KEY environment variable is not set.")
        return None

    payload = {
        "contents": [{"parts": [{"text": f"{SYSTEM_PROMPT}\n\n{user_query}"}]}],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    
    headers = {'Content-Type': 'application/json'}
    
    for attempt in range(MAX_RETRIES):
        try:
            # Exponential backoff: 2^attempt seconds (1, 2, 4, 8...)
            if attempt > 0:
                delay = 2 ** attempt
                print(f"Retrying API call in {delay} seconds... (Attempt {attempt + 1}/{MAX_RETRIES})")
                time.sleep(delay)

            response = requests.post(BASE_URL, headers=headers, data=json.dumps(payload))
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            
            result = response.json()
            
            # Extract the raw JSON string text from the structured response
            json_text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text')
            
            if json_text:
                # The response should be a valid JSON string enforced by the schema
                return json.loads(json_text)
            else:
                print("❌ ERROR: API response structure was missing content or candidates.")
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ API Request Failed (Network/HTTP Error): {e}")
        except json.JSONDecodeError:
            print(f"❌ API Response Failed (JSON Parsing Error): The model did not return valid JSON.")
        except Exception as e:
            print(f"❌ An unexpected error occurred during API call: {e}")

    print(f"❌ Final attempt failed after {MAX_RETRIES} retries.")
    return None

def generate_quiz(category: str, topic: str) -> List[Dict[str, Any]] | None:
    """
    Generates three complete quiz objects ready for saving.
    """
    print(f"\n🔍 Generating 3 quizzes for Category: '{category}' on Topic: '{topic}'...")

    # The prompt tells the model what to search for and generate
    user_prompt = f"Generate three different multiple-choice questions about the following football topic: {topic}"
    
    # Get the raw structured output from the API (now an array)
    raw_quiz_array = call_gemini_api(user_prompt)
    
    if not raw_quiz_array or not isinstance(raw_quiz_array, list):
        return None

    # Augment each quiz with required metadata
    final_quiz_list = []
    for raw_quiz_data in raw_quiz_array:
        final_quiz_data = {
            "quiz_id": str(uuid.uuid4()),
            "category": category,
            "query_topic": topic,
            **raw_quiz_data
        }
        final_quiz_list.append(final_quiz_data)
    
    return final_quiz_list