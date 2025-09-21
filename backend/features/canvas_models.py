"""
Canvas-specific data models and utilities
"""
from dataclasses import dataclass
from datetime import datetime, date, time
from typing import Optional, List, Dict, Any


@dataclass
class CanvasCourse:
    """Represents a Canvas course"""
    id: int
    name: str
    course_code: str
    enrollment_term_id: Optional[int] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    credit_hours: Optional[int] = None
    
    def extract_credit_hours(self) -> int:
        """Extract credit hours from course code (e.g., '18.600' -> 6)"""
        if not self.course_code:
            return 3  # Default
            
        parts = self.course_code.split('.')
        if len(parts) >= 2:
            try:
                return int(parts[1][0])  # First digit after decimal
            except (ValueError, IndexError):
                pass
        return 3  # Default fallback


@dataclass 
class CanvasAssignment:
    """Represents a Canvas assignment"""
    id: int
    name: str
    description: Optional[str]
    due_at: Optional[datetime]
    points_possible: Optional[float]
    course_id: int
    assignment_group_id: Optional[int] = None
    html_url: Optional[str] = None
    submission_types: Optional[List[str]] = None
    
    @property
    def due_date(self) -> Optional[date]:
        """Get due date without time"""
        return self.due_at.date() if self.due_at else None
    
    @property 
    def due_time(self) -> Optional[time]:
        """Get due time without date"""
        return self.due_at.time() if self.due_at else None


@dataclass
class CanvasAssignmentGroup:
    """Represents a Canvas assignment group (like 'Problem Sets', 'Exams')"""
    id: int
    name: str
    weight: Optional[float]
    course_id: int


@dataclass
class StudyBunnyTask:
    """Represents a task to be created in StudyBunny"""
    title: str
    description: str
    due_date: date
    due_time: time
    estimated_hours: float
    priority: int
    course_name: str
    points_possible: Optional[float] = None
    canvas_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for task creation"""
        return {
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date,
            'due_time': self.due_time,
            'T_n': f"{int(self.estimated_hours)}:{int((self.estimated_hours % 1) * 60):02d}:00",
            'delta': self.priority,
            'completed_so_far': 0.0,
            'is_completed': False,
        }


class CanvasTaskConverter:
    """Converts Canvas assignments to StudyBunny tasks"""
    
    @staticmethod
    def estimate_time_from_assignment(assignment: CanvasAssignment, course: CanvasCourse) -> float:
        """
        Estimate time needed for assignment based on various factors
        Returns: estimated hours as float
        """
        base_hours = 2.0  # Default base time
        
        # Adjust based on points
        if assignment.points_possible:
            if assignment.points_possible >= 100:
                base_hours = 10.0  # Major assignment
            elif assignment.points_possible >= 50:
                base_hours = 6.0   # Medium assignment
            elif assignment.points_possible >= 20:
                base_hours = 4.0   # Small assignment
            else:
                base_hours = 2.0   # Minimal assignment
        
        # Adjust based on course credit hours
        credit_multiplier = course.credit_hours / 3.0 if course.credit_hours else 1.0
        base_hours *= credit_multiplier
        
        # Adjust based on assignment name keywords
        name_lower = assignment.name.lower()
        if any(word in name_lower for word in ['exam', 'test', 'midterm', 'final']):
            base_hours *= 2.0  # Exams need more study time
        elif any(word in name_lower for word in ['quiz', 'hw', 'homework']):
            base_hours *= 0.7  # Quizzes/homework typically shorter
        elif any(word in name_lower for word in ['project', 'paper', 'essay']):
            base_hours *= 1.5  # Projects need more time
            
        return min(base_hours, 20.0)  # Cap at 20 hours
    
    @staticmethod
    def calculate_priority(assignment: CanvasAssignment, days_until_due: int) -> int:
        """
        Calculate priority (1-5, where 1 is highest priority)
        """
        if days_until_due <= 1:
            return 1  # Due very soon
        elif days_until_due <= 3:
            return 2  # Due soon
        elif days_until_due <= 7:
            return 3  # Due this week
        elif days_until_due <= 14:
            return 4  # Due in two weeks
        else:
            return 5  # Due later
    
    @classmethod
    def convert_to_studybunny_task(
        cls, 
        assignment: CanvasAssignment, 
        course: CanvasCourse,
        assignment_group: Optional[CanvasAssignmentGroup] = None
    ) -> StudyBunnyTask:
        """Convert Canvas assignment to StudyBunny task"""
        
        # Calculate days until due
        days_until_due = 999  # Default for no due date
        if assignment.due_date:
            days_until_due = (assignment.due_date - date.today()).days
        
        # Build description
        description_parts = [f"Course: {course.name}"]
        if assignment.points_possible:
            description_parts.append(f"Points: {assignment.points_possible}")
        if assignment.html_url:
            description_parts.append(f"Canvas URL: {assignment.html_url}")
        if assignment_group:
            description_parts.append(f"Assignment Group: {assignment_group.name}")
            
        description = "\n".join(description_parts)
        
        return StudyBunnyTask(
            title=f"{course.course_code}: {assignment.name}",
            description=description,
            due_date=assignment.due_date or date.today() + timedelta(days=7),
            due_time=assignment.due_time or time(23, 59),
            estimated_hours=cls.estimate_time_from_assignment(assignment, course),
            priority=cls.calculate_priority(assignment, days_until_due),
            course_name=course.name,
            points_possible=assignment.points_possible,
            canvas_url=assignment.html_url,
        )
