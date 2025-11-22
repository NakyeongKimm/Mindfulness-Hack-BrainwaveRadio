import asyncio
import json
import ssl
import websockets
import csv
import os
from datetime import datetime
import time

HUB_IP = "your_hub_ip"

def save_to_csv(data, filename):
    """
    Save collected data to CSV file.
    Created this function to auto-save collected data to CSV file as the server is unstable.
    """
    if not data:
        return
    
    # Get all unique keys
    all_keys = set()
    for row in data:
        all_keys.update(row.keys())
    
    fieldnames = sorted(list(all_keys))
    
    # auto-save every 10 points
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"Auto-saved {len(data)} points to {filename}")

async def collect_with_retry(num_samples, csv_filename, max_retries=5):
    """Collect data with automatic retry on connection failure."""
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    collected_data = []
    retry_count = 0
    
    while len(collected_data) < num_samples and retry_count < max_retries:
        try:
            print(f"\n{'='*60}")
            if retry_count > 0:
                print(f"Retry attempt {retry_count}/{max_retries}")
                print(f"Already collected: {len(collected_data)}/{num_samples}")
                await asyncio.sleep(2)  # Wait before retry
            
            print(f"Connecting to {HUB_IP}...")
            print(f"{'='*60}\n")
            
            async with websockets.connect(
                f"wss://{HUB_IP}", 
                ssl=ssl_context,
                open_timeout=60,
                close_timeout=10,
                ping_interval=None,
                ping_timeout=None
            ) as ws:
                print(f"Connected! Collecting data...")
                print(f"Target: {num_samples} points | Current: {len(collected_data)}\n")
                
                async for msg in ws:
                    try:
                        eeg = json.loads(msg)
                        collected_data.append(eeg)
                        
                        # Show progress
                        left_p_bad = eeg.get('Left__p_bad', 1)
                        right_p_bad = eeg.get('Right__p_bad', 1)
                        print(f"[{len(collected_data)}/{num_samples}] L_p_bad: {left_p_bad:.2f}, R_p_bad: {right_p_bad:.2f}")
                        
                        # Auto-save every 10 points
                        if len(collected_data) % 10 == 0:
                            save_to_csv(collected_data, csv_filename)
                        
                        if len(collected_data) >= num_samples:
                            print(f"\nCollected {num_samples} data points!")
                            break
                            
                    except Exception as e:
                        print(f"Error processing message: {e}")
        
        except asyncio.TimeoutError:
            retry_count += 1
            print(f"Connection timeout (attempt {retry_count}/{max_retries})")
            if len(collected_data) > 0:
                save_to_csv(collected_data, csv_filename)
        
        except Exception as e:
            retry_count += 1
            print(f"Connection error: {e}")
            if len(collected_data) > 0:
                save_to_csv(collected_data, csv_filename)
    
    return collected_data

async def main():
    print(f"Brainwave Radio - Data Collector")
    
    # How many data points to collect?
    num_samples = int(input("How many data points to collect? (e.g., 100): ").strip())
    
    # Create data folder if it doesn't exist
    os.makedirs("../data", exist_ok=True)
    
    # Create CSV filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"../data/eeg_data_{timestamp}.csv"
    
    print(f"Will save to: {csv_filename}")
    print(f"Auto-save: Every 10 points")
    print(f"Max retries: 5 attempts\n")
    
    # Collect with retry
    collected_data = await collect_with_retry(num_samples, csv_filename, max_retries=5)
    
    # Final save
    if collected_data:
        save_to_csv(collected_data, csv_filename)
        
        print(f" COLLECTION COMPLETE")
        print(f"File: {csv_filename}")
        print(f"Total rows: {len(collected_data)}")
        
        # Get all unique keys
        all_keys = set()
        for data in collected_data:
            all_keys.update(data.keys())
        print(f"Total columns: {len(all_keys)}")
        print(f"\nYou can now process this data offline with:")
        print(f"  python process_csv.py {csv_filename}")
    else:
        print("No data collected. Server may be down.")

if __name__ == "__main__":
    asyncio.run(main())

