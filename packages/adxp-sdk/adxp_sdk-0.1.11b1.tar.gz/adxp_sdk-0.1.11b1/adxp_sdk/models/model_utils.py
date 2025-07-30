import uuid

def is_valid_uuid(val: str) -> bool:
    """
    Check if the given string is a valid UUID.
    Args:
        val (str): The string to check.
    Returns:
        bool: True if valid UUID, False otherwise.
    """
    try:
        uuid_obj = uuid.UUID(val)
        return str(uuid_obj) == val
    except (ValueError, AttributeError, TypeError):
        return False 