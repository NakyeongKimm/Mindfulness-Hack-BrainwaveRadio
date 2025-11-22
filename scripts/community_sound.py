import asyncio
import json
import ssl
import websockets
from brainwave_core import EEGProcessor, MusicGenerator
from collections import Counter
import os

HUB_IP = "your_hub_ip"

async def main():
    print(f"Connecting to {HUB_IP}")
    
    # Initialize Core Components
    processor = EEGProcessor()
    
    # How many people/sessions to collect?
    num_sessions = int(input("How many people/sessions to collect? (e.g., 5): ").strip())

    # Disable SSL certificate verification (for testing only)
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # Track sessions (one per person)
    sessions = []  # List of sessions, each session has unique emotions
    current_session_emotions = []
    previous_p_bad = None
    session_count = 0
    
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
            print(f"Connected to stream. Collecting {num_sessions} person sessions...")
            print("(Each person = one session from headphone on to off)\n")
            
            async for msg in ws:
                try:
                    eeg = json.loads(msg)
                    
                    # Get p_bad values
                    left_p_bad = eeg.get('Left__p_bad', 1)
                    right_p_bad = eeg.get('Right__p_bad', 1)
                    is_headphone_on = (left_p_bad < 0.5 or right_p_bad < 0.5)
                    
                    # Detect session start
                    if is_headphone_on and (previous_p_bad is None or not previous_p_bad):
                        if previous_p_bad is not None:
                            session_count += 1
                            print(f"Person {session_count} started session")
                        current_session_emotions = []
                    
                    # Detect session end
                    elif not is_headphone_on and previous_p_bad:
                        if current_session_emotions:
                            # Get unique emotions for this person
                            unique_emotions = list(set(current_session_emotions))
                            sessions.append(unique_emotions)
                            
                            print(f"Person {session_count} ended session")
                            print(f"Data points: {len(current_session_emotions)}")
                            print(f"Unique emotions: {unique_emotions}")
                            print(f"Total people collected: {len(sessions)}/{num_sessions}\n")
                            
                            current_session_emotions = []
                            
                            # Check if we have enough sessions
                            if len(sessions) >= num_sessions:
                                print(f"Collected {num_sessions} people sessions!")
                                break
                    
                    # Process data if headphone is on
                    if is_headphone_on:
                        valence, arousal = processor.extract_features(eeg)
                        eeg_emotion = processor.determine_emotion(valence, arousal)
                        current_session_emotions.append(eeg_emotion)
                    
                    previous_p_bad = is_headphone_on
                    
                except Exception as e:
                    print(f"Error processing message: {e}")
    
    except asyncio.TimeoutError:
        print("Connection timeout. Please check the server.")
        return
    except Exception as e:
        print(f"Connection error: {e}")
        return
    
    if not sessions:
        print("No sessions collected. Exiting.")
        return
    
    # Aggregate emotions across all people (each person counted once)
    all_emotions = []
    for session_emotions in sessions:
        # Each person contributes their most common emotion
        # Or we can use all unique emotions from each person
        all_emotions.extend(session_emotions)
    
    emotion_counts = Counter(all_emotions)
    most_common_emotion = emotion_counts.most_common(1)[0][0]
    
    print(f"Community Emotional State")
    print(f"Total People: {len(sessions)}")
    print(f"Most Common Emotion: {most_common_emotion}")
    print(f"Emotion Distribution: {dict(emotion_counts)}")
    
    # Generate "Community Sound"
    print(f"Generating 'Community Sound'...")
    generator = MusicGenerator()
    
    # Create radios folder if it doesn't exist
    os.makedirs("../radios", exist_ok=True)
    
    # Use only the community's most common emotion
    community_emotions = [most_common_emotion]
    
    generator.generate_music(
        emotions=community_emotions, 
        duration=30,  # Longer for community sound
        filename="../radios/community_sound.wav"
    )
    
    print("Community Sound generated: radios/community_sound.wav")

if __name__ == "__main__":
    asyncio.run(main())
