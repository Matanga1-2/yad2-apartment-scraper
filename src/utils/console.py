def prompt_yes_no(question: str) -> bool:
    """Prompt user for a yes/no response.
    
    Args:
        question: The question to ask
    Returns:
        bool: True if user answers yes, False if no
    """
    while True:
        response = input(f"{question} (y/n) ").lower().strip()
        if response in ('y', 'yes'):
            return True
        if response in ('n', 'no'):
            return False
        print("Please answer 'y' or 'n'") 