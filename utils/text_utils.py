"""
Text processing utilities.
"""
import re
import nltk
from typing import List
from pathlib import Path
from config.config import NLP_CONFIG
from utils.logger import setup_logger

logger = setup_logger(__name__)


def ensure_nltk_data():
    """Ensure required NLTK data is available (don't auto-download)."""
    # Add custom NLTK data path
    nltk_data_path = Path(NLP_CONFIG["nltk_data_path"])
    
    if str(nltk_data_path) not in nltk.data.path:
        nltk.data.path.insert(0, str(nltk_data_path))
    
    # Check if punkt_tab is available
    try:
        nltk.data.find('tokenizers/punkt_tab')
        logger.info("NLTK punkt_tab found")
    except LookupError:
        logger.warning("NLTK punkt_tab not found. Attempting download...")
        try:
            # Only download if absolutely necessary
            import ssl
            try:
                _create_unverified_https_context = ssl._create_unverified_context
            except AttributeError:
                pass
            else:
                ssl._create_default_https_context = _create_unverified_https_context
            
            nltk.download('punkt_tab', quiet=True, download_dir=str(nltk_data_path))
        except Exception as e:
            logger.error(f"Failed to download punkt_tab: {e}")
            raise RuntimeError(
                "NLTK punkt_tab is required. Please download manually:\n"
                "python -m nltk.downloader punkt_tab"
            )


# Ensure NLTK data on import
ensure_nltk_data()


def clean_text(text: str) -> str:
    """
    Clean text for processing.
    
    Args:
        text: Raw text string
    
    Returns:
        Cleaned text
    """
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Keep punctuation for sentence detection
    # Only remove excessive special characters
    text = re.sub(r'[^\w\s.,;!?\'-]', '', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def tokenize_sentences(text: str) -> List[str]:
    """
    Tokenize text into sentences using NLTK.
    
    Args:
        text: Text string
    
    Returns:
        List of sentences
    """
    try:
        sentences = nltk.sent_tokenize(text)
        return [s.strip() for s in sentences if s.strip()]
    except LookupError as e:
        logger.error(f"NLTK tokenizer not found: {e}")
        # Fallback: simple sentence splitting
        return _fallback_sentence_tokenize(text)
    except Exception as e:
        logger.error(f"Error tokenizing sentences: {e}")
        return _fallback_sentence_tokenize(text)


def _fallback_sentence_tokenize(text: str) -> List[str]:
    """
    Fallback sentence tokenizer (simple splitting).
    
    Args:
        text: Text string
    
    Returns:
        List of sentences
    """
    # Split by common sentence endings
    sentences = re.split(r'[.!?]+\s+', text)
    
    # Clean and filter empty sentences
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Re-add periods to sentences
    sentences = [s if s.endswith(('.', '!', '?')) else s + '.' for s in sentences]
    
    logger.warning("Using fallback sentence tokenizer")
    return sentences


def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    """
    Extract top keywords from text (simple frequency-based).
    
    Args:
        text: Text string
        top_n: Number of top keywords to return
    
    Returns:
        List of keywords
    """
    # Extract words (3+ characters)
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())
    
    # Common English stop words
    stop_words = {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 
        'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 
        'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 
        'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 
        'use', 'with', 'from', 'have', 'this', 'that', 'will', 'than',
        'been', 'were', 'said', 'each', 'which', 'their', 'there', 'would'
    }
    
    words = [w for w in words if w not in stop_words]
    
    # Count frequency
    from collections import Counter
    word_freq = Counter(words)
    
    return [word for word, _ in word_freq.most_common(top_n)]