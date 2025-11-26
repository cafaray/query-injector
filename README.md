# Football Quiz Generator

An AI-powered multilingual football trivia generator that creates structured quiz questions using Google's Gemini API. The system generates questions in Spanish, Catalan, and English with randomized answer positions.

## Core Features

- **Multilingual Support**: Questions generated in Spanish (es), Catalan (ca), and English (en)
- **Batch Generation**: Creates 3 different questions per API call for efficiency
- **Randomized Answers**: Correct answer position varies (A, B, C, or D) to prevent predictability
- **Structured Data**: JSON output with strict validation using Pydantic models
- **Category System**: 6 predefined categories for organized quiz generation
- **Source Tracking**: Each answer includes source information for verification
- **Bulk Upload**: Upload entire quiz database to backend service in one operation

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│     app.py      │───▶│  gemini_client.py │───▶│  Gemini API     │
│   (Main CLI)    │    │  (API Handler)   │    │  (AI Service)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │
         ▼                        ▼
┌─────────────────┐    ┌──────────────────┐
│ data_manager.py │    │ Response Parser  │
│ (Data Storage)  │    │ & Validation     │
└─────────────────┘    └──────────────────┘
         │
         ▼
┌─────────────────┐
│football_quiz_   │
│data.json        │
│(Persistent Data)│
└─────────────────┘
```

### Components

- **`app.py`**: CLI interface and main application logic
- **`gemini_client.py`**: Gemini API integration and response handling
- **`data_manager.py`**: Data validation, storage, and Pydantic models
- **`football_quiz_data.json`**: Persistent JSON storage for generated quizzes

## How It Works

1. **User Input**: Select category and enter specific topic
2. **API Request**: System sends structured prompt to Gemini API requesting 3 questions
3. **AI Generation**: Gemini generates multilingual questions with randomized correct answers
4. **Validation**: Pydantic models validate structure and data types
5. **Storage**: Valid quizzes are appended to JSON file
6. **Display**: Preview shows generated questions in English

## Categories

| ID | Category | Description |
|----|----------|-------------|
| 1 | Match | Specific matches, results, scores |
| 2 | Venue | Stadiums, locations, facilities |
| 3 | Previous Years | Historical events, past seasons |
| 4 | Curious Info | Interesting facts, records, trivia |
| 5 | Team | Club information, players, management |
| 6 | Assistants | Coaches, staff, technical teams |

## Installation & Setup

### Prerequisites
- Python 3.8+
- Google Gemini API key

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd query-injector

# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
```

### Configuration

Copy and configure the `.env` file:

```bash
# Copy the environment template
cp .env .env.local

# Edit .env file with your actual values
GEMINI_API_KEY=your_actual_gemini_api_key
QUARKUS_UPLOAD_URL=http://localhost:8080/v1/questions/bulkUpload
```

**Environment Variables:**
- `GEMINI_API_KEY`: Your Google Gemini API key
- `GEMINI_BASE_URL`: Gemini API base URL (default provided)
- `QUARKUS_UPLOAD_URL`: Backend upload endpoint
- `QUARKUS_UPLOAD_URL_LOCAL`: Local development endpoint
- `QUARKUS_UPLOAD_URL_PROD`: Production endpoint

## Usage

### Basic Execution

```bash
python app.py
```

### Interactive Menu

```
==================================================
      ⚽ FOOTBALL QUIZ GENERATOR ⚽
==================================================
Please select a query category:
  [1] Match
  [2] Venue
  [3] Previous Years
  [4] Curious Info
  [5] Team
  [6] Assistants
  [7] Upload Quiz Data to Backend
  [0] Exit
--------------------------------------------------
Enter your choice (1-7 or 0 to exit): 1
Selected Category: Match.
Enter a specific topic/query (e.g., 'Manchester Derby 2024'): El Clasico 2023
```

## Output Format

### JSON Structure

```json
{
  "quiz_id": "uuid-string",
  "category": "Match",
  "query_topic": "El Clasico 2023",
  "question": {
    "es": "¿Cuál fue el resultado del Clásico de octubre 2023?",
    "ca": "Quin va ser el resultat del Clàssic d'octubre 2023?",
    "en": "What was the result of the October 2023 Clasico?"
  },
  "options": [
    {
      "id": "A",
      "text": {
        "es": "Barcelona 2-1 Real Madrid",
        "ca": "Barcelona 2-1 Real Madrid", 
        "en": "Barcelona 2-1 Real Madrid"
      }
    }
  ],
  "correct_option_id": "C",
  "correct_answer_text": {
    "es": "Real Madrid ganó 2-1",
    "ca": "El Real Madrid va guanyar 2-1",
    "en": "Real Madrid won 2-1"
  },
  "source": "Official La Liga website"
}
```

## Examples

### Example 1: Match Category
**Input**: `Barcelona vs Real Madrid 2023`
**Output**: Questions about specific Clasico matches, scores, and key moments

### Example 2: Team Category  
**Input**: `Manchester United history`
**Output**: Questions about club records, famous players, and achievements

### Example 3: Venue Category
**Input**: `Camp Nou stadium`
**Output**: Questions about stadium capacity, location, and notable matches

### Example 4: Bulk Upload
**Menu Option**: `[7] Upload Quiz Data to Backend`
**Process**: 
1. Select option 7
2. Enter file path (or press Enter for default `football_quiz_data.json`)
3. System validates all quiz data
4. Uploads valid quizzes to configured backend service

## Technical Details

### API Configuration
- **Model**: `gemini-2.5-flash-preview-09-2025`
- **Response Format**: JSON with strict schema validation
- **Retry Logic**: Exponential backoff (max 5 attempts)
- **Batch Size**: 3 questions per API call

### Data Validation
- **Pydantic Models**: Strict type checking and validation
- **Required Fields**: All quiz components must be present
- **Language Validation**: Ensures all three languages are included
- **Option Validation**: Exactly 4 options (A, B, C, D) required
- **Source Validation**: Each answer must include source information

### Backend Integration
- **Bulk Upload**: Validates and uploads entire quiz database
- **Data Validation**: Pre-upload validation using Pydantic models
- **Error Recovery**: Skips invalid entries, uploads valid ones
- **Configurable Endpoints**: Local and production URLs via environment variables

### Error Handling
- API key validation
- Network error recovery with retries
- JSON parsing error handling
- Data validation with detailed error messages
- Upload failure recovery with detailed error reporting

## File Structure

```
query-injector/
├── app.py                    # Main CLI application
├── gemini_client.py          # Gemini API integration
├── data_manager.py           # Data validation & storage
├── football_quiz_data.json   # Generated quiz storage
├── .env                      # Environment configuration
├── .gitignore               # Git ignore rules
├── requirements.txt          # Dependencies (requests, pydantic, python-dotenv)
└── README.md                # This documentation
```

## Troubleshooting

### Common Issues

1. **API Key Error**: Ensure `GEMINI_API_KEY` is set in `.env` file
2. **Network Errors**: Check internet connection and API quotas
3. **Validation Errors**: Verify JSON structure matches expected schema
4. **Empty Responses**: Check API key permissions and model availability
5. **Upload Failures**: Verify `QUARKUS_UPLOAD_URL` is correct and backend is running
6. **File Not Found**: Check quiz data file path when using bulk upload
7. **Environment Variables**: Ensure `.env` file exists and `python-dotenv` is installed

### Debug Mode
Add debug prints in `gemini_client.py` to inspect API responses:

```python
print(f"Raw API Response: {result}")
```

## License

This project is licensed under the MIT License.