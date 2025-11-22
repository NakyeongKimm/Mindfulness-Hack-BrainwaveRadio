# Brainwave Radio 🎵

Generate music from EEG brainwave data using Meta's MusicGen model.

Check our demo: https://www.figma.com/proto/1aJlm5AKHwtTGDSrztZMKc/Brainwave-Radio?node-id=0-1&t=Zu52wPhsLEi8PjEm-1

## Directory Structure

```
Mindfulness-Hack-BrainwaveRadio/
├── scripts/                    # All Python scripts
│   ├── brainwave_core.py      # Core EEG processing & music generation
│   ├── collect_data.py        # Collect EEG data to CSV
│   ├── process_csv.py         # Generate music per person from CSV
│   ├── community_from_csv.py  # Generate community sound from CSV
│   ├── brainwave_stream.py    # Real-time streaming (requires server)
│   ├── community_sound.py     # Real-time community sound (requires server)
│   └── test_brainwave.py      # Test with hardcoded data
├── data/                       # Collected EEG data (CSV files)
│   └── eeg_data_*.csv         # Auto-generated timestamped files
├── radios/                     # Generated music files
│   ├── session*_*.wav         # Individual person music
│   ├── community_sound.wav    # Community aggregated music
│   └── test_output_*.wav      # Test output files
└── README.md                   # This file
```

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/Mindfulness-Hack-BrainwaveRadio.git
cd Mindfulness-Hack-BrainwaveRadio
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

**Note**: First run will download the MusicGen model (~2.4GB)

## Quick Start

### Activate Environment
```bash
conda activate <your_environment>
cd /path/to/Mindfulness-Hack-BrainwaveRadio
```

## Commands

### 0. Collect Data to CSV (Offline Use)
Save EEG data from the server to work offline later.

```bash
cd scripts
python collect_data.py
```

**What it does:**
- Connects to the server
- Collects N data points
- Saves to `data/eeg_data_TIMESTAMP.csv`
- No music generation (just data collection)

---

### 0b. Process Saved CSV Data
Generate music from previously saved CSV data (no server needed).

```bash
cd scripts
python process_csv.py ../data/eeg_data_YYYYMMDD_HHMMSS.csv
```

**What it does:**
- Reads EEG data from CSV
- Detects person sessions (using p_bad)
- Generates music for each person
- Works completely offline!

---

### 0c. Community Sound from CSV
Generate community sound from saved CSV data (no server needed).

```bash
cd scripts
python community_from_csv.py ../data/eeg_data_YYYYMMDD_HHMMSS.csv
```

**What it does:**
- Reads EEG data from CSV
- Detects all person sessions
- Aggregates emotions (each person counted once)
- Generates one 30s community sound
- Works completely offline!

---

### 1. Real-time Stream (Continuous)
Connects to WebSocket and generates music for **every** incoming data point.

```bash
cd scripts
python brainwave_stream.py
```

**What it does:**
- Connects to `wss://stream2.mindfulmakers.xyz`
- Asks for your desired emotion
- Processes all incoming EEG data continuously
- Generates music files: `radios/sad_energized.wav`, `radios/sad_energized_1.wav`, etc.
- Press `Ctrl+C` to stop

---

### 2. Community Sound (Aggregated)
Collects N data points and generates **one** collective music file.

```bash
cd scripts
python community_sound.py
```

**What it does:**
- Asks how many data points to collect (e.g., 10)
- Aggregates emotions from the community
- Generates one 30-second file: `radios/community_sound.wav`

---

### 3. Test Mode
Tests the system with hardcoded data points.

```bash
cd scripts
python test_brainwave.py
```
- Tests with 2 hardcoded samples
- Files: `radios/test_output_1.wav`, `radios/test_output_2.wav`

---

## File Naming

### Stream Mode
Files are named based on emotions:
- `{eeg_emotion}_{user_emotion}.wav` (first occurrence)
- `{eeg_emotion}_{user_emotion}_1.wav` (second occurrence)
- `{eeg_emotion}_{user_emotion}_2.wav` (third occurrence)

**Examples:**
- `sad_energized.wav`
- `happy_calm.wav`
- `stressed_relaxed_1.wav`

### Community Mode
- `community_sound.wav` (always the same name, overwrites previous)

---

## Tips

- **First run takes longer** - MusicGen model (~2.4GB) downloads on first use
- **Generation is slow** - Each 10s clip takes ~10-20 seconds to generate
- **Stop anytime** - Press `Ctrl+C` to stop streaming
- **Check output** - All `.wav` files are saved in the current directory

---

## Troubleshooting

### "Command not found"
Make sure you're in the correct directory:
```bash
cd /path/to/Mindfulness-Hack-BrainwaveRadio
```

### "Module not found"
Activate the conda environment:
```bash
conda activate <your_environment>
```

### "Connection failed"
Check your internet connection and VPN settings.
