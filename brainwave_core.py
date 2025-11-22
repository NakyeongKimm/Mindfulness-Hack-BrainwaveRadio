import ast
import numpy as np
from scipy.io import wavfile
import math
import torch
from transformers import pipeline
import os

class EEGProcessor:
    def parse_input(self, data_str):
        """Parses the input string into a dictionary."""
        try:
            if isinstance(data_str, dict):
                return data_str
            return ast.literal_eval(data_str)
        except Exception as e:
            print(f"Error parsing input: {e}")
            return None

    def extract_features(self, data):
        """
        Computes Valence and Arousal from EEG data.
        Calculated based on the paper: Detecting emotions through EEG signals based on modified convolutional fuzzy neural network.
        """
        l_alpha = data.get('Left__alpha', 0)
        r_alpha = data.get('Right__alpha', 0)
        
        l_beta = data.get('Left__beta', 0)
        r_beta = data.get('Right__beta', 0)
        
        if l_alpha + r_alpha == 0:
            valence = 0
        else:
            """
            Valence: How positive (pleasant) or negative (unpleasant) the emotion is.
            """
            valence = (r_alpha - l_alpha) / (r_alpha + l_alpha)

        avg_alpha = (l_alpha + r_alpha) / 2
        avg_beta = (l_beta + r_beta) / 2
        
        if avg_alpha == 0:
            arousal = 0
        else:
            """
            Arousal: How intense or calm the emotion is (from excited to sleepy).
            """
            arousal = avg_beta / avg_alpha
            
        return valence, arousal

    def determine_emotion(self, valence, arousal):
        # Arousal Thresholds: Low < Moderate < High
        arousal_low_to_moderate_threshold = 0.5
        arousal_moderate_to_high_threshold = 1.0  
        
        # Valence Thresholds: Negative < Neutral < Positive
        valence_negative_threshold = -0.5
        valence_positive_threshold = 0.5
        
        
        # High Arousal (A >= 1.0)
        if arousal >= arousal_moderate_to_high_threshold:
            if valence >= valence_positive_threshold:
                return "Excited"  # High V, High A
            elif valence < valence_negative_threshold:
                return "Angry"    # Negative V, High A
            else: # -0.5 <= valence < 0.5
                return "Tense"    # Neutral V, High A

        # Moderate Arousal (0.5 <= A < 1.0)
        elif arousal >= arousal_low_to_moderate_threshold:
            if valence >= valence_positive_threshold:
                return "Happy"    # High V, Moderate A
            elif valence < valence_negative_threshold:
                return "Stressed" # Negative V, Moderate A
            else: # -0.5 <= valence < 0.5
                return "Bored"    # Neutral V, Moderate A

        # Low Arousal (A < 0.5)
        else: # arousal < arousal_low_to_moderate_threshold
            if valence >= valence_positive_threshold:
                return "Relaxed"  # High V, Low A
            elif valence < valence_negative_threshold:
                return "Sad"      # Negative V, Low A
            else: # -0.5 <= valence < 0.5
                return "Calm"     # Neutral V, Low A

from transformers import AutoProcessor, MusicgenForConditionalGeneration

class MusicGenerator:
    def __init__(self):
        print("Loading MusicGen model... this might take a while...")
        self.processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
        self.model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")
        
    def get_prompt(self, emotions):
        # make a prompt to generate music based on the emotion detected by EEG
        
        base_prompts = {
        # High Arousal (Top Row)
        "Excited": "Vibrant, ecstatic, major scale, very fast tempo, dynamic rhythm, bright synth lead, EDM/Pop style, high energy",
        "Tense": "Anxious, suspenseful, moderate-to-fast tempo, dissonant chords, rising pitch, aggressive percussion, cinematic/electronic, unsettling",
        "Angry": "Aggressive, volatile, very fast tempo, highly dissonant, heavy distortion, intense rhythm section, Heavy Metal/Punk style, loud",

        # Moderate Arousal (Middle Row)
        "Happy": "Upbeat, cheerful, major scale, fast tempo, pop style, clear melody, bright brass/strings",
        "Bored": "Dull, monotonous, moderate-to-slow tempo, repetitive motif, simple texture, neutral key, lo-fi or elevator music",
        "Stressed": "Intense, chaotic, fast tempo, minor key, complex rhythm, electronic textures, high energy, dark atmosphere",

        # Low Arousal (Bottom Row)
        "Relaxed": "Serene, peaceful, slow tempo, gentle major/modal scale, soft textures, acoustic guitar, nature sounds, ambient, tranquil",
        "Calm": "Tranquil, centered, very slow tempo, smooth textures, simple harmonies, meditation or ambient style, soft piano",
        "Sad": "Melancholic, sorrowful, slow tempo, minor scale, sparse arrangement, emotional piano/strings, ballad style"
        }
        
        # Construct prompt
        prompt_parts = []
        
        # All emotions except the last one are EEG detected
        # Last emotion is user input about how the user wants to feel.
        eeg_emotions = emotions[:-1] if len(emotions) > 1 else emotions
        user_emotion = emotions[-1] if len(emotions) > 1 else None
        
        # Add EEG emotions
        for emotion in eeg_emotions:
            if emotion in base_prompts:
                prompt_parts.append(base_prompts[emotion])
            else:
                prompt_parts.append(f"{emotion} mood")
        
        # Add user emotion with "want to feel" prefix
        if user_emotion and len(emotions) > 1:
            if user_emotion in base_prompts:
                prompt_parts.append(f"want to feel {base_prompts[user_emotion]}")
            else:
                prompt_parts.append(f"want to feel {user_emotion} mood")
                
        final_prompt = f"A high quality music track. {', '.join(prompt_parts)}"
        return final_prompt

    def generate_music(self, emotions, duration=10, filename="output_music.wav"):
        """Generates a music file based on a list of emotions."""
        prompt = self.get_prompt(emotions)
        print(f"Generating music with prompt: '{prompt}'")
        
        inputs = self.processor(
            text=[prompt],
            padding=True,
            return_tensors="pt",
        )
        
        # Calculate max_new_tokens
        # MusicGen generates at 50 Hz frame rate
        tokens = int(duration * 50)
        
        audio_values = self.model.generate(**inputs, max_new_tokens=tokens)
        
        # audio_values is (batch, channels, samples)
        # We take the first one
        audio_data = audio_values[0].cpu().numpy()
        
        sampling_rate = self.model.config.audio_encoder.sampling_rate
        
        # Scipy expects (samples, channels)
        # Current shape (channels, samples) -> Transpose
        if audio_data.ndim > 1:
            audio_data = audio_data.T
            
        wavfile.write(filename, sampling_rate, audio_data)
        print(f"Generated music saved to {filename}")
