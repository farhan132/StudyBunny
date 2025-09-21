"""
Canvas API integration for StudyBunny homework dashboard
Automatically fetches and integrates with existing backend parameters
"""
import requests
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from apps.study.models import Task
from apps.core.models import TimeCalculation
import json

class CanvasIntegrator:
    def __init__(self, api_token, canvas_base_url="https://canvas.instructure.com"):
        """
        Initialize Canvas API integration
        
        Args:
            api_token (str): Canvas API access token
            canvas_base_url (str): Base URL for Canvas instance
        """
        self.api_token = api_token
        self.base_url = canvas_base_url.rstrip('/')
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
    
    def fetch_all_courses(self):
        """
        Fetch all enrolled courses from Canvas
        
        Returns:
            list: List of course dictionaries with all relevant data
        """
        url = f"{self.base_url}/api/v1/courses"
        params = {
            'enrollment_state': 'active',
            'include': ['syllabus_body', 'term', 'course_progress', 'sections', 'total_students']
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            courses = response.json()
            
            # Process courses and extract credit hours from course codes if possible
            processed_courses = []
            for course in courses:
                processed_course = {
                    'canvas_id': course.get('id'),
                    'name': course.get('name', ''),
                    'course_code': course.get('course_code', ''),
                    'credit_hours': self._extract_credit_hours(course.get('course_code', '')),
                    'term': course.get('term', {}).get('name', ''),
                    'syllabus': course.get('syllabus_body', ''),
                    'total_students': course.get('total_students', 0),
                    'canvas_url': course.get('html_url', '')
                }
                processed_courses.append(processed_course)
            
            return processed_courses
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching courses: {e}")
            return []
    
    def fetch_course_assignments(self, course_id):
        """
        Fetch all assignments for a specific course
        
        Args:
            course_id (int): Canvas course ID
            
        Returns:
            list: List of assignment dictionaries
        """
        url = f"{self.base_url}/api/v1/courses/{course_id}/assignments"
        params = {
            'include': ['submission', 'assignment_group', 'rubric', 'overrides'],
            'order_by': 'due_at'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            assignments = response.json()
            
            processed_assignments = []
            for assignment in assignments:
                due_date = assignment.get('due_at')
                if due_date:
                    due_datetime = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                else:
                    due_datetime = None
                
                processed_assignment = {
                    'canvas_id': assignment.get('id'),
                    'title': assignment.get('name', ''),
                    'description': assignment.get('description', ''),
                    'due_date': due_datetime.date() if due_datetime else None,
                    'due_time': due_datetime.time() if due_datetime else None,
                    'points_possible': assignment.get('points_possible', 0),
                    'assignment_group': assignment.get('assignment_group', {}).get('name', ''),
                    'submission_status': self._get_submission_status(assignment.get('submission')),
                    'estimated_time': self._estimate_assignment_time(assignment),
                    'canvas_url': assignment.get('html_url', ''),
                    'course_id': course_id
                }
                processed_assignments.append(processed_assignment)
            
            return processed_assignments
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching assignments for course {course_id}: {e}")
            return []
    
    def sync_with_studybunny(self, user, api_token="7867~GJxFLY3HMHGQRD6cHvVckvFQV2zBwN2nAtvTDJVMZBtuufeDvVrtymDGyvKEXayH"):
        """
        Complete sync function that integrates Canvas data with StudyBunny backend
        
        Args:
            user (User): Django user instance
            api_token (str): Canvas API token
            
        Returns:
            dict: Summary of sync results
        """
        # Initialize with provided token
        self.api_token = api_token
        self.headers['Authorization'] = f'Bearer {self.api_token}'
        
        sync_results = {
            'courses_synced': 0,
            'assignments_synced': 0,
            'tasks_created': 0,
            'errors': []
        }
        
        try:
            # Fetch all courses
            courses = self.fetch_all_courses()
            sync_results['courses_synced'] = len(courses)
            
            for course in courses:
                try:
                    # Fetch assignments for each course
                    assignments = self.fetch_course_assignments(course['canvas_id'])
                    sync_results['assignments_synced'] += len(assignments)
                    
                    # Create StudyBunny tasks from assignments
                    for assignment in assignments:
                        if assignment['due_date']:  # Only create tasks with due dates
                            task_created = self._create_studybunny_task(
                                user, course, assignment
                            )
                            if task_created:
                                sync_results['tasks_created'] += 1
                
                except Exception as e:
                    sync_results['errors'].append(f"Error processing course {course['name']}: {str(e)}")
            
            return sync_results
            
        except Exception as e:
            sync_results['errors'].append(f"General sync error: {str(e)}")
            return sync_results
    
    def _create_studybunny_task(self, user, course, assignment):
        """
        Create a StudyBunny Task from Canvas assignment data
        
        Args:
            user (User): Django user
            course (dict): Course data
            assignment (dict): Assignment data
            
        Returns:
            bool: True if task created successfully
        """
        try:
            # Check if task already exists
            existing_task = Task.objects.filter(
                user=user,
                title=f"{course['course_code']}: {assignment['title']}"
            ).first()
            
            if existing_task:
                return False  # Task already exists
            
            # Calculate priority based on due date and points
            priority = self._calculate_priority(assignment)
            
            # Create the task
            task = Task.objects.create(
                user=user,
                title=f"{course['course_code']}: {assignment['title']}",
                description=f"Course: {course['name']}\nCredit Hours: {course['credit_hours']}\nAssignment Group: {assignment['assignment_group']}\nPoints: {assignment['points_possible']}\n\n{assignment['description'][:500]}...",
                T_n=assignment['estimated_time'],
                completed_so_far=0.0,
                delta=priority,
                due_date=assignment['due_date'],
                due_time=assignment['due_time'] or datetime.now().time().replace(hour=23, minute=59)
            )
            
            return True
            
        except Exception as e:
            print(f"Error creating task for assignment {assignment['title']}: {e}")
            return False
    
    def _extract_credit_hours(self, course_code):
        """
        Extract credit hours from course code if possible
        
        Args:
            course_code (str): Course code like "MATH-301-3CR"
            
        Returns:
            int: Estimated credit hours (default 3 if not found)
        """
        import re
        
        # Look for patterns like "3CR", "3-CR", "3 CR", etc.
        patterns = [
            r'(\d+)[-\s]*CR',
            r'(\d+)[-\s]*CREDIT',
            r'(\d+)[-\s]*HRS?',
            r'(\d+)[-\s]*HOUR'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, course_code.upper())
            if match:
                return int(match.group(1))
        
        # Default to 3 credit hours if not found
        return 3
    
    def _get_submission_status(self, submission_data):
        """
        Determine submission status from Canvas data
        
        Args:
            submission_data (dict): Canvas submission data
            
        Returns:
            str: Submission status
        """
        if not submission_data:
            return 'not_submitted'
        
        workflow_state = submission_data.get('workflow_state', 'unsubmitted')
        return workflow_state
    
    def _estimate_assignment_time(self, assignment):
        """
        Estimate time needed for assignment based on points and type
        
        Args:
            assignment (dict): Assignment data
            
        Returns:
            timedelta: Estimated time needed
        """
        points = assignment.get('points_possible', 10)
        if points is None:
            points = 10  # Default to 10 points if None
        
        assignment_group = assignment.get('assignment_group', {}).get('name', '').lower()
        
        # Special handling for problem sets - always 6 hours
        assignment_name = assignment.get('name', '').lower()
        if 'pset' in assignment_name or 'problem set' in assignment_name:
            base_hours = 6.0  # Problem sets always take 6 hours
            multiplier = 1.0
        else:
            # Base time calculation: 1 hour per 10 points
            base_hours = max(1, points / 10)
            
            # Adjust based on assignment type
            multiplier = 1.0
            if 'exam' in assignment_group or 'test' in assignment_group:
                multiplier = 0.5  # Exams are usually shorter but intense
            elif 'project' in assignment_group or 'paper' in assignment_group:
                multiplier = 2.0  # Projects take longer
            elif 'homework' in assignment_group or 'assignment' in assignment_group:
                multiplier = 1.0  # Standard homework
            elif 'quiz' in assignment_group:
                multiplier = 0.3  # Quizzes are quick
        
        estimated_hours = base_hours * multiplier
        final_hours = min(20, max(0.5, estimated_hours))
        
        print(f"🔍 CANVAS TIME ESTIMATION:")
        print(f"   Assignment: {assignment.get('name', 'Unknown')}")
        print(f"   Points: {points}")
        print(f"   Assignment Group: {assignment_group}")
        print(f"   Base Hours: {base_hours}")
        print(f"   Multiplier: {multiplier}")
        print(f"   Final Hours: {final_hours}")
        
        return timedelta(hours=final_hours)
    
    def _calculate_priority(self, assignment):
        """
        Calculate priority (1-5) based on assignment data
        
        Args:
            assignment (dict): Assignment data
            
        Returns:
            int: Priority level (1-5)
        """
        if not assignment['due_date']:
            return 3  # Medium priority if no due date
        
        days_until_due = (assignment['due_date'] - datetime.now().date()).days
        points = assignment.get('points_possible', 10)
        if points is None:
            points = 10  # Default to 10 points if None
        
        # High priority if due soon or worth many points
        if days_until_due <= 1:
            return 5  # Very high
        elif days_until_due <= 3:
            return 4  # High
        elif days_until_due <= 7:
            return 3  # Medium
        elif days_until_due <= 14:
            return 2  # Low
        else:
            return 1  # Very low
        
        # Adjust based on points
        if points >= 100:
            return min(5, priority + 1)
        elif points <= 10:
            return max(1, priority - 1)
        
        return 3

# Convenience function for easy use
def sync_canvas_homework(user, api_token="7867~GJxFLY3HMHGQRD6cHvVckvFQV2zBwN2nAtvTDJVMZBtuufeDvVrtymDGyvKEXayH", canvas_url="https://canvas.instructure.com"):
    """
    One-function sync that automatically includes all StudyBunny backend parameters
    
    Args:
        user (User): Django user instance
        api_token (str): Canvas API token
        canvas_url (str): Canvas instance URL
        
    Returns:
        dict: Sync results summary
    """
    integrator = CanvasIntegrator(api_token, canvas_url)
    return integrator.sync_with_studybunny(user, api_token)
