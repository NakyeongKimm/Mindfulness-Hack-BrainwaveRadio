import csv
import os
from brainwave_core import EEGProcessor, MusicGenerator
from collections import Counter

def process_community_from_csv(csv_filename):
    """Generate community sound from CSV file - one music for all people."""
    
    print(f"Brainwave Radio - Community Sound from CSV")
    print(f"Reading data from: {csv_filename}")
    
    # Read CSV
    data_points = []
    with open(csv_filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Convert string values back to float
            converted_row = {}
            for key, value in row.items():
                try:
                    converted_row[key] = float(value)
                except (ValueError, TypeError):
                    converted_row[key] = value
            data_points.append(converted_row)
    
    print(f"Loaded {len(data_points)} data points\n")
    
    # Initialize components
    processor = EEGProcessor()
    
    # Track sessions (one per person)
    sessions = []
    current_session_emotions = []
    previous_p_bad = None
    session_count = 0
    
    # Process each data point to find sessions
    print("Detecting person sessions...\n")
    for idx, eeg in enumerate(data_points):
        # Get p_bad values
        left_p_bad = eeg.get('Left__p_bad', 1)
        right_p_bad = eeg.get('Right__p_bad', 1)
        is_headphone_on = (left_p_bad < 0.5 or right_p_bad < 0.5)
        
        # Detect session start
        if is_headphone_on and (previous_p_bad is None or not previous_p_bad):
            if previous_p_bad is not None:
                session_count += 1
                print(f"Person {session_count} started session (row {idx})")
            current_session_emotions = []
        
        # Detect session end
        elif not is_headphone_on and previous_p_bad:
            if current_session_emotions:
                # Get unique emotions for this person
                unique_emotions = list(set(current_session_emotions))
                sessions.append(unique_emotions)
                
                print(f"Person {session_count} ended session (row {idx})")
                print(f"Data points: {len(current_session_emotions)}")
                print(f"Unique emotions: {unique_emotions}\n")
                
                current_session_emotions = []
        
        # Process data if headphone is on
        if is_headphone_on:
            valence, arousal = processor.extract_features(eeg)
            eeg_emotion = processor.determine_emotion(valence, arousal)
            current_session_emotions.append(eeg_emotion)
        
        previous_p_bad = is_headphone_on
    
    if not sessions:
        print("No sessions found in CSV. Make sure the data has p_bad values.")
        return
    
    # Aggregate emotions across all people (each person counted once)
    all_emotions = []
    for session_emotions in sessions:
        all_emotions.extend(session_emotions)
    
    emotion_counts = Counter(all_emotions)
    most_common_emotion = emotion_counts.most_common(1)[0][0]
    
    print(f"Community Emotional State")
    print(f"Total People: {len(sessions)}")
    print(f"Most Common Emotion: {most_common_emotion}")
    print(f"Emotion Distribution: {dict(emotion_counts)}")
    print(f"{'='*60}\n")
    
    # Generate "Community Sound"
    print(f"Generating 'Community Sound'...")
    generator = MusicGenerator()
    
    # Create radios folder if it doesn't exist
    os.makedirs("radios", exist_ok=True)
    
    # Use only the community's most common emotion
    community_emotions = [most_common_emotion]
    
    generator.generate_music(
        emotions=community_emotions, 
        duration=30,
        filename="radios/community_sound.wav"
    )
    
    print("Community Sound generated: radios/community_sound.wav")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        csv_file = input("Enter CSV filename (e.g., data/eeg_data_20251122_144953.csv): ").strip()
    
    if not os.path.exists(csv_file):
        print(f"File not found: {csv_file}")
    else:
        process_community_from_csv(csv_file)
