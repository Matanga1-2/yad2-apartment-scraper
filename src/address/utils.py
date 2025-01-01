def normalize_hebrew_text(text: str) -> str:
    """
    Normalize Hebrew text by removing special characters and diacritics.
    
    Args:
        text: The Hebrew text to normalize
        
    Returns:
        Normalized text string
    """
    # Remove quotes and special characters
    normalized = text.replace('"', '').replace('\'', '')
    # Remove Hebrew abbreviation marks
    normalized = normalized.replace('\"', '').replace('"', '')
    # Remove any double spaces
    normalized = ' '.join(normalized.split())
    return normalized.strip() 