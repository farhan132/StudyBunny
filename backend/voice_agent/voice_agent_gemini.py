import speech_recognition as sr
import os
import google.generativeai as genai
from dotenv import load_dotenv
import time
from datetime import datetime

def main():
    """Voice input with Gemini AI text responses only"""
    
    # Load environment variables
    load_dotenv()
    
    # Configure Gemini
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ Error: GEMINI_API_KEY not found in .env file!")
            print("Please add your Gemini API key to the .env file")
            return
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ Gemini AI configured successfully")
    except Exception as e:
        print(f"❌ Error configuring Gemini: {e}")
        return
    
    # Initialize speech recognition
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    # Settings for complete sentences
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 2.0  # Wait 2 seconds of silence
    recognizer.phrase_threshold = 0.3
    recognizer.non_speaking_duration = 1.0
    
    # Create transcript file
    transcript_file = f"gemini_voice_transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    print("🎤 Voice Input + Gemini AI Text Output")
    print("   Speak to me, I'll respond with text only")
    print("   Say 'quit' to stop")
    print(f"   Transcript saved to: {transcript_file}")
    print("=" * 60)
    
    def save_to_transcript(user_text, ai_response):
        """Save conversation to transcript file"""
        with open(transcript_file, "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime('%H:%M:%S')
            f.write(f"[{timestamp}] User: {user_text}\n")
            f.write(f"[{timestamp}] AI: {ai_response}\n\n")
            f.flush()
    
    try:
        with microphone as source:
            print("🎤 Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=2)
            print("✅ Ready! Speak to me...")
            
            # Initialize transcript file
            with open(transcript_file, "w", encoding="utf-8") as f:
                f.write("=== VOICE INPUT + GEMINI AI TEXT OUTPUT ===\n")
                f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("Voice input with Gemini AI text responses\n\n")
            
            while True:
                try:
                    print("\n🎤 Listening... (speak to me)")
                    print("   (I'll wait 2 seconds after you stop talking)")
                    
                    # Listen for complete speech
                    audio = recognizer.listen(
                        source, 
                        timeout=30,
                        phrase_time_limit=60
                    )
                    
                    print("🔄 Processing your speech...")
                    
                    try:
                        # Convert speech to text
                        user_text = recognizer.recognize_google(audio, language='en-US')
                        
                        if user_text and len(user_text.strip()) > 0:
                            print(f"\n👤 You said: {user_text}")
                            
                            # Check for exit commands
                            if any(word in user_text.lower() for word in ["quit", "exit", "stop", "goodbye"]):
                                print("👋 Goodbye!")
                                break
                            
                            # Get AI response from Gemini
                            print("🤖 Thinking...")
                            try:
                                response = model.generate_content(user_text)
                                ai_response = response.text
                                
                                print(f"\n🤖 AI Response:")
                                print(f"   {ai_response}")
                                
                                # Save to transcript
                                save_to_transcript(user_text, ai_response)
                                print("✅ Saved to transcript file")
                                
                            except Exception as e:
                                error_msg = f"Sorry, I had trouble processing that: {e}"
                                print(f"❌ Gemini error: {e}")
                                print(f"   {error_msg}")
                                save_to_transcript(user_text, error_msg)
                            
                            print("\n✅ Ready for next input...")
                        else:
                            print("❌ No speech detected")
                            
                    except sr.UnknownValueError:
                        print("❌ Could not understand - try speaking more clearly")
                    except sr.RequestError as e:
                        print(f"❌ Speech recognition error: {e}")
                
                except sr.WaitTimeoutError:
                    print("⏰ No speech detected - listening again...")
                    continue
                except KeyboardInterrupt:
                    print("\n👋 Stopping...")
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
                    continue
                    
    except Exception as e:
        print(f"❌ Microphone error: {e}")

if __name__ == "__main__":
    main()
