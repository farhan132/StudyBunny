"""
Examples of using Gemini API to generate numerical outputs for StudyBunny
"""
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

load_dotenv()

def setup_gemini():
    """Setup Gemini API"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

def get_task_priority_score(task_description, due_date, user_workload):
    """
    Get numerical priority score (1-5) based on task parameters
    """
    model = setup_gemini()
    
    prompt = f"""
    Analyze this task and return ONLY a JSON object with numerical values:
    
    Task: "{task_description}"
    Due date: {due_date}
    Current workload: {user_workload}/10
    
    Return exactly this format:
    {{
        "priority_score": <integer 1-5>,
        "urgency_factor": <float 0.1-1.0>,
        "estimated_hours": <float>,
        "stress_level": <integer 1-10>
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        result = json.loads(response.text.strip())
        return result
    except Exception as e:
        print(f"Error getting priority score: {e}")
        return None

def get_time_allocation(tasks_list, available_hours, intensity_level):
    """
    Get time allocation for multiple tasks based on parameters
    """
    model = setup_gemini()
    
    tasks_str = "\n".join([f"- {task}" for task in tasks_list])
    
    prompt = f"""
    Given these tasks and constraints, allocate time efficiently:
    
    Tasks:
    {tasks_str}
    
    Available time: {available_hours} hours
    Intensity level: {intensity_level}/10
    
    Return ONLY a JSON array with time allocations:
    [
        {{
            "task_index": <integer>,
            "allocated_minutes": <integer>,
            "priority_weight": <float 0-1>,
            "difficulty_factor": <float 0-1>
        }}
    ]
    """
    
    try:
        response = model.generate_content(prompt)
        result = json.loads(response.text.strip())
        return result
    except Exception as e:
        print(f"Error getting time allocation: {e}")
        return None

def get_study_intensity_recommendation(current_performance, stress_level, deadline_pressure):
    """
    Get recommended study intensity based on multiple parameters
    """
    model = setup_gemini()
    
    prompt = f"""
    Based on these student metrics, recommend optimal study intensity:
    
    Current performance: {current_performance}%
    Stress level: {stress_level}/10
    Deadline pressure: {deadline_pressure}/10
    
    Return ONLY this JSON format:
    {{
        "recommended_intensity": <float 0.0-1.0>,
        "study_hours_per_day": <float>,
        "break_frequency_minutes": <integer>,
        "motivation_score": <integer 1-100>,
        "burnout_risk": <float 0.0-1.0>
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        result = json.loads(response.text.strip())
        return result
    except Exception as e:
        print(f"Error getting intensity recommendation: {e}")
        return None

def get_completion_prediction(task_complexity, user_skill, time_spent, total_estimated):
    """
    Predict task completion percentage based on parameters
    """
    model = setup_gemini()
    
    prompt = f"""
    Predict task completion based on these parameters:
    
    Task complexity: {task_complexity}/10
    User skill level: {user_skill}/10
    Time already spent: {time_spent} hours
    Total estimated time: {total_estimated} hours
    
    Return ONLY this JSON:
    {{
        "predicted_completion": <float 0-100>,
        "remaining_hours": <float>,
        "efficiency_score": <float 0-1>,
        "completion_confidence": <float 0-1>
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        result = json.loads(response.text.strip())
        return result
    except Exception as e:
        print(f"Error getting completion prediction: {e}")
        return None

# Example usage
if __name__ == "__main__":
    # Test priority scoring
    priority_result = get_task_priority_score(
        "Complete machine learning assignment", 
        "2024-01-15", 
        7
    )
    print("Priority Score Result:", priority_result)
    
    # Test time allocation
    tasks = ["Math homework", "Science project", "English essay"]
    time_result = get_time_allocation(tasks, 4.5, 8)
    print("Time Allocation Result:", time_result)
    
    # Test intensity recommendation
    intensity_result = get_study_intensity_recommendation(75, 6, 8)
    print("Intensity Recommendation:", intensity_result)
    
    # Test completion prediction
    completion_result = get_completion_prediction(7, 6, 2.5, 5.0)
    print("Completion Prediction:", completion_result)
