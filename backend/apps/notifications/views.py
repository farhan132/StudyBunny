from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from .models import Notification, NotificationSettings
from .serializers import NotificationSerializer, NotificationSettingsSerializer
from .services import NotificationService


@api_view(['GET'])
@permission_classes([AllowAny])
def get_notifications(request):
    """Get all notifications for the user"""
    try:
        # Get demo user for now
        user, created = User.objects.get_or_create(
            username='demo_user',
            defaults={'email': 'demo@studybunny.com', 'first_name': 'Demo', 'last_name': 'User'}
        )
        
        # Get all notifications for this user
        all_notifications = Notification.objects.filter(user=user).order_by('-created_at')
        
        # Count unread notifications
        unread_count = all_notifications.filter(is_read=False).count()
        
        # Get recent notifications (limit to 20)
        recent_notifications = all_notifications[:20]
        serializer = NotificationSerializer(recent_notifications, many=True)
        
        return Response({
            'success': True,
            'notifications': serializer.data,
            'unread_count': unread_count,
            'total_count': all_notifications.count()
        })
        
    except Exception as e:
        return Response(
            {'error': f'Error fetching notifications: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def mark_notification_read(request, notification_id):
    """Mark a specific notification as read"""
    try:
        # Get demo user for now
        user, created = User.objects.get_or_create(
            username='demo_user',
            defaults={'email': 'demo@studybunny.com', 'first_name': 'Demo', 'last_name': 'User'}
        )
        
        notification = Notification.objects.get(id=notification_id, user=user)
        notification.mark_as_read()
        
        return Response({
            'success': True,
            'message': 'Notification marked as read'
        })
        
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Notification not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Error marking notification as read: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    try:
        # Get demo user for now
        user, created = User.objects.get_or_create(
            username='demo_user',
            defaults={'email': 'demo@studybunny.com', 'first_name': 'Demo', 'last_name': 'User'}
        )
        
        count = Notification.objects.filter(user=user, is_read=False).update(is_read=True)
        
        return Response({
            'success': True,
            'message': f'Marked {count} notifications as read'
        })
        
    except Exception as e:
        return Response(
            {'error': f'Error marking notifications as read: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['DELETE'])
@permission_classes([AllowAny])
def clear_all_notifications(request):
    """Clear all notifications for the user"""
    try:
        # Get demo user for now
        user, created = User.objects.get_or_create(
            username='demo_user',
            defaults={'email': 'demo@studybunny.com', 'first_name': 'Demo', 'last_name': 'User'}
        )
        
        count = Notification.objects.filter(user=user).count()
        Notification.objects.filter(user=user).delete()
        
        return Response({
            'success': True,
            'message': f'Cleared {count} notifications'
        })
        
    except Exception as e:
        return Response(
            {'error': f'Error clearing notifications: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def notification_settings(request):
    """Get or update notification settings"""
    try:
        # Get demo user for now
        user, created = User.objects.get_or_create(
            username='demo_user',
            defaults={'email': 'demo@studybunny.com', 'first_name': 'Demo', 'last_name': 'User'}
        )
        
        # Get or create notification settings
        settings, created = NotificationSettings.objects.get_or_create(user=user)
        
        if request.method == 'GET':
            serializer = NotificationSettingsSerializer(settings)
            return Response({
                'success': True,
                'settings': serializer.data
            })
        
        elif request.method == 'POST':
            serializer = NotificationSettingsSerializer(settings, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Notification settings updated',
                    'settings': serializer.data
                })
            else:
                return Response(
                    {'error': 'Invalid settings data', 'details': serializer.errors}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
    except Exception as e:
        return Response(
            {'error': f'Error with notification settings: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def generate_test_notifications(request):
    """Generate test notifications for development"""
    try:
        # Get demo user for now
        user, created = User.objects.get_or_create(
            username='demo_user',
            defaults={'email': 'demo@studybunny.com', 'first_name': 'Demo', 'last_name': 'User'}
        )
        
        # Generate test notifications
        test_notifications = [
            {
                'type': 'success',
                'title': 'Task Completed!',
                'message': 'Great job! You completed your Canvas assignment.',
                'icon': '🎉'
            },
            {
                'type': 'reminder',
                'title': 'Study Session Starting',
                'message': 'Time to start your scheduled study session for 18.600.',
                'icon': '⏰'
            },
            {
                'type': 'achievement',
                'title': 'Streak Achievement!',
                'message': 'Congratulations! You\'ve maintained a 7-day study streak.',
                'icon': '🔥'
            },
            {
                'type': 'motivation',
                'title': 'Keep Going!',
                'message': 'You\'re doing great! Only 2 more tasks to complete this week.',
                'icon': '💪'
            }
        ]
        
        created_count = 0
        for notif_data in test_notifications:
            Notification.objects.create(
                user=user,
                **notif_data
            )
            created_count += 1
        
        return Response({
            'success': True,
            'message': f'Created {created_count} test notifications'
        })
        
    except Exception as e:
        return Response(
            {'error': f'Error generating test notifications: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
