"""
Utilities for validation and normalization of user-provided data.
"""

def validate_name(name: str)-> bool:
    """
    Validates a given name.

    Args:
        name (str): Name to validate.
    """
    #Random fact: the shortest name ever registered is a single-lettered name ("J" a boy from India)
    if not name:
        return False
    else:
        return True
    
def validate_phone_number(phone: str)->bool:
    """
    Validates a given phone number.

    Args:
        phone (str): Phone number to validate.
    """
    #For semplicity this method only checks if the given phone number has 10 digits
    phone = phone.strip()
    if len(phone) != 10:
        return False
    for char in phone:
        if char not in ["1","2","3","4","5","6","7","8","9","0"]:
            return False
    return True

def _normalize_token(token: str) -> str:
    """
    Return the token with only its first letter upper-cased.

    Args:
        token (str): Raw token to normalize.
    """
    if not token:
        return ""
    return token[0].upper() + token[1:].lower()


def normalize_name(name: str) -> str:
    """
    Capitalize each part of the provided name.

    Args:
        name (str): Name string that may contain multiple parts.
    """
    if not name:
        return ""

    parts = [part for part in name.strip().split() if part]
    normalized_parts = [_normalize_token(part) for part in parts]
    return " ".join(normalized_parts)

def normalize_surname(surname: str):
    """
    Capitalize each part of the provided surname.

    Args:
        surname (str): Surname string that needs normalization.
    """
    if not surname:
        return ""

    parts = [part for part in surname.strip().split() if part]
    normalized_parts = [_normalize_token(part) for part in parts]
    return " ".join(normalized_parts)
