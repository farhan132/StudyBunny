"""
StudyBunny Features Module
Contains integrations and advanced features for the StudyBunny application
"""

from .canvas import CanvasIntegrator, sync_canvas_homework
from .canvas_models import (
    CanvasCourse, 
    CanvasAssignment, 
    CanvasAssignmentGroup,
    StudyBunnyTask,
    CanvasTaskConverter
)
from .canvas_utils import (
    CanvasAPIClient,
    CanvasDataProcessor,
    CanvasDataFilter,
    CanvasSync,
    CanvasAPIError
)
from .canvas_config import CanvasConfig, extract_credit_hours

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
