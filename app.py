# app.py
# The entry point that handles the user interface, coordination, and error logging.
# It interacts with both the Gemini service client and the data manager modules.
import os
from typing import Dict, Any, List
from gemini_client import generate_quiz
from data_manager import save_quiz_data, validate_quiz_structure, QUIZ_DATA_FILE

# --- Quiz Categories (Matching the design document) ---
CATEGORIES = {
    "1": "Match",
    "2": "Venue",
    "3": "Previous Years",
    "4": "Curious Info",
    "5": "Team",
    "6": "Assistants"
}

def display_menu() -> None:
    """Displays the interactive menu to the user."""
    print("\n" + "="*50)
    print("      ⚽ FOOTBALL QUIZ GENERATOR ⚽")
    print("="*50)
    print("Please select a query category:")
    for key, value in CATEGORIES.items():
        print(f"  [{key}] {value}")
    print("  [0] Exit")
    print("-" * 50)

def main() -> None:
    """Main execution function for the CLI application."""
    print("Initializing Football Quiz Generator...")
    
    # Check for API key presence early
    if not os.environ.get("GEMINI_API_KEY"):
        print("CRITICAL: The GEMINI_API_KEY environment variable is NOT set.")
        print("Please set this variable to run the application.")
        return

    while True:
        display_menu()
        choice = input("Enter your choice (1-6 or 0 to exit): ").strip()

        if choice == '0':
            print("\nShutting down. Goodbye! 👋")
            break
        
        category_name = CATEGORIES.get(choice)
        
        if not category_name:
            print("❗ Invalid choice. Please try again.")
            continue
            
        topic = input(f"Selected Category: {category_name}.\nEnter a specific topic/query (e.g., 'Manchester Derby 2024'): ").strip()
        
        if not topic:
            print("❗ Topic cannot be empty. Please try again.")
            continue

        # 1. Generate the raw quiz data using the Gemini client
        raw_quizzes = generate_quiz(category_name, topic)
        
        if raw_quizzes:
            for i, raw_quiz in enumerate(raw_quizzes, 1):
                # 2. Validate the data structure
                validated_quiz = validate_quiz_structure(raw_quiz)
                
                if validated_quiz:
                    # 3. Display the result for the user
                    print(f"\n" + "#"*60)
                    print(f"  GENERATED QUIZ {i} PREVIEW  ")
                    print("#"*60)
                    print(f"  Category: {validated_quiz['category']}")
                    print(f"  Topic: {validated_quiz['query_topic']}")
                    print(f"  Question (EN): {validated_quiz['question']['en']}")
                    print("  Options:")
                    for opt in validated_quiz['options']:
                        print(f"    [{opt['id']}] {opt['text']['en']}")
                    print(f"  Correct Answer ID: {validated_quiz['correct_option_id']}")
                    print(f"  Answer Text (EN): {validated_quiz['correct_answer_text']['en']}")
                    print("#"*60)
                    
                    # 4. Save the data
                    save_quiz_data(validated_quiz)
                
                else:
                    print(f"\nSkipping save for quiz {i} due to validation failure.")
        else:
            print("\nCould not generate quizzes. Check API key and logs for errors.")

if __name__ == "__main__":
    main()