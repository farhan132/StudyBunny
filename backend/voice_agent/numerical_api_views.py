"""
API views for numerical parameter extraction and recommendations
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .numerical_voice_agent import get_numerical_parameters_from_voice, get_smart_recommendations

@csrf_exempt
@require_http_methods(["POST"])
def extract_numbers_from_text(request):
    """
    API endpoint to extract numerical parameters from text/voice input
    
    POST /voice_agent/extract_numbers/
    Body: {"text": "I spent 2 hours on homework and it's 75% complete"}
    
    Returns: {"completion_percentage": 75, "time_spent_minutes": 120, ...}
    """
    try:
        data = json.loads(request.body)
        text = data.get('text', '')
        
        if not text:
            return JsonResponse({
                'success': False,
                'error': 'Text parameter is required'
            }, status=400)
        
        # Extract numerical parameters using Gemini
        parameters = get_numerical_parameters_from_voice(text)
        
        if parameters is None:
            return JsonResponse({
                'success': False,
                'error': 'Failed to extract parameters'
            }, status=500)
        
        return JsonResponse({
            'success': True,
            'extracted_parameters': parameters,
            'original_text': text
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error processing request: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def get_numerical_recommendations(request):
    """
    API endpoint to get numerical recommendations based on task and parameters
    
    POST /voice_agent/get_recommendations/
    Body: {
        "task_name": "Math homework",
        "parameters": {
            "completion_percentage": 60,
            "time_spent_minutes": 90,
            "difficulty_rating": 7
        }
    }
    """
    try:
        data = json.loads(request.body)
        task_name = data.get('task_name', 'Unknown Task')
        parameters = data.get('parameters', {})
        
        # Get recommendations using Gemini
        recommendations = get_smart_recommendations(task_name, parameters)
        
        if recommendations is None:
            return JsonResponse({
                'success': False,
                'error': 'Failed to generate recommendations'
            }, status=500)
        
        return JsonResponse({
            'success': True,
            'task_name': task_name,
            'input_parameters': parameters,
            'recommendations': recommendations
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error processing request: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def complete_numerical_analysis(request):
    """
    Complete workflow: extract numbers + generate recommendations
    
    POST /voice_agent/complete_analysis/
    Body: {"text": "I worked on the project for 3 hours, it's getting difficult"}
    """
    try:
        data = json.loads(request.body)
        text = data.get('text', '')
        
        if not text:
            return JsonResponse({
                'success': False,
                'error': 'Text parameter is required'
            }, status=400)
        
        # Step 1: Extract parameters
        parameters = get_numerical_parameters_from_voice(text)
        if parameters is None:
            return JsonResponse({
                'success': False,
                'error': 'Failed to extract parameters'
            }, status=500)
        
        # Step 2: Generate recommendations
        task_name = data.get('task_name', 'Current Task')
        recommendations = get_smart_recommendations(task_name, parameters)
        
        if recommendations is None:
            return JsonResponse({
                'success': False,
                'error': 'Failed to generate recommendations'
            }, status=500)
        
        return JsonResponse({
            'success': True,
            'original_text': text,
            'extracted_parameters': parameters,
            'recommendations': recommendations,
            'analysis_summary': {
                'has_time_data': parameters.get('time_spent_minutes') is not None,
                'has_completion_data': parameters.get('completion_percentage') is not None,
                'has_difficulty_data': parameters.get('difficulty_rating') is not None,
                'recommended_next_action': 'continue' if parameters.get('completion_percentage', 0) < 80 else 'review'
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error processing request: {str(e)}'
        }, status=500)
