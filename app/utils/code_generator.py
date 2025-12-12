"""Room code generator"""
import random
import string


def generate_room_code(length: int = 6) -> str:
    """
    Generate a random room code.
    
    Uses Base36 (0-9, A-Z) excluding confusing characters (0, O, 1, I, L)
    to create a unique, human-readable room code.
    
    Args:
        length: Length of the code (default: 6)
        
    Returns:
        Random alphanumeric code
    """
    # Exclude confusing characters
    chars = '23456789ABCDEFGHJKMNPQRSTUVWXYZ'
    return ''.join(random.choice(chars) for _ in range(length))


def is_valid_room_code(code: str) -> bool:
    """
    Validate room code format.
    
    Args:
        code: Room code to validate
        
    Returns:
        True if valid, False otherwise
    """
    if len(code) != 6:
        return False
    
    valid_chars = '23456789ABCDEFGHJKMNPQRSTUVWXYZ'
    return all(c in valid_chars for c in code.upper())
