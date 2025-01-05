import sys

import regex  # Using regex instead of re for better Unicode support


def is_hebrew(text: str) -> bool:
    """Check if text contains Hebrew characters."""
    hebrew_pattern = regex.compile(r'[\p{Hebrew}]')
    return bool(hebrew_pattern.search(text))

def format_hebrew(text: str) -> str:
    """
    Format Hebrew text for display, handling both terminal and exe environments.
    Only reverses text containing Hebrew characters.
    """
    if getattr(sys, 'frozen', False):
        # Running as exe - leave text as is
        return text
    
    # Running in terminal
    # Split by spaces to preserve word order
    words = text.split()
    
    # Process each word: reverse only if contains Hebrew
    formatted_words = []
    for word in words:
        if word.isdigit():
            formatted_words.append(word)
        elif is_hebrew(word):
            formatted_words.append(word[::-1])
        else:
            formatted_words.append(word)
    
    # For text containing Hebrew, reverse the order of words
    if any(is_hebrew(word) for word in words):
        formatted_words.reverse()
    
    return ' '.join(formatted_words) 