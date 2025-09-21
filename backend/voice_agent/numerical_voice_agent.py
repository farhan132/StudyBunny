"""
Enhanced voice agent with numerical parameter extraction using Gemini
"""
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

def get_numerical_parameters_from_voice(voice_text):
    """
    Extract numerical parameters from voice input using Gemini
    """
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Extract numerical parameters from this voice command: "{voice_text}"
    
    Return ONLY a JSON object with these numerical values (use null if not mentioned):
    {{
        "completion_percentage": <integer 0-100 or null>,
        "time_spent_minutes": <integer or null>,
        "priority_level": <integer 1-5 or null>,
        "difficulty_rating": <integer 1-10 or null>,
        "hours_needed": <float or null>,
        "days_until_due": <integer or null>,
        "stress_level": <integer 1-10 or null>
    }}
    
    Examples:
    "I spent 2 hours on math homework and it's 75% done" → {{"completion_percentage": 75, "time_spent_minutes": 120, "priority_level": null, "difficulty_rating": null, "hours_needed": null, "days_until_due": null, "stress_level": null}}
    "Set high priority for the project due in 3 days" → {{"completion_percentage": null, "time_spent_minutes": null, "priority_level": 4, "difficulty_rating": null, "hours_needed": null, "days_until_due": 3, "stress_level": null}}
    """
    
    try:
        response = model.generate_content(prompt)
        result = json.loads(response.text.strip())
        return result
    except Exception as e:
        print(f"Error extracting numerical parameters: {e}")
        return None

def get_smart_recommendations(task_name, parameters):
    """
    Get smart numerical recommendations based on task and parameters
    """
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    params_str = json.dumps(parameters, indent=2)
    
    prompt = f"""
    Based on this task and current parameters, provide smart recommendations:
    
    Task: "{task_name}"
    Current parameters: {params_str}
    
    Return ONLY this JSON format:
    {{
        "recommended_next_session_minutes": <integer>,
        "optimal_break_frequency_minutes": <integer>,
        "suggested_daily_commitment_minutes": <integer>,
        "productivity_boost_factor": <float 0-2>,
        "completion_timeline_days": <integer>,
        "motivation_score": <integer 1-100>,
        "recommended_intensity": <float 0-1>
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        result = json.loads(response.text.strip())
        return result
    except Exception as e:
        print(f"Error getting recommendations: {e}")
        return None

def process_numerical_voice_command(voice_text):
    """
    Complete workflow: voice → numerical extraction → recommendations
    """
    print(f"Processing voice command: '{voice_text}'")
    
    # Step 1: Extract numerical parameters
    parameters = get_numerical_parameters_from_voice(voice_text)
    if not parameters:
        return {"error": "Could not extract parameters"}
    
    print(f"Extracted parameters: {json.dumps(parameters, indent=2)}")
    
    # Step 2: Identify task name (simplified extraction)
    task_name = "Unknown Task"  # You can enhance this with another Gemini call
    
    # Step 3: Get smart recommendations
    recommendations = get_smart_recommendations(task_name, parameters)
    if not recommendations:
        return {"error": "Could not generate recommendations"}
    
    return {
        "extracted_parameters": parameters,
        "recommendations": recommendations,
        "success": True
    }

# Example usage and testing
if __name__ == "__main__":
    test_commands = [
        "I spent 90 minutes on the math assignment and I'm about 60% done",
        "Set the science project to high priority, it's due in 5 days",
        "I worked on the essay for 3 hours today, feeling stressed level 8",
        "The programming task is really difficult, maybe 9 out of 10, need 4 more hours"
    ]
    
    for command in test_commands:
        print(f"\n{'='*60}")
        result = process_numerical_voice_command(command)
        print(json.dumps(result, indent=2))
