# AI Meeting Summarizer Backend

FastAPI backend service for processing meeting audio and text to generate summaries, extract tasks, and identify action points.

## Features

- **Audio Processing**: Convert audio files to text using Whisper or Google Speech-to-Text
- **Text Summarization**: Generate concise summaries using BART, T5, or OpenAI models
- **Task Extraction**: Automatically identify assigned tasks with deadlines and priorities
- **Action Point Detection**: Extract actionable items from meeting discussions
- **Participant Identification**: Recognize meeting participants from transcript
- **Multiple Input Formats**: Support for various audio formats and direct text input

## Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Install additional models:**
```bash
# Download spaCy English model
python -m spacy download en_core_web_sm

# For Whisper (if not already installed)
pip install git+https://github.com/openai/whisper.git
```

3. **Set up environment variables:**
```bash
# Optional: OpenAI API (for enhanced summarization)
export OPENAI_API_KEY="your-openai-api-key"

# Optional: Google Cloud (for speech-to-text)
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
export GOOGLE_CLOUD_PROJECT="your-project-id"

# Configuration
export WHISPER_MODEL="base"  # tiny, base, small, medium, large
export DEBUG="true"
```

## Usage

1. **Start the server:**
```bash
python main.py
# or
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

2. **API Endpoints:**

### Upload Audio
```bash
curl -X POST "http://localhost:8000/upload-audio" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@meeting.wav"
```

### Process Text
```bash
curl -X POST "http://localhost:8000/process-text" \
  -H "Content-Type: application/json" \
  -d '{"text": "Meeting transcript here..."}'
```

### Health Check
```bash
curl http://localhost:8000/health
```

## API Response Format

```json
{
  "summary": "Meeting summary text...",
  "tasks": [
    {
      "assignee": "John Doe",
      "task": "Complete the project proposal",
      "deadline": "2025-01-15",
      "priority": "high"
    }
  ],
  "action_points": [
    "Schedule follow-up meeting",
    "Review budget allocation"
  ],
  "participants": ["John Doe", "Jane Smith", "Mike Johnson"],
  "meeting_date": "January 8, 2025",
  "confidence_score": 0.85
}
```

## Model Configuration

### Whisper Models
- `tiny`: Fastest, least accurate (~39 MB)
- `base`: Good balance (~74 MB) - **Default**
- `small`: Better accuracy (~244 MB)
- `medium`: High accuracy (~769 MB)
- `large`: Best accuracy (~1550 MB)

### Summarization Models
- `facebook/bart-large-cnn`: Default, good for news/meetings
- `t5-small`: Lightweight alternative
- `gpt-3.5-turbo`: Requires OpenAI API key

## Performance Tips

1. **For production:** Use `medium` or `large` Whisper models
2. **For development:** Use `base` model for faster processing
3. **Audio preprocessing:** Normalize audio to 16kHz mono for better results
4. **Large files:** Consider chunking long audio files (>30 minutes)

## Error Handling

The API includes comprehensive error handling:
- Invalid file formats
- Large file size limits
- Model loading failures
- Processing timeouts
- Fallback mechanisms for failed AI models

## Development

Run tests:
```bash
pytest tests/
```

Format code:
```bash
black backend/
isort backend/
```

## Production Deployment

1. **Use production ASGI server:**
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

2. **Set production environment variables:**
```bash
export DEBUG="false"
export API_HOST="0.0.0.0"
export API_PORT="8000"
```

3. **Consider using Redis for caching and task queues for long-running processes**