import asyncio
import json
import ssl
import websockets
from brainwave_core import EEGProcessor, MusicGenerator
import time
import os

HUB_IP = "your_hub_ip"

async def main():
    print(f"Connecting to {HUB_IP}")
    
    # Initialize Core Components
    processor = EEGProcessor()

    # Disable SSL certificate verification (for testing only)
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # Create radios folder if it doesn't exist
    os.makedirs("../radios", exist_ok=True)
    
    # Initialize generator once (loads model)
    print("Initializing MusicGen model...")
    generator = MusicGenerator()
    
    # Track sessions
    current_session_emotions = []  # Emotions in current session
    previous_p_bad = None
    session_count = 0
    filename_counts = {}
    
    try:
        # Disable ping/pong since music generation blocks the async loop
        async with websockets.connect(
            f"wss://{HUB_IP}", 
            ssl=ssl_context,
            open_timeout=60,
            close_timeout=10,
            ping_interval=None,  # Disable automatic pings
            ping_timeout=None
        ) as ws:
            print("Connected to stream. Monitoring for person sessions...")
            print("(A session starts when headphone is on)")
            print("(A session ends when headphone is off)\n")
            
            async for msg in ws:
                try:
                    eeg = json.loads(msg)
                    
                    # Get p_bad values (check both Left and Right)
                    left_p_bad = eeg.get('Left__p_bad', 1)
                    right_p_bad = eeg.get('Right__p_bad', 1)
                    
                    # Consider headphone "on" if either side is on (p_bad close to 0)
                    # Using threshold because p_bad might not be exactly 0 or 1
                    is_headphone_on = (left_p_bad < 0.5 or right_p_bad < 0.5)
                    
                    # Detect session start (headphone put on)
                    if is_headphone_on and (previous_p_bad is None or not previous_p_bad):
                        if previous_p_bad is not None:  # Not the first data point
                            session_count += 1
                            print(f"\n{'='*60}")
                            print(f"🎧 SESSION {session_count} STARTED")
                            print(f"{'='*60}")
                        current_session_emotions = []
                    
                    # Detect session end (headphone taken off)
                    elif not is_headphone_on and previous_p_bad:
                        if current_session_emotions:
                            print(f"\n{'='*60}")
                            print(f"🎧 SESSION {session_count} ENDED")
                            print(f"Total data points: {len(current_session_emotions)}")
                            print(f"{'='*60}\n")
                            
                            # Get unique emotions from this session
                            unique_emotions = list(set(current_session_emotions))
                            print(f"Unique emotions experienced: {unique_emotions}")
                            
                            # Ask user for their desired emotion for this person
                            user_emotion = input(f"What emotion do you want this person to feel?: ").strip().capitalize()
                            
                            # Create prompt with all unique emotions + user emotion
                            all_emotions = unique_emotions + [user_emotion]
                            
                            # Create filename
                            emotions_str = "_".join([e.lower() for e in unique_emotions])
                            base_name = f"session{session_count}_{emotions_str}_{user_emotion.lower()}"
                            
                            # Handle duplicates
                            if base_name in filename_counts:
                                filename_counts[base_name] += 1
                                filename = f"../radios/{base_name}_{filename_counts[base_name]}.wav"
                            else:
                                filename_counts[base_name] = 0
                                filename = f"../radios/{base_name}.wav"
                            
                            print(f"\nGenerating music for {all_emotions}...")
                            generator.generate_music(all_emotions, duration=20, filename=filename)
                            print(f"✓ Saved: {filename}\n")
                            
                            current_session_emotions = []
                    
                    # Process data if headphone is on
                    if is_headphone_on:
                        valence, arousal = processor.extract_features(eeg)
                        eeg_emotion = processor.determine_emotion(valence, arousal)
                        current_session_emotions.append(eeg_emotion)
                        
                        print(f"[Session {session_count}, Point {len(current_session_emotions)}] {eeg_emotion} (V:{valence:.2f}, A:{arousal:.2f}, L_p_bad:{left_p_bad:.2f}, R_p_bad:{right_p_bad:.2f})")
                    
                    previous_p_bad = is_headphone_on
                    
                except Exception as e:
                    print(f"Error processing message: {e}")
    
    except asyncio.TimeoutError:
        print("\nCheck server availability") #server is unstable or down
    except Exception as e:
        print(f"\nConnection error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
