"""
Validators utilitaires (téléphone, Excel, etc.).
"""
import re
from typing import Optional

import phonenumbers
from phonenumbers import NumberParseException


def validate_phone_number(phone: str, default_region: str = "SN") -> bool:
    """
    Valider un numéro de téléphone avec phonenumbers library.

    Args:
        phone: Numéro de téléphone à valider
        default_region: Région par défaut (code ISO, ex: "SN" pour Sénégal)

    Returns:
        True si valide, False sinon

    Examples:
        >>> validate_phone_number("+221771234567")
        True
        >>> validate_phone_number("771234567", "SN")
        True
        >>> validate_phone_number("invalid")
        False
    """
    if not phone:
        return False

    try:
        parsed = phonenumbers.parse(phone, default_region)
        return phonenumbers.is_valid_number(parsed)
    except NumberParseException:
        return False


def format_phone_number(phone: str, default_region: str = "SN") -> Optional[str]:
    """
    Formater un numéro de téléphone au format international.

    Args:
        phone: Numéro à formater
        default_region: Région par défaut

    Returns:
        Numéro formaté (ex: "+221771234567") ou None si invalide

    Examples:
        >>> format_phone_number("771234567", "SN")
        "+221771234567"
        >>> format_phone_number("+221 77 123 45 67")
        "+221771234567"
    """
    if not phone:
        return None

    try:
        parsed = phonenumbers.parse(phone, default_region)
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        return None
    except NumberParseException:
        return None


def validate_ninea(ninea: str) -> bool:
    """
    Valider un numéro NINEA sénégalais (format basique).

    NINEA = Numéro d'Identification National des Entreprises et Associations
    Format attendu: 7 à 10 chiffres

    Args:
        ninea: Numéro NINEA à valider

    Returns:
        True si le format est valide, False sinon

    Examples:
        >>> validate_ninea("1234567")
        True
        >>> validate_ninea("ABC123")
        False
    """
    if not ninea:
        return False

    # Format: 7 à 10 chiffres
    pattern = r'^\d{7,10}$'
    return bool(re.match(pattern, ninea))


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    Valider la force d'un mot de passe.

    Critères:
    - Au moins 8 caractères
    - Au moins 1 majuscule
    - Au moins 1 minuscule
    - Au moins 1 chiffre
    - Au moins 1 caractère spécial (optionnel mais recommandé)

    Args:
        password: Mot de passe à valider

    Returns:
        Tuple (is_valid, error_message)

    Examples:
        >>> validate_password_strength("Motdepasse123!")
        (True, None)
        >>> validate_password_strength("weak")
        (False, "Le mot de passe doit contenir au moins 8 caractères")
    """
    if len(password) < 8:
        return False, "Le mot de passe doit contenir au moins 8 caractères"

    if not re.search(r'[A-Z]', password):
        return False, "Le mot de passe doit contenir au moins une majuscule"

    if not re.search(r'[a-z]', password):
        return False, "Le mot de passe doit contenir au moins une minuscule"

    if not re.search(r'\d', password):
        return False, "Le mot de passe doit contenir au moins un chiffre"

    # Optionnel: vérifier caractère spécial
    # if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
    #     return False, "Le mot de passe doit contenir au moins un caractère spécial"

    return True, None
