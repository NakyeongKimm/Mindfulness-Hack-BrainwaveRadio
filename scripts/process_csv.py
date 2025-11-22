import csv
import os
from brainwave_core import EEGProcessor, MusicGenerator

def process_from_csv(csv_filename):
    """Process EEG data from CSV file and generate music per person session."""
    
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
    generator = MusicGenerator()
    
    # Create radios folder
    os.makedirs("../radios", exist_ok=True)
    
    # Track sessions
    sessions = []
    current_session_emotions = []
    previous_p_bad = None
    session_count = 0
    filename_counts = {}
    
    # Process each data point
    for idx, eeg in enumerate(data_points):
        # Get p_bad values
        left_p_bad = eeg.get('Left__p_bad', 1)
        right_p_bad = eeg.get('Right__p_bad', 1)
        is_headphone_on = (left_p_bad < 0.5 or right_p_bad < 0.5)
        
        # Detect session start
        if is_headphone_on and (previous_p_bad is None or not previous_p_bad):
            if previous_p_bad is not None:
                session_count += 1
                print(f"\nSESSION {session_count} STARTED (row {idx})")
            current_session_emotions = []
        
        # Detect session end
        elif not is_headphone_on and previous_p_bad:
            if current_session_emotions:
                print(f"SESSION {session_count} ENDED (row {idx})")
                print(f"   Data points: {len(current_session_emotions)}")
                
                # Get unique emotions
                unique_emotions = list(set(current_session_emotions))
                print(f"   Unique emotions: {unique_emotions}")
                
                # Ask user for their desired emotion for this person
                user_emotion = input(f"I want to feel: ").strip().capitalize()
                
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
                
                print(f"Generating music for {all_emotions}...")
                generator.generate_music(all_emotions, duration=20, filename=filename)
                print(f"Saved: {filename}\n")
                
                current_session_emotions = []
        
        # Process data if headphone is on
        if is_headphone_on:
            valence, arousal = processor.extract_features(eeg)
            eeg_emotion = processor.determine_emotion(valence, arousal)
            current_session_emotions.append(eeg_emotion)
            
            if len(current_session_emotions) % 10 == 0:  # Progress every 10 points
                print(f"   Session {session_count}: {len(current_session_emotions)} points collected...")
        
        previous_p_bad = is_headphone_on
    
    # Handle incomplete session at end of file
    if current_session_emotions and session_count > 0:
        print(f"SESSION {session_count} INCOMPLETE (reached end of file)")
        print(f"Data points: {len(current_session_emotions)}")
        
        # Get unique emotions
        unique_emotions = list(set(current_session_emotions))
        print(f"Unique emotions: {unique_emotions}")
        
        # Ask user for desired emotion
        user_emotion = input(f"I want to feel: ").strip().capitalize()
        
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
        
        print(f"Generating music for {all_emotions}...")
        generator.generate_music(all_emotions, duration=20, filename=filename)
        print(f"Saved: {filename}\n")
    
    print(f"Processed {session_count} sessions from CSV!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        csv_file = input("Enter CSV filename (e.g., data/eeg_data_20231122_143000.csv): ").strip()
    
    if not os.path.exists(csv_file):
        print(f"File not found: {csv_file}")
    else:
        process_from_csv(csv_file)
