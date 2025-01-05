from src.address.utils import normalize_hebrew_text

def test_normalize_hebrew_text():
    test_cases = [
        ('בית"ר', 'ביתר'),
        ('רח\' המלך', 'רח המלך'),
        ('שד"ל', 'שדל'),
        ('  multiple   spaces  ', 'multiple spaces')
    ]
    
    for input_text, expected in test_cases:
        assert normalize_hebrew_text(input_text) == expected 