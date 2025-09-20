from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import speech_recognition as sr
import google.generativeai as genai
from dotenv import load_dotenv
from voice_agent.update_task_core import process_voice_command

class Command(BaseCommand):
    help = 'Real Voice Agent - Speak to your StudyBunny!'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='User ID to use (defaults to first user)',
        )

    def get_voice_input(self):
        """Capture actual voice input and return as string"""
        
        # Load environment variables
        load_dotenv()
        
        # Initialize speech recognition
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        
        # Settings for complete sentences
        recognizer.energy_threshold = 300
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 2.0  # Wait 2 seconds of silence
        recognizer.phrase_threshold = 0.3
        recognizer.non_speaking_duration = 1.0
        
        self.stdout.write("🎤 Listening... (speak now)")
        
        try:
            with microphone as source:
                self.stdout.write("🎤 Adjusting for ambient noise...")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                self.stdout.write("✅ Ready! Speak to me...")
                
                # Listen for complete speech
                audio = recognizer.listen(
                    source, 
                    timeout=30,
                    phrase_time_limit=60
                )
                
                self.stdout.write("🔄 Processing your speech...")
                
                try:
                    # Convert speech to text
                    user_text = recognizer.recognize_google(audio, language='en-US')
                    
                    if user_text and len(user_text.strip()) > 0:
                        self.stdout.write(self.style.SUCCESS(f"✅ You said: {user_text}"))
                        return user_text
                    else:
                        self.stdout.write(self.style.WARNING("❌ No speech detected"))
                        return None
                        
                except sr.UnknownValueError:
                    self.stdout.write(self.style.WARNING("❌ Could not understand - try speaking more clearly"))
                    return None
                except sr.RequestError as e:
                    self.stdout.write(self.style.ERROR(f"❌ Speech recognition error: {e}"))
                    return None
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Microphone error: {e}"))
            return None

    def handle(self, *args, **options):
        self.stdout.write("🎤 StudyBunny Real Voice Agent")
        self.stdout.write("=" * 40)
        
        # Get user
        if options['user_id']:
            user = User.objects.get(id=options['user_id'])
        else:
            user = User.objects.first()
        
        if not user:
            self.stdout.write(self.style.ERROR("❌ No users found. Please create a user first."))
            return
        
        self.stdout.write(self.style.SUCCESS(f"✅ Connected as: {user.username}"))
        self.stdout.write("\n💡 Example things to say:")
        self.stdout.write("   • I finished my math homework")
        self.stdout.write("   • Update science project progress to 75%")
        self.stdout.write("   • Set high priority for English essay")
        self.stdout.write("   • I completed homework and spent 2 hours on the project")
        self.stdout.write("\n" + "="*40)
        
        while True:
            try:
                # Get voice input
                command = self.get_voice_input()
                
                if not command:
                    self.stdout.write("🔄 Try again...")
                    continue
                    
                if command.lower() in ['quit', 'exit', 'stop', 'bye', 'goodbye']:
                    self.stdout.write("👋 Goodbye!")
                    break
                
                self.stdout.write(f"\n🤖 Processing: '{command}'")
                self.stdout.write("-" * 30)
                
                # Process the command
                process_voice_command(command, user)
                
                self.stdout.write("\n" + "="*40)
                self.stdout.write("🎤 Ready for next command...")
                
            except KeyboardInterrupt:
                self.stdout.write("\n👋 Goodbye!")
                break
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))
                continue
