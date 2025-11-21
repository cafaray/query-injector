System Design: Gemini-Powered Football Quiz Generator

This document outlines the design and requirements for a Python system that uses the Gemini API to generate multiple-choice football (soccer) trivia questions, validates the data, and saves the output to a structured JSON file.

1. Core System Components

The system will consist of four primary modules that execute in sequence:

1.1. User Input & Orchestration Module

Purpose: Handles user interaction (selecting a topic/category) and manages the overall workflow.

Requirements: Must present a clear list of predefined categories to the user (e.g., Match, Venue, Team, etc.) and allow for specific input (e.g., "Manchester City vs. Arsenal 2024").

1.2. LLM Interaction Module (The "Query Formulator")

Purpose: Communicates with the Gemini API to formulate the quiz content.

Critical Feature: Structured Output: To ensure the response is reliable and easy to parse, this module MUST utilize the API's JSON Schema feature. The model will be instructed to return the data directly in the required JSON format, minimizing parsing errors.

Requirements:

Must use Google Search grounding (tools: [{"google_search": {}}]) in the API call to ensure factual accuracy for current or historical queries.

Must provide a robust systemInstruction to guide the model (e.g., "You are a football trivia specialist. Generate one complex, multiple-choice question with four distinct options, only one of which is correct.").

1.3. Data Model & Validation Module

Purpose: Defines the required JSON structure and checks the generated data before saving (although structured output minimizes this need, a final validation check is good practice).

Data Structure: (See Section 3 for the detailed JSON schema).

Requirements: Must assign a unique identifier (quiz_id) and correctly map the user's category selection to the output.

1.4. File Management Module

Purpose: Handles persistence by writing the generated, validated data to the disk.

Requirements: Must append new JSON objects to a single file (football_quiz_data.json) to create a continuous database of trivia questions.

2. Query Classification & Categories

The system must allow the user to select one of the following classification tags before generating a query. This tag will be saved in the final JSON output.

Classification Tag

Description of Query Focus

Example Topic Input

Match

Specific current/upcoming fixture.

"Real Madrid vs. Barcelona (Upcoming)"

Venue

Information about a stadium or location.

"Wembley Stadium History"

Previous Years

Historical data from a specific rivalry/match.

"El Clásico 1990-2000 Era"

Curious Info

Unusual facts, records, or strange events.

"Fastest red cards in EPL"

Team

Facts specific to a club's players, history, or league standing.

"Manchester United 2008 Squad"

Assistants

Facts related to coaching staff, referees, or support roles.

"Current Premier League Referee Roster"

3. Pre-Configured JSON Format (Data Requirements)

The system must output data that strictly adheres to the following JSON schema. This structure will be mirrored in the responseSchema sent to the Gemini API to enforce structured generation.

{
  "quiz_id": "string (UUID or Timestamp)",
  "category": "string (One of the Classification Tags above, e.g., 'Match')",
  "query_topic": "string (The user's specific input, e.g., 'Real Madrid vs. Barcelona (Upcoming)')",
  "question": "string (The generated trivia question)",
  "options": [
    {
      "id": "A",
      "text": "string (Text for Option A)"
    },
    {
      "id": "B",
      "text": "string (Text for Option B)"
    },
    {
      "id": "C",
      "text": "string (Text for Option C)"
    },
    {
      "id": "D",
      "text": "string (Text for Option D)"
    }
  ],
  "correct_option_id": "string (Must be 'A', 'B', 'C', or 'D')",
  "correct_answer_text": "string (The specific, correct answer text for verification)"
}


4. Technical Requirements

Programming Language: Python 3.x.

API Integration: Use the requests library (or an official Python SDK if available) to communicate with the Gemini API.

Dependencies: json for handling data serialization, uuid for generating unique IDs, and the LLM client library.

Error Handling: Implement try...except blocks for:

API connection failures (network errors, rate limits).

Parsing errors if the model fails to adhere to the JSON schema despite the enforcement.

File I/O errors when writing to the JSON file.

Best Practice: Implement exponential backoff for API request retries to handle transient errors or rate limiting gracefully.

requests>=2.31.0
pydantic>=2.5.3

Note: For environment setup, you would use uv like:

uv venv

uv pip install -r requirements.txt


