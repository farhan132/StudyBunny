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
    try:
        # Get user from request (you might need to adjust this based on your auth system)
        user_id = request.POST.get('user_id') or request.headers.get('X-User-ID')
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
        command_text = request.POST.get('command_text')
        if not command_text:
            return JsonResponse({
                'success': False,
                'error': 'Command text required'
            }, status=400)
        
        # Process the voice command
        process_voice_command(command_text, user)
        
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
        # Get user from request
        user_id = request.POST.get('user_id') or request.headers.get('X-User-ID')
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
        
        # Get voice input
        voice_text = get_voice_input()
        
        if voice_text:
            # Process the voice command
            process_voice_command(voice_text, user)
            
            return JsonResponse({
                'success': True,
                'voice_text': voice_text,
                'message': 'Voice input captured and processed successfully'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'No voice input captured'
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
