"""
StudyBunny Features Module
Contains integrations and advanced features for the StudyBunny application
"""

# Import only when needed to avoid circular imports
def get_canvas_integrator():
    from .canvas import CanvasIntegrator
    return CanvasIntegrator

def get_sync_canvas_homework():
    from .canvas import sync_canvas_homework
    return sync_canvas_homework

def get_canvas_models():
    from .canvas_models import (
        CanvasCourse, 
        CanvasAssignment, 
        CanvasAssignmentGroup,
        StudyBunnyTask,
        CanvasTaskConverter
    )
    return {
        'CanvasCourse': CanvasCourse,
        'CanvasAssignment': CanvasAssignment,
        'CanvasAssignmentGroup': CanvasAssignmentGroup,
        'StudyBunnyTask': StudyBunnyTask,
        'CanvasTaskConverter': CanvasTaskConverter
    }

def get_canvas_utils():
    from .canvas_utils import (
        CanvasAPIClient,
        CanvasDataProcessor,
        CanvasDataFilter,
        CanvasSync,
        CanvasAPIError
    )
    return {
        'CanvasAPIClient': CanvasAPIClient,
        'CanvasDataProcessor': CanvasDataProcessor,
        'CanvasDataFilter': CanvasDataFilter,
        'CanvasSync': CanvasSync,
        'CanvasAPIError': CanvasAPIError
    }

def get_canvas_config():
    from .canvas_config import CanvasConfig, extract_credit_hours
    return CanvasConfig, extract_credit_hours

__all__ = [
    # Main integration
    'CanvasIntegrator',
    'sync_canvas_homework',
    
    # Data models
    'CanvasCourse',
    'CanvasAssignment', 
    'CanvasAssignmentGroup',
    'StudyBunnyTask',
    'CanvasTaskConverter',
    
    # API utilities
    'CanvasAPIClient',
    'CanvasDataProcessor',
    'CanvasDataFilter',
    'CanvasSync',
    'CanvasAPIError',
    
    # Configuration
    'CanvasConfig',
    'extract_credit_hours',
]
