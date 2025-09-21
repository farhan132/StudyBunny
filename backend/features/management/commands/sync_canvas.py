"""
Django management command to sync Canvas assignments to StudyBunny tasks
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.conf import settings


class Command(BaseCommand):
    help = 'Sync Canvas assignments to StudyBunny tasks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='demo_user',
            help='Username to sync Canvas tasks for (default: demo_user)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be synced without actually creating tasks'
        )

    def handle(self, *args, **options):
        username = options['username']
        dry_run = options['dry_run']
        
        # Get Canvas configuration
        canvas_token = getattr(settings, 'CANVAS_API_TOKEN', None)
        canvas_base_url = getattr(settings, 'CANVAS_BASE_URL', 'https://canvas.instructure.com')
        
        if not canvas_token:
            raise CommandError('Canvas API token not configured in settings')
        
        # Get or create user
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=username,
                email=f'{username}@example.com'
            )
            self.stdout.write(f'Created user: {username}')
        
        if dry_run:
            self.stdout.write('DRY RUN MODE - No tasks will be created')
            # TODO: Implement dry run functionality
            return
        
        # Sync Canvas homework
        try:
            from features import get_sync_canvas_homework
            sync_canvas_homework = get_sync_canvas_homework()
            
            self.stdout.write(f'Syncing Canvas tasks for user: {username}')
            sync_results = sync_canvas_homework(
                user=user,
                api_token=canvas_token,
                canvas_url=canvas_base_url
            )
            
            if sync_results['tasks_created'] > 0 or len(sync_results['errors']) == 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Canvas sync successful! Created {sync_results["tasks_created"]} tasks from {sync_results["courses_synced"]} courses'
                    )
                )
                if sync_results['errors']:
                    self.stdout.write(
                        self.style.WARNING(f'Warnings: {sync_results["errors"]}')
                    )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Canvas sync failed: {sync_results["errors"]}')
                )
                
        except Exception as e:
            raise CommandError(f'Error syncing Canvas tasks: {str(e)}')
