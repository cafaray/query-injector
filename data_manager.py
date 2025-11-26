# data_manager.py
# This module handles the structured persistence of the quiz data 
# into the football_quiz_data.json file.
# It ensures that new quizzes are appended correctly without overwriting existing data.

import json
import os
from typing import Dict, Any, List

# Define the file path for data persistence
QUIZ_DATA_FILE = "football_quiz_data.json"

def load_existing_data() -> List[Dict[str, Any]]:
    """Loads existing quiz data from the JSON file."""
    if not os.path.exists(QUIZ_DATA_FILE):
        return []
    try:
        with open(QUIZ_DATA_FILE, 'r') as f:
            # Load the entire list of quizzes
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, IOError) as e:
        print(f"Warning: Could not load existing data or file is corrupt ({e}). Starting with empty list.")
        return []

def save_quiz_data(new_quiz: Dict[str, Any]) -> None:
    """
    Loads existing quizzes, appends the new quiz, and saves the updated list.
    
    Args:
        new_quiz: The structured quiz object to save.
    """
    # 1. Load existing data
    all_quizzes = load_existing_data()
    
    # 2. Append the new data
    all_quizzes.append(new_quiz)
    
    # 3. Write back the complete list
    try:
        with open(QUIZ_DATA_FILE, 'w') as f:
            # Use indent for readability in the stored JSON file
            json.dump(all_quizzes, f, indent=4)
        print(f"\n✅ Successfully saved new quiz data to {QUIZ_DATA_FILE}")
    except IOError as e:
        print(f"\n❌ ERROR: Could not write data to file: {e}")

# Pydantic models for strict type checking and validation of the incoming quiz data
from pydantic import BaseModel, Field, ValidationError
from typing import Dict

class MultilingualText(BaseModel):
    """Schema for multilingual text content."""
    es: str  # Spanish
    ca: str  # Catalan
    en: str  # English

class Option(BaseModel):
    """Schema for a single multiple-choice option."""
    id: str = Field(pattern="^[A-D]$")  # Must be A, B, C, or D
    text: MultilingualText

class QuizItem(BaseModel):
    """Schema for the complete structured quiz item."""
    quiz_id: str
    category: str
    query_topic: str
    question: MultilingualText
    options: List[Option]
    correct_option_id: str = Field(pattern="^[A-D]$")
    correct_answer_text: MultilingualText
    source: str

def validate_quiz_structure(data: Dict[str, Any]) -> Dict[str, Any] | None:
    """Validates the generated quiz data against the Pydantic schema."""
    try:
        # Pydantic will validate the structure, types, and constraints (like A-D)
        validated_data = QuizItem(**data)
        # Convert back to a standard dictionary for saving
        return validated_data.model_dump()
    except ValidationError as e:
        print("\n❌ DATA VALIDATION ERROR: The structured data from the LLM did not match the required schema.")
        print(e)
        return None