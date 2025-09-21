"""
Intensity utility functions for StudyBunny
"""
from django.conf import settings
from typing import Dict, Any, Tuple
from datetime import date, timedelta


def get_intensity() -> float:
    """
    Get the current global intensity value from the database
    
    Returns:
        float: Intensity value between 0.0 and 1.0
    """
    try:
        from .models import GlobalIntensity
        return GlobalIntensity.get_current_intensity()
    except Exception as e:
        # If database access fails, fall back to settings
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to load intensity from database: {e}")
        return getattr(settings, 'STUDYBUNNY_INTENSITY', 0.7)


def set_intensity(value: float) -> None:
    """
    Set the global intensity value in the database
    
    Args:
        value (float): Intensity value between 0.0 and 1.0
        
    Raises:
        ValueError: If value is not between 0.0 and 1.0
    """
    if not 0.0 <= value <= 1.0:
        raise ValueError("Intensity must be between 0.0 and 1.0")
    
    try:
        from .models import GlobalIntensity
        GlobalIntensity.set_intensity(value)
        # Also update settings in memory for immediate use
        settings.STUDYBUNNY_INTENSITY = value
    except Exception as e:
        # If database access fails, just update settings in memory
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to save intensity to database: {e}")
        settings.STUDYBUNNY_INTENSITY = value


def get_intensity_info() -> Dict[str, Any]:
    """
    Get comprehensive intensity information
    
    Returns:
        Dict containing intensity details and impact
    """
    intensity = get_intensity()
    
    # Calculate intensity impact factors
    intensityXcap = intensity * 2/5 + 3/5 * (2 * intensity - intensity**2)
    intensityY = min(0.95, (2 * intensity - intensity**2))
    average_intensity = (intensityXcap + intensityY) / 2
    
    return {
        'current_intensity': intensity,
        'intensity_level': _get_intensity_level(intensity),
        'intensityXcap': intensityXcap,
        'intensityY': intensityY,
        'average_intensity': average_intensity,
        'description': _get_intensity_description(intensity),
        'impact_factors': {
            'time_efficiency': intensity,  # Higher intensity = more efficient time usage
            'task_capacity': intensity,    # Higher intensity = more tasks per day
            'priority_weight': 1.0 + intensity,  # Higher intensity = more weight on priority
            'free_time_multiplier': 0.3 + (intensity * 0.7)  # Range: 0.3 to 1.0
        }
    }


def _get_intensity_level(intensity: float) -> str:
    """
    Get human-readable intensity level
    
    Args:
        intensity: Intensity value (0.0 to 1.0)
        
    Returns:
        str: Intensity level description
    """
    if intensity < 0.2:
        return "Very Low"
    elif intensity < 0.4:
        return "Low"
    elif intensity < 0.6:
        return "Medium"
    elif intensity < 0.8:
        return "High"
    else:
        return "Very High"


def _get_intensity_description(intensity: float) -> str:
    """
    Get detailed description of intensity impact
    
    Args:
        intensity: Intensity value (0.0 to 1.0)
        
    Returns:
        str: Description of how intensity affects the system
    """
    if intensity < 0.2:
        return "Relaxed pace - minimal time pressure, comfortable scheduling"
    elif intensity < 0.4:
        return "Gentle pace - low time pressure, flexible scheduling"
    elif intensity < 0.6:
        return "Balanced pace - moderate time pressure, balanced scheduling"
    elif intensity < 0.8:
        return "Active pace - high time pressure, efficient scheduling"
    else:
        return "Intense pace - maximum time pressure, aggressive scheduling"


def calculate_intensity_for_completion(target_completion_rate: float) -> float:
    """
    Calculate required intensity to achieve target completion rate
    
    Args:
        target_completion_rate: Target completion rate (0.0 to 1.0)
        
    Returns:
        float: Required intensity (0.0 to 1.0)
    """
    if not 0.0 <= target_completion_rate <= 1.0:
        raise ValueError("Target completion rate must be between 0.0 and 1.0")
    
    # Simple linear relationship - can be made more complex
    # Higher completion rate requires higher intensity
    return min(1.0, target_completion_rate * 1.2)


def get_intensity_recommendations() -> Dict[str, Any]:
    """
    Get intensity recommendations based on current system state
    
    Returns:
        Dict containing intensity recommendations
    """
    current_intensity = get_intensity()
    
    recommendations = {
        'current_intensity': current_intensity,
        'recommendations': []
    }
    
    # Add recommendations based on intensity level
    if current_intensity < 0.3:
        recommendations['recommendations'].append({
            'type': 'increase',
            'suggested_intensity': 0.5,
            'reason': 'Low intensity may lead to incomplete tasks',
            'impact': 'Will increase task completion rate'
        })
    elif current_intensity > 0.8:
        recommendations['recommendations'].append({
            'type': 'decrease',
            'suggested_intensity': 0.6,
            'reason': 'Very high intensity may cause burnout',
            'impact': 'Will reduce stress while maintaining efficiency'
        })
    else:
        recommendations['recommendations'].append({
            'type': 'maintain',
            'suggested_intensity': current_intensity,
            'reason': 'Current intensity is well-balanced',
            'impact': 'Continue with current settings'
        })
    
    return recommendations


def validate_intensity_range(intensity: float) -> bool:
    """
    Validate if intensity is within acceptable range
    
    Args:
        intensity: Intensity value to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    return 0.0 <= intensity <= 1.0


def get_intensity_history() -> Dict[str, Any]:
    """
    Get intensity usage history (placeholder for future implementation)
    
    Returns:
        Dict containing intensity history information
    """
    return {
        'message': 'Intensity history tracking not yet implemented',
        'current_intensity': get_intensity(),
        'suggestion': 'Consider implementing intensity change logging for analytics'
    }


def reset_intensity_to_default() -> float:
    """
    Reset intensity to default value
    
    Returns:
        float: The default intensity value
    """
    default_intensity = 0.7
    set_intensity(default_intensity)
    return default_intensity


def get_intensity_impact_on_free_time(target_date: date = None) -> Dict[str, Any]:
    """
    Calculate how intensity affects free time calculation
    
    Args:
        target_date: Date to calculate for (defaults to today)
        
    Returns:
        Dict containing free time impact information
    """
    from .models import TimeCalculation, currentTimeInHours
    from django.utils import timezone
    
    if target_date is None:
        target_date = timezone.now().date()
    
    # Get current intensity
    current_intensity = get_intensity()
    
    # Calculate free time with current intensity
    current_free_time = TimeCalculation.get_free_d(target_date)
    
    # Calculate free time with different intensities for comparison
    intensities_to_test = [0.1, 0.3, 0.5, 0.7, 0.9]
    free_time_comparison = {}
    
    original_intensity = get_intensity()
    
    try:
        for test_intensity in intensities_to_test:
            set_intensity(test_intensity)
            free_time = TimeCalculation.get_free_d(target_date)
            free_time_comparison[test_intensity] = {
                'free_time': free_time,
                'free_time_hours': free_time.total_seconds() / 3600,
                'percentage_of_day': (free_time.total_seconds() / (24 * 3600)) * 100
            }
    finally:
        set_intensity(original_intensity)
    
    return {
        'target_date': target_date,
        'current_intensity': current_intensity,
        'current_free_time': {
            'free_time': current_free_time,
            'free_time_hours': current_free_time.total_seconds() / 3600,
            'percentage_of_day': (current_free_time.total_seconds() / (24 * 3600)) * 100
        },
        'comparison': free_time_comparison,
        'recommendation': 'Higher intensity generally results in more efficient time usage'
    }
