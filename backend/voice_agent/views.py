from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
import json

# Import aifc compatibility module before importing speech_recognition
try:
    import aifc
except ImportError:
    # Python 3.13+ compatibility - aifc module was removed
    from . import aifc_compat

from .update_task import process_voice_command, get_voice_input

@csrf_exempt
@require_http_methods(["POST"])
def voice_command_api(request):
    """
    API endpoint to process voice commands for task updates
    """
    print("🎤 VOICE COMMAND API CALLED")
    print(f"   Method: {request.method}")
    print(f"   Headers: {dict(request.headers)}")
    print(f"   Body: {request.body}")
    
    try:
        # Parse JSON data
        try:
            data = json.loads(request.body)
            print(f"   Parsed data: {data}")
        except json.JSONDecodeError:
            print("   ❌ Invalid JSON data")
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        
        # Get user from request (you might need to adjust this based on your auth system)
        user_id = data.get('user_id') or request.headers.get('X-User-ID')
        if not user_id:
            return JsonResponse({
                'success': False,
                'error': 'User ID required'
            }, status=400)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'User not found'
            }, status=404)
        
        # Get voice command text
        command_text = data.get('command_text')
        if not command_text:
            return JsonResponse({
                'success': False,
                'error': 'Command text required'
            }, status=400)
        
        # Process the voice command
        print(f"   Processing command: '{command_text}' for user: {user.username}")
        result = process_voice_command(command_text, user)
        print(f"   Command processing result: {result}")
        
        return JsonResponse({
            'success': True,
            'message': 'Voice command processed successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error processing voice command: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def voice_input_api(request):
    """
    API endpoint to capture voice input and process it
    """
    try:
        # Parse JSON data
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        
        # Get user from request
        user_id = data.get('user_id') or request.headers.get('X-User-ID')
        if not user_id:
            return JsonResponse({
                'success': False,
                'error': 'User ID required'
            }, status=400)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'User not found'
            }, status=404)
        
        # This endpoint is no longer needed since we use browser speech recognition
        # But keeping it for backward compatibility
        return JsonResponse({
            'success': False,
            'error': 'This endpoint is deprecated. Use browser speech recognition instead.'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error capturing voice input: {str(e)}'
        }, status=500)

def voice_agent_page(request):
    """
    Simple page to test the voice agent
    """
    return render(request, 'voice_agent/voice_agent.html')
