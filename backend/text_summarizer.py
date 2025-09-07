"""
Text summarization module using various NLP models
"""

from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from typing import List, Dict, Optional
import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.frequency import FreqDist
import logging

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    logger.info("Downloading NLTK punkt tokenizer")
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    logger.info("Downloading NLTK stopwords")
    nltk.download('stopwords')

class TextSummarizer:
    def __init__(self, model_type: str = "huggingface"):
        self.model_type = model_type
        logger.info(f"Initializing TextSummarizer with model type: {model_type}")
        
        if model_type == "huggingface":
            try:
                # Initialize HuggingFace BART model for summarization
                logger.info("Loading BART model for summarization")
                self.summarizer = pipeline(
                    "summarization",
                    model="facebook/bart-large-cnn",
                    tokenizer="facebook/bart-large-cnn",
                    device=-1,  # Use CPU
                    framework="pt"
                )
                logger.info("BART model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load BART model: {e}")
                # Fallback to smaller model
                try:
                    logger.info("Falling back to DistilBART model")
                    self.summarizer = pipeline(
                        "summarization",
                        model="sshleifer/distilbart-cnn-12-6",
                        device=-1
                    )
                except Exception as e2:
                    logger.error(f"Failed to load fallback model: {e2}")
                    self.summarizer = None
        
        elif model_type == "t5":
            try:
                # Alternative: T5 model
                self.model_name = "t5-small"
                logger.info(f"Loading T5 model: {self.model_name}")
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
                self.summarizer = pipeline(
                    "summarization",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    device=-1
                )
                logger.info("T5 model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load T5 model: {e}")
                self.summarizer = None
        
        else:
            self.summarizer = None
        
        try:
            self.stop_words = set(stopwords.words('english'))
        except Exception as e:
            logger.warning(f"Failed to load stopwords: {e}")
            self.stop_words = set()
    
    async def summarize(self, text: str, max_length: int = 150, min_length: int = 50) -> str:
        """
        Generate summary of the input text
        """
        try:
            logger.info(f"Starting summarization. Text length: {len(text)} characters")
            
            # Clean and preprocess text
            cleaned_text = self._preprocess_text(text)
            
            if len(cleaned_text.split()) < 50:
                logger.warning("Text too short for meaningful summarization")
                return "Text too short for meaningful summarization."
            
            # Use model-based summarization if available
            if self.summarizer:
                summary = await self._huggingface_summarize(cleaned_text, max_length, min_length)
                logger.info(f"Model-based summarization completed. Summary length: {len(summary)} characters")
                return summary
            else:
                logger.info("Using extractive summarization fallback")
                return self._extractive_summarization(cleaned_text)
        
        except Exception as e:
            # Fallback to extractive summarization
            logger.error(f"Model summarization failed: {e}")
            logger.info("Falling back to extractive summarization")
            return self._extractive_summarization(text)
    
    async def _huggingface_summarize(self, text: str, max_length: int, min_length: int) -> str:
        """
        Summarize using HuggingFace models
        """
        try:
            # Handle long text by chunking
            max_chunk_length = 1000  # Conservative chunk size
            if len(text) > max_chunk_length:
                logger.info("Text is long, chunking for processing")
                chunks = self._chunk_text(text, max_chunk_length)
                summaries = []
                
                for i, chunk in enumerate(chunks):
                    logger.info(f"Processing chunk {i+1}/{len(chunks)}")
                    result = self.summarizer(
                        chunk,
                        max_length=min(max_length // len(chunks), 100),
                        min_length=min(min_length // len(chunks), 20),
                        do_sample=False,
                        clean_up_tokenization_spaces=True
                    )
                    summaries.append(result[0]['summary_text'])
                
                # Combine chunk summaries
                combined_summary = " ".join(summaries)
                
                # Summarize the combined summary if it's still too long
                if len(combined_summary.split()) > max_length:
                    logger.info("Combined summary still long, doing final summarization")
                    final_result = self.summarizer(
                        combined_summary,
                        max_length=max_length,
                        min_length=min_length,
                        do_sample=False,
                        clean_up_tokenization_spaces=True
                    )
                    return final_result[0]['summary_text']
                
                return combined_summary
            
            else:
                result = self.summarizer(
                    text,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=False,
                    clean_up_tokenization_spaces=True
                )
                return result[0]['summary_text']
        
        except Exception as e:
            logger.error(f"HuggingFace summarization error: {e}")
            raise Exception(f"HuggingFace summarization failed: {e}")
    
    def _extractive_summarization(self, text: str, num_sentences: int = 3) -> str:
        """
        Fallback extractive summarization using frequency analysis
        """
        try:
            logger.info("Performing extractive summarization")
            
            sentences = sent_tokenize(text)
            if len(sentences) <= num_sentences:
                return text
                
            words = word_tokenize(text.lower())
            
            # Remove stopwords and punctuation
            words = [word for word in words if word.isalnum() and word not in self.stop_words]
            
            if not words:
                return text[:500] + "..." if len(text) > 500 else text
            
            # Calculate word frequencies
            word_freq = FreqDist(words)
            
            # Score sentences based on word frequencies
            sentence_scores = {}
            for sentence in sentences:
                sentence_words = word_tokenize(sentence.lower())
                sentence_words = [word for word in sentence_words if word.isalnum()]
                
                score = 0
                word_count = 0
                for word in sentence_words:
                    if word in word_freq:
                        score += word_freq[word]
                        word_count += 1
                
                if word_count > 0:
                    sentence_scores[sentence] = score / word_count
            
            if not sentence_scores:
                return text[:500] + "..." if len(text) > 500 else text
            
            # Select top sentences
            top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
            summary_sentences = [sentence for sentence, score in top_sentences[:num_sentences]]
            
            # Maintain original order
            summary = []
            for sentence in sentences:
                if sentence in summary_sentences:
                    summary.append(sentence)
            
            result = " ".join(summary)
            logger.info(f"Extractive summarization completed. Summary length: {len(result)} characters")
            return result
        
        except Exception as e:
            logger.error(f"Extractive summarization failed: {e}")
            return f"Summarization failed: {e}"
    
    def _preprocess_text(self, text: str) -> str:
        """
        Clean and preprocess text for better summarization
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove speaker labels (e.g., "John:", "Speaker 1:")
        text = re.sub(r'^[A-Za-z\s]+:\s*', '', text, flags=re.MULTILINE)
        
        # Remove timestamps (e.g., "[00:05:30]")
        text = re.sub(r'\[\d{2}:\d{2}:\d{2}\]', '', text)
        
        # Remove filler words and sounds
        filler_words = ['um', 'uh', 'er', 'ah', 'like', 'you know', 'so', 'well']
        for filler in filler_words:
            text = re.sub(rf'\b{filler}\b', '', text, flags=re.IGNORECASE)
        
        # Clean up multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _chunk_text(self, text: str, max_length: int) -> List[str]:
        """
        Split long text into manageable chunks
        """
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_length:
                current_chunk += " " + sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks