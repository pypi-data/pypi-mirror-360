"""Utility functions for Bible CLI."""

import re
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
import os


def parse_reference(reference: str) -> Optional[Tuple[str, int, Optional[int], Optional[int]]]:
    """Parse Bible reference string into components.
    
    Args:
        reference: Reference string like "John 3:16", "Genesis 1:1-5", "Psalms 23"
        
    Returns:
        Tuple of (book, chapter, start_verse, end_verse) or None if invalid
    """
    # Remove extra whitespace and normalize
    reference = reference.strip()
    
    # Common patterns for Bible references
    patterns = [
        # Book Chapter:Verse-Verse (e.g., "John 3:16-17")
        r'^(\d?\s?[A-Za-z]+(?:\s+[A-Za-z]+)*)\s+(\d+):(\d+)-(\d+)$',
        # Book Chapter:Verse (e.g., "John 3:16")
        r'^(\d?\s?[A-Za-z]+(?:\s+[A-Za-z]+)*)\s+(\d+):(\d+)$',
        # Book Chapter (e.g., "John 3")
        r'^(\d?\s?[A-Za-z]+(?:\s+[A-Za-z]+)*)\s+(\d+)$',
    ]
    
    for pattern in patterns:
        match = re.match(pattern, reference)
        if match:
            groups = match.groups()
            book = groups[0].strip()
            chapter = int(groups[1])
            
            if len(groups) == 4:  # Range format
                start_verse = int(groups[2])
                end_verse = int(groups[3])
                return (book, chapter, start_verse, end_verse)
            elif len(groups) == 3:  # Single verse
                verse = int(groups[2])
                return (book, chapter, verse, verse)
            else:  # Chapter only
                return (book, chapter, None, None)
    
    return None


def normalize_book_name(book_name: str) -> str:
    """Normalize book name for consistent matching."""
    # Remove extra whitespace
    book_name = book_name.strip()
    
    # Common abbreviations and variations
    book_mappings = {
        # Old Testament
        'gen': 'Genesis',
        'gn': 'Genesis',
        'ex': 'Exodus',
        'exod': 'Exodus',
        'lev': 'Leviticus',
        'lv': 'Leviticus',
        'num': 'Numbers',
        'nm': 'Numbers',
        'deut': 'Deuteronomy',
        'dt': 'Deuteronomy',
        'josh': 'Joshua',
        'jos': 'Joshua',
        'judg': 'Judges',
        'jdg': 'Judges',
        'rt': 'Ruth',
        '1sam': '1 Samuel',
        '1s': '1 Samuel',
        '2sam': '2 Samuel',
        '2s': '2 Samuel',
        '1king': '1 Kings',
        '1k': '1 Kings',
        '2king': '2 Kings',
        '2k': '2 Kings',
        '1chr': '1 Chronicles',
        '1chron': '1 Chronicles',
        '2chr': '2 Chronicles',
        '2chron': '2 Chronicles',
        'ezr': 'Ezra',
        'neh': 'Nehemiah',
        'est': 'Esther',
        'ps': 'Psalms',
        'psa': 'Psalms',
        'psalm': 'Psalms',
        'prov': 'Proverbs',
        'pr': 'Proverbs',
        'eccl': 'Ecclesiastes',
        'ecc': 'Ecclesiastes',
        'song': 'Song of Solomon',
        'sos': 'Song of Solomon',
        'isa': 'Isaiah',
        'is': 'Isaiah',
        'jer': 'Jeremiah',
        'lam': 'Lamentations',
        'ezek': 'Ezekiel',
        'ez': 'Ezekiel',
        'dan': 'Daniel',
        'dn': 'Daniel',
        'hos': 'Hosea',
        'joel': 'Joel',
        'jl': 'Joel',
        'amos': 'Amos',
        'am': 'Amos',
        'obad': 'Obadiah',
        'ob': 'Obadiah',
        'jonah': 'Jonah',
        'jon': 'Jonah',
        'mic': 'Micah',
        'nah': 'Nahum',
        'hab': 'Habakkuk',
        'zeph': 'Zephaniah',
        'zep': 'Zephaniah',
        'hag': 'Haggai',
        'zech': 'Zechariah',
        'zec': 'Zechariah',
        'mal': 'Malachi',
        
        # New Testament
        'matt': 'Matthew',
        'mt': 'Matthew',
        'mark': 'Mark',
        'mk': 'Mark',
        'luke': 'Luke',
        'lk': 'Luke',
        'john': 'John',
        'jn': 'John',
        'acts': 'Acts',
        'ac': 'Acts',
        'rom': 'Romans',
        'ro': 'Romans',
        '1cor': '1 Corinthians',
        '1co': '1 Corinthians',
        '2cor': '2 Corinthians',
        '2co': '2 Corinthians',
        'gal': 'Galatians',
        'ga': 'Galatians',
        'eph': 'Ephesians',
        'ep': 'Ephesians',
        'phil': 'Philippians',
        'php': 'Philippians',
        'col': 'Colossians',
        '1thess': '1 Thessalonians',
        '1th': '1 Thessalonians',
        '2thess': '2 Thessalonians',
        '2th': '2 Thessalonians',
        '1tim': '1 Timothy',
        '1ti': '1 Timothy',
        '2tim': '2 Timothy',
        '2ti': '2 Timothy',
        'tit': 'Titus',
        'philem': 'Philemon',
        'phm': 'Philemon',
        'heb': 'Hebrews',
        'james': 'James',
        'jas': 'James',
        '1pet': '1 Peter',
        '1pe': '1 Peter',
        '2pet': '2 Peter',
        '2pe': '2 Peter',
        '1john': '1 John',
        '1jn': '1 John',
        '2john': '2 John',
        '2jn': '2 John',
        '3john': '3 John',
        '3jn': '3 John',
        'jude': 'Jude',
        'jud': 'Jude',
        'rev': 'Revelation',
        'revelation': 'Revelation',
    }
    
    # Check for exact match first
    normalized = book_name.lower().replace(' ', '')
    if normalized in book_mappings:
        return book_mappings[normalized]
    
    # Check for partial matches
    for abbr, full_name in book_mappings.items():
        if normalized.startswith(abbr) or abbr.startswith(normalized):
            return full_name
    
    # Return original if no match found
    return book_name


def format_reference(book: str, chapter: int, verse: Optional[int] = None, 
                    end_verse: Optional[int] = None) -> str:
    """Format a Bible reference string."""
    if verse is None:
        return f"{book} {chapter}"
    elif end_verse is None or verse == end_verse:
        return f"{book} {chapter}:{verse}"
    else:
        return f"{book} {chapter}:{verse}-{end_verse}"


def clean_text(text: str) -> str:
    """Clean and normalize text for display."""
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Fix common formatting issues
    text = text.replace('  ', ' ')  # Double spaces
    text = text.replace(' ,', ',')  # Space before comma
    text = text.replace(' .', '.')  # Space before period
    text = text.replace(' ;', ';')  # Space before semicolon
    text = text.replace(' :', ':')  # Space before colon
    
    return text.strip()


def highlight_text(text: str, query: str, case_sensitive: bool = False) -> str:
    """Highlight search query in text using rich markup."""
    if not query:
        return text
    
    if case_sensitive:
        highlighted = text.replace(query, f"[bold yellow]{query}[/bold yellow]")
    else:
        # Use regex for case-insensitive replacement
        pattern = re.escape(query)
        highlighted = re.sub(pattern, f"[bold yellow]{query}[/bold yellow]", text, flags=re.IGNORECASE)
    
    return highlighted


def get_data_directory() -> Path:
    """Get the data directory for Bible CLI."""
    data_dir = Path.home() / ".local" / "share" / "bible-cli"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_config_directory() -> Path:
    """Get the config directory for Bible CLI."""
    config_dir = Path.home() / ".config" / "bible-cli"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_cache_directory() -> Path:
    """Get the cache directory for Bible CLI."""
    cache_dir = Path.home() / ".cache" / "bible-cli"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def format_time_ago(timestamp) -> str:
    """Format timestamp as human-readable time ago."""
    from datetime import datetime, timezone
    
    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp)
    
    now = datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    
    delta = now - timestamp
    
    if delta.days > 0:
        return f"{delta.days} day{'s' if delta.days != 1 else ''} ago"
    elif delta.seconds > 3600:
        hours = delta.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif delta.seconds > 60:
        minutes = delta.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "just now"


def extract_keywords(text: str, min_length: int = 3, max_keywords: int = 10) -> List[str]:
    """Extract keywords from text for searching."""
    # Common stop words
    stop_words = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
        'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
        'to', 'was', 'were', 'will', 'with', 'his', 'her', 'him', 'she',
        'they', 'their', 'them', 'this', 'these', 'those', 'you', 'your',
        'i', 'me', 'my', 'we', 'our', 'us', 'but', 'not', 'no', 'all',
        'any', 'can', 'had', 'have', 'if', 'into', 'may', 'more', 'must',
        'said', 'shall', 'should', 'so', 'than', 'up', 'who', 'would'
    }
    
    # Extract words (remove punctuation)
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    
    # Filter words
    keywords = []
    for word in words:
        if (len(word) >= min_length and 
            word not in stop_words and 
            word not in keywords):
            keywords.append(word)
    
    return keywords[:max_keywords]


def validate_translation(translation: str) -> bool:
    """Validate if translation code is supported."""
    supported_translations = {
        'NIV', 'KJV', 'ESV', 'NASB', 'NLT', 'NKJV', 'CSB', 'HCSB',
        'BBE', 'WEB', 'YLT', 'ASV', 'NET', 'MSG', 'AMP', 'VOICE'
    }
    return translation.upper() in supported_translations


def create_backup(file_path: Path, backup_dir: Optional[Path] = None) -> Path:
    """Create a backup of a file."""
    if backup_dir is None:
        backup_dir = file_path.parent / "backups"
    
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
    backup_path = backup_dir / backup_name
    
    import shutil
    shutil.copy2(file_path, backup_path)
    return backup_path


def setup_logging(log_level: str = "INFO", log_file: Optional[Path] = None) -> None:
    """Setup logging configuration."""
    import logging
    from rich.logging import RichHandler
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(message)s",
        handlers=[
            RichHandler(rich_tracebacks=True, markup=True),
            logging.FileHandler(log_file) if log_file else logging.NullHandler()
        ]
    )


def get_system_info() -> Dict[str, Any]:
    """Get system information for debugging."""
    import platform
    import sys
    
    return {
        "platform": platform.platform(),
        "python_version": sys.version,
        "python_executable": sys.executable,
        "architecture": platform.architecture(),
        "processor": platform.processor(),
        "machine": platform.machine(),
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
    }


def estimate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """Estimate reading time in seconds."""
    word_count = len(text.split())
    minutes = word_count / words_per_minute
    return int(minutes * 60)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length."""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def is_valid_url(url: str) -> bool:
    """Check if URL is valid."""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None