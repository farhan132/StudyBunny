"""
Simple intensity utility for StudyBunny
"""
from django.conf import settings


def get_intensity():
    """
    Get the current global intensity value
    
    Returns:
        float: Intensity value between 0.0 and 1.0
    """
    return getattr(settings, 'STUDYBUNNY_INTENSITY', 0.7)


def set_intensity(value):
    """
    Set the global intensity value
    Note: This only changes the value in memory, not in settings.py
    For permanent changes, modify STUDYBUNNY_INTENSITY in settings.py
    
    Args:
        value (float): Intensity value between 0.0 and 1.0
    """
    if not 0.0 <= value <= 1.0:
        raise ValueError("Intensity must be between 0.0 and 1.0")
    
    # This would require a more complex implementation to persist
    # For now, just update the settings object
    settings.STUDYBUNNY_INTENSITY = value
