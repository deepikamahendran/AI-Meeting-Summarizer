"""
AI Meeting Summarizer FastAPI Backend
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import tempfile
import os
from datetime import datetime
import json
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import AI processing modules
from audio_processor import AudioProcessor
from text_summarizer import TextSummarizer
from task_extractor import TaskExtractor
from config import settings

app = FastAPI(title="AI Meeting Summarizer", version="1.0.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class TextInput(BaseModel):
    text: str

class Task(BaseModel):
    assignee: str
    task: str
    deadline: str
    priority: str

class MeetingSummary(BaseModel):
    summary: str
    tasks: List[Task]
    action_points: List[str]
    participants: List[str]
    duration: Optional[str] = None
    meeting_date: str
    confidence_score: float

class ProcessingStatus(BaseModel):
    status: str
    progress: int
    message: str

# Initialize processors
audio_processor = None
text_summarizer = None
task_extractor = None

@app.on_event("startup")
async def startup_event():
    """Initialize AI models on startup"""
    global audio_processor, text_summarizer, task_extractor
    
    try:
        logger.info("Initializing AI models...")
        audio_processor = AudioProcessor()
        text_summarizer = TextSummarizer(model_type="huggingface")
        task_extractor = TaskExtractor()
        logger.info("AI models initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize AI models: {e}")
        # Initialize with fallback processors
        audio_processor = AudioProcessor()
        text_summarizer = TextSummarizer(model_type="huggingface")
        task_extractor = TaskExtractor()

@app.get("/")
async def root():
    return {"message": "AI Meeting Summarizer API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "models_loaded": {
            "audio_processor": audio_processor is not None,
            "text_summarizer": text_summarizer is not None,
            "task_extractor": task_extractor is not None
        }
    }

@app.post("/upload-audio", response_model=dict)
async def upload_audio(file: UploadFile = File(...)):
    """
    Upload and process audio file
    """
    # Check file type
    allowed_types = ['audio/', 'video/']
    if not any(file.content_type.startswith(t) for t in allowed_types):
        raise HTTPException(status_code=400, detail="File must be an audio or video file")
    
    # Check file size
    if file.size and file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File size exceeds {settings.MAX_FILE_SIZE // (1024*1024)}MB limit")
    
    try:
        logger.info(f"Processing audio file: {file.filename}")
        
        # Save uploaded file temporarily
        file_extension = os.path.splitext(file.filename)[1] if file.filename else '.wav'
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Preprocess audio for better results
        preprocessed_path = audio_processor.preprocess_audio(tmp_file_path)
        
        # Process audio to text
        logger.info("Starting transcription...")
        transcript = await audio_processor.transcribe(preprocessed_path)
        logger.info(f"Transcription completed. Length: {len(transcript)} characters")
        
        # Clean up temp file
        os.unlink(tmp_file_path)
        if preprocessed_path != tmp_file_path:
            os.unlink(preprocessed_path)
        
        # Process the transcript
        summary_result = await process_transcript(transcript)
        
        return {
            "status": "success",
            "transcript": transcript,
            "summary": summary_result
        }
    
    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")

@app.post("/process-text", response_model=MeetingSummary)
async def process_text(input_data: TextInput):
    """
    Process text transcript
    """
    try:
        logger.info(f"Processing text input. Length: {len(input_data.text)} characters")
        
        if len(input_data.text.strip()) < 50:
            raise HTTPException(status_code=400, detail="Text input too short for meaningful analysis")
        
        if len(input_data.text) > settings.MAX_TRANSCRIPT_LENGTH:
            raise HTTPException(status_code=400, detail=f"Text input too long. Maximum {settings.MAX_TRANSCRIPT_LENGTH} characters allowed")
        
        result = await process_transcript(input_data.text)
        return result
    except Exception as e:
        logger.error(f"Error processing text: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")

async def process_transcript(transcript: str) -> MeetingSummary:
    """
    Process transcript to extract summary, tasks, and action points
    """
    try:
        logger.info("Starting transcript processing...")
        
        # Run all processing tasks concurrently for better performance
        summary_task = text_summarizer.summarize(
            transcript, 
            max_length=settings.DEFAULT_SUMMARY_LENGTH,
            min_length=settings.MIN_SUMMARY_LENGTH
        )
        tasks_task = task_extractor.extract_tasks(transcript)
        action_points_task = task_extractor.extract_action_points(transcript)
        participants_task = task_extractor.extract_participants(transcript)
        
        # Wait for all tasks to complete
        summary, tasks, action_points, participants = await asyncio.gather(
            summary_task,
            tasks_task,
            action_points_task,
            participants_task
        )
        
        logger.info(f"Processing completed: {len(tasks)} tasks, {len(action_points)} action points, {len(participants)} participants")
        
        # Calculate confidence score
        confidence = calculate_confidence_score(transcript, summary, tasks)
        
        return MeetingSummary(
            summary=summary,
            tasks=tasks,
            action_points=action_points,
            participants=participants,
            meeting_date=datetime.now().strftime("%B %d, %Y"),
            confidence_score=confidence
        )
    
    except Exception as e:
        logger.error(f"Error in transcript processing: {e}")
        raise Exception(f"Error in transcript processing: {str(e)}")

def calculate_confidence_score(transcript: str, summary: str, tasks: List[Task]) -> float:
    """
    Calculate confidence score based on processing results
    """
    score = 0.0
    
    # Base score for having content
    if len(transcript) > 100:
        score += 0.3
    
    if len(summary) > 50:
        score += 0.3
    
    if len(tasks) > 0:
        score += 0.2
    
    # Additional scoring based on content quality
    if any(word in transcript.lower() for word in ['action', 'task', 'deadline', 'assign']):
        score += 0.1
    
    if any(word in transcript.lower() for word in ['meeting', 'discuss', 'decision', 'next']):
        score += 0.1
    
    return min(score, 1.0)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=settings.API_HOST, 
        port=settings.API_PORT,
        log_level="info"
    )