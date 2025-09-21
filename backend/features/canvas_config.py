"""
Canvas API configuration and constants
"""
import os
from typing import Dict, Any


class CanvasConfig:
    """Configuration for Canvas API integration"""
    
    # Default Canvas instance URL
    DEFAULT_BASE_URL = "https://canvas.instructure.com"
    
    # API endpoints
    API_ENDPOINTS = {
        'courses': '/api/v1/courses',
        'assignments': '/api/v1/courses/{course_id}/assignments',
        'assignment_groups': '/api/v1/courses/{course_id}/assignment_groups',
        'user': '/api/v1/users/self',
        'enrollments': '/api/v1/courses/{course_id}/enrollments',
    }
    
    # Request parameters
    DEFAULT_PARAMS = {
        'per_page': 100,  # Max items per request
        'include[]': ['term', 'course_image', 'banner_image'],
    }
    
    # Assignment parameters
    ASSIGNMENT_PARAMS = {
        'per_page': 100,
        'include[]': ['submission', 'assignment_group'],
        'order_by': 'due_at',
    }
    
    # Time estimation defaults (in hours)
    TIME_ESTIMATES = {
        'default': 2.0,
        'quiz': 1.0,
        'homework': 3.0,
        'project': 8.0,
        'exam': 5.0,
        'paper': 6.0,
        'discussion': 1.5,
    }
    
    # Priority mappings
    PRIORITY_THRESHOLDS = {
        1: 1,   # Due in 1 day or less
        3: 2,   # Due in 3 days or less  
        7: 3,   # Due in 1 week or less
        14: 4,  # Due in 2 weeks or less
        999: 5, # Due later or no due date
    }
    
    @classmethod
    def get_api_token(cls) -> str:
        """Get Canvas API token from environment"""
        token = os.getenv('CANVAS_API_TOKEN')
        if not token:
            raise ValueError(
                "CANVAS_API_TOKEN not found in environment variables. "
                "Please set your Canvas API token in the .env file."
            )
        return token
    
    @classmethod
    def get_base_url(cls) -> str:
        """Get Canvas base URL from environment or use default"""
        return os.getenv('CANVAS_BASE_URL', cls.DEFAULT_BASE_URL)
    
    @classmethod
    def get_headers(cls) -> Dict[str, str]:
        """Get standard headers for Canvas API requests"""
        return {
            'Authorization': f'Bearer {cls.get_api_token()}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
    
    @classmethod
    def get_course_filters(cls) -> Dict[str, Any]:
        """Get filters for course enrollment"""
        return {
            'enrollment_state': 'active',
            'enrollment_type': 'student',
            'state[]': ['available', 'unpublished'],
        }


# Course code to credit hours mapping
COURSE_CREDIT_MAPPING = {
    # MIT course patterns
    '6.': 12,    # EECS courses (often 12 units)
    '18.': 12,   # Math courses  
    '8.': 12,    # Physics courses
    '7.': 12,    # Biology courses
    '5.': 12,    # Chemistry courses
    '2.': 12,    # Mechanical Engineering
    '3.': 12,    # Materials Science
    '4.': 12,    # Architecture
    '15.': 12,   # Management
    '16.': 12,   # Aeronautics
    '20.': 12,   # Biological Engineering
    '22.': 12,   # Nuclear Science
}

def extract_credit_hours(course_code: str) -> int:
    """
    Extract credit hours from MIT course code
    
    Args:
        course_code: Course code like "6.006", "18.600", etc.
        
    Returns:
        Estimated credit hours (MIT uses units, typically 12 per course)
    """
    if not course_code:
        return 12  # Default MIT course units
        
    # Look for department prefix
    for prefix, credits in COURSE_CREDIT_MAPPING.items():
        if course_code.startswith(prefix):
            return credits
            
    # Fallback: try to parse numeric pattern
    parts = course_code.split('.')
    if len(parts) >= 2:
        try:
            # Some courses encode difficulty/level in the number
            course_num = int(parts[1])
            if course_num >= 900:  # Graduate level
                return 12
            elif course_num >= 600:  # Advanced undergrad
                return 12  
            else:  # Intro/intermediate
                return 12
        except ValueError:
            pass
            
    return 12  # MIT default
