import time
import os
from brainwave_core import EEGProcessor, MusicGenerator

def test_data():
    # Data provided by user
    data_points = [
        {'Left__total_power': 21135745.8154917, 'Left__delta': 0.006540136886535747, 'Left__theta': 0.02849005547458703, 'Left__alpha': 0.023955596666606627, 'Left__beta': 0.13258223592915666, 'Left__beta_low': 0.037634196683480274, 'Left__beta_high': 0.09494803924567645, 'Left__gamma': 0.808431975043114, 'Left__a_ta': 0.4643415986366913, 'Left__b_tb': 0.8273938569584512, 'Left__b_ab': 0.8471440038809874, 'Left__mab_tmab': 0.8273979534714393, 'Left__p_bad': 0.7510881722628432, 'Right__total_power': 12164520849.98057, 'Right__delta': 0.06342370401366408, 'Right__theta': 0.426370879772638, 'Right__alpha': 0.13883929940313472, 'Right__beta': 0.1673352877381924, 'Right__beta_low': 0.07719544973533496, 'Right__beta_high': 0.09013983800285741, 'Right__gamma': 0.20403082907237072, 'Right__a_ta': 0.2643213156834539, 'Right__b_tb': 0.3049852110370289, 'Right__b_ab': 0.5262367885447691, 'Right__mab_tmab': 0.34024438293880016, 'Right__p_bad': 0.9999000000000002, 'time': 1763830571.2155955},
        {'Left__total_power': 19651162.41040105, 'Left__delta': 0.006590138231462802, 'Left__theta': 0.028638233441746905, 'Left__alpha': 0.023949847360914038, 'Left__beta': 0.13251350517745708, 'Left__beta_low': 0.03759756000891651, 'Left__beta_high': 0.09491594516854059, 'Left__gamma': 0.8083082757884192, 'Left__a_ta': 0.46430503428071596, 'Left__b_tb': 0.827274584390503, 'Left__b_ab': 0.8469827322261089, 'Left__mab_tmab': 0.8273026647736853, 'Left__p_bad': 0.7510881722628432, 'Right__total_power': 11224586199.81794, 'Right__delta': 0.06788747236763885, 'Right__theta': 0.49368566474380704, 'Right__alpha': 0.1556943246102349, 'Right__beta': 0.13470711192265342, 'Right__beta_low': 0.05314031173407067, 'Right__beta_high': 0.08156680018858273, 'Right__gamma': 0.1480254263556664, 'Right__a_ta': 0.2570720621516548, 'Right__b_tb': 0.2324460794075013, 'Right__b_ab': 0.4470859596117011, 'Right__mab_tmab': 0.27886603982304553, 'Right__p_bad': 0.9999000000000002, 'time': 1763830572.266945}
    ]

    processor = EEGProcessor()
    generator = MusicGenerator()
    
    # Create radios folder if it doesn't exist
    os.makedirs("../radios", exist_ok=True)
    
    # Mock user input
    user_emotion = "Relaxed"
    print(f"User Emotion: {user_emotion}")

    for i, data in enumerate(data_points):
        print(f"Processing Data Point {i+1}")
        valence, arousal = processor.extract_features(data)
        eeg_emotion = processor.determine_emotion(valence, arousal)
        print(f"Detected EEG Emotion: {eeg_emotion} (Valence: {valence:.2f}, Arousal: {arousal:.2f})")
        
        emotions = [eeg_emotion, user_emotion]
        filename = f"../radios/test_output_{i+1}.wav"
        
        print(f"Generating music for {emotions}...")
        generator.generate_music(emotions, duration=10, filename=filename)

if __name__ == "__main__":
    test_data()
