"""
Canvas API utility functions and helpers
"""
import requests
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
import logging

from .canvas_config import CanvasConfig
from .canvas_models import CanvasCourse, CanvasAssignment, CanvasAssignmentGroup

logger = logging.getLogger(__name__)


class CanvasAPIError(Exception):
    """Custom exception for Canvas API errors"""
    pass


class CanvasAPIClient:
    """Low-level Canvas API client"""
    
    def __init__(self, api_token: str = None, base_url: str = None):
        self.api_token = api_token or CanvasConfig.get_api_token()
        self.base_url = base_url or CanvasConfig.get_base_url()
        self.session = requests.Session()
        self.session.headers.update(CanvasConfig.get_headers())
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a request to Canvas API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Canvas API request failed: {e}")
            raise CanvasAPIError(f"Failed to fetch from Canvas API: {e}")
    
    def get_courses(self) -> List[Dict[str, Any]]:
        """Get all active courses for the user"""
        params = {
            **CanvasConfig.DEFAULT_PARAMS,
            **CanvasConfig.get_course_filters()
        }
        return self._make_request(CanvasConfig.API_ENDPOINTS['courses'], params)
    
    def get_assignments(self, course_id: int) -> List[Dict[str, Any]]:
        """Get all assignments for a course"""
        endpoint = CanvasConfig.API_ENDPOINTS['assignments'].format(course_id=course_id)
        return self._make_request(endpoint, CanvasConfig.ASSIGNMENT_PARAMS)
    
    def get_assignment_groups(self, course_id: int) -> List[Dict[str, Any]]:
        """Get assignment groups for a course"""
        endpoint = CanvasConfig.API_ENDPOINTS['assignment_groups'].format(course_id=course_id)
        return self._make_request(endpoint, CanvasConfig.DEFAULT_PARAMS)


class CanvasDataProcessor:
    """Process and transform Canvas API data"""
    
    @staticmethod
    def parse_datetime(date_str: Optional[str]) -> Optional[datetime]:
        """Parse Canvas datetime string"""
        if not date_str:
            return None
        
        try:
            # Canvas uses ISO 8601 format
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            logger.warning(f"Failed to parse datetime: {date_str}")
            return None
    
    @classmethod
    def process_course_data(cls, course_data: Dict[str, Any]) -> CanvasCourse:
        """Convert Canvas course data to CanvasCourse object"""
        return CanvasCourse(
            id=course_data['id'],
            name=course_data.get('name', 'Unknown Course'),
            course_code=course_data.get('course_code', ''),
            enrollment_term_id=course_data.get('enrollment_term_id'),
            start_at=cls.parse_datetime(course_data.get('start_at')),
            end_at=cls.parse_datetime(course_data.get('end_at')),
            credit_hours=None  # Will be calculated later
        )
    
    @classmethod  
    def process_assignment_data(cls, assignment_data: Dict[str, Any]) -> CanvasAssignment:
        """Convert Canvas assignment data to CanvasAssignment object"""
        return CanvasAssignment(
            id=assignment_data['id'],
            name=assignment_data.get('name', 'Untitled Assignment'),
            description=assignment_data.get('description'),
            due_at=cls.parse_datetime(assignment_data.get('due_at')),
            points_possible=assignment_data.get('points_possible'),
            course_id=assignment_data['course_id'],
            assignment_group_id=assignment_data.get('assignment_group_id'),
            html_url=assignment_data.get('html_url'),
            submission_types=assignment_data.get('submission_types', [])
        )
    
    @classmethod
    def process_assignment_group_data(cls, group_data: Dict[str, Any]) -> CanvasAssignmentGroup:
        """Convert Canvas assignment group data to CanvasAssignmentGroup object"""
        return CanvasAssignmentGroup(
            id=group_data['id'],
            name=group_data.get('name', 'Untitled Group'),
            weight=group_data.get('group_weight'),
            course_id=group_data['course_id']
        )


class CanvasDataFilter:
    """Filter and validate Canvas data"""
    
    @staticmethod
    def filter_active_assignments(assignments: List[CanvasAssignment]) -> List[CanvasAssignment]:
        """Filter out completed or irrelevant assignments"""
        active_assignments = []
        today = date.today()
        
        for assignment in assignments:
            # Skip assignments that are too old
            if assignment.due_date and assignment.due_date < today - timedelta(days=7):
                continue
                
            # Skip assignments without due dates that are likely not real assignments
            if not assignment.due_date and not assignment.points_possible:
                continue
                
            active_assignments.append(assignment)
        
        return active_assignments
    
    @staticmethod
    def filter_current_courses(courses: List[CanvasCourse]) -> List[CanvasCourse]:
        """Filter courses to current/active ones"""
        current_courses = []
        today = date.today()
        
        for course in courses:
            # Skip courses that have ended
            if course.end_at and course.end_at.date() < today:
                continue
                
            # Skip courses that haven't started yet (more than 1 week in future)
            if course.start_at and course.start_at.date() > today + timedelta(days=7):
                continue
                
            current_courses.append(course)
        
        return current_courses


class CanvasSync:
    """High-level Canvas synchronization utilities"""
    
    def __init__(self, api_token: str = None):
        self.client = CanvasAPIClient(api_token)
        self.processor = CanvasDataProcessor()
        self.filter = CanvasDataFilter()
    
    def get_all_course_data(self) -> Tuple[List[CanvasCourse], Dict[int, List[CanvasAssignment]], Dict[int, List[CanvasAssignmentGroup]]]:
        """
        Get all relevant course data from Canvas
        
        Returns:
            Tuple of (courses, assignments_by_course_id, assignment_groups_by_course_id)
        """
        # Get courses
        courses_data = self.client.get_courses()
        courses = [self.processor.process_course_data(c) for c in courses_data]
        courses = self.filter.filter_current_courses(courses)
        
        # Get assignments and assignment groups for each course
        assignments_by_course = {}
        groups_by_course = {}
        
        for course in courses:
            try:
                # Get assignments
                assignments_data = self.client.get_assignments(course.id)
                assignments = [self.processor.process_assignment_data(a) for a in assignments_data]
                assignments = self.filter.filter_active_assignments(assignments)
                assignments_by_course[course.id] = assignments
                
                # Get assignment groups
                groups_data = self.client.get_assignment_groups(course.id)
                groups = [self.processor.process_assignment_group_data(g) for g in groups_data]
                groups_by_course[course.id] = groups
                
            except CanvasAPIError as e:
                logger.error(f"Failed to get data for course {course.name}: {e}")
                assignments_by_course[course.id] = []
                groups_by_course[course.id] = []
        
        return courses, assignments_by_course, groups_by_course
    
    def get_upcoming_assignments(self, days_ahead: int = 30) -> List[Tuple[CanvasCourse, CanvasAssignment]]:
        """
        Get all assignments due in the next N days
        
        Returns:
            List of (course, assignment) tuples
        """
        courses, assignments_by_course, _ = self.get_all_course_data()
        
        upcoming = []
        cutoff_date = date.today() + timedelta(days=days_ahead)
        
        for course in courses:
            for assignment in assignments_by_course.get(course.id, []):
                if assignment.due_date and assignment.due_date <= cutoff_date:
                    upcoming.append((course, assignment))
        
        # Sort by due date
        upcoming.sort(key=lambda x: x[1].due_date or date.max)
        return upcoming
