from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from voice_agent.update_task_core import delete_task, update_task, process_voice_command

class Command(BaseCommand):
    help = 'Test the voice agent functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='User ID to test with (defaults to first user)',
        )
        parser.add_argument(
            '--command',
            type=str,
            help='Voice command to test',
        )

    def handle(self, *args, **options):
        self.stdout.write("🧪 Testing Voice Agent Functions")
        self.stdout.write("=" * 40)
        
        try:
            # Get user
            if options['user_id']:
                user = User.objects.get(id=options['user_id'])
            else:
                user = User.objects.first()
            
            if not user:
                self.stdout.write(self.style.ERROR("❌ No users found in database"))
                return
            
            self.stdout.write(self.style.SUCCESS(f"✅ Testing with user: {user.username}"))
            
            # Test with provided command or default tests
            if options['command']:
                commands = [options['command']]
            else:
                commands = [
                    "I finished my math homework",
                    "Update science project progress to 75%",
                    "Set high priority for English essay",
                    "I completed homework and spent 2 hours on the project"
                ]
            
            for i, command in enumerate(commands, 1):
                self.stdout.write(f"\n📝 Test {i}: {command}")
                self.stdout.write("-" * 30)
                
                # Process the command
                process_voice_command(command, user)
            
            self.stdout.write(self.style.SUCCESS("\n✅ Voice agent functions tested successfully!"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error during testing: {e}"))
            import traceback
            traceback.print_exc()
