import glob
import os
import re
import av

def natural_sort_key(path):
    match = re.search(r"(\d+)", os.path.basename(path))
    return int(match.group(1)) if match else 0

def combine_to_m4a(input_pattern="vocab_part_*.wav", output_file="latin_vocabulary.m4a"):
    files = sorted(glob.glob(input_pattern), key=natural_sort_key)
    
    if not files:
        print(f"No files found matching '{input_pattern}'.")
        return

    print(f"Found {len(files)} files. Stitching them into {output_file}...")

    output_container = av.open(output_file, mode="w")
    
    output_stream = output_container.add_stream("aac", rate=24000)
    output_stream.bit_rate = 48000  
    output_stream.layout = "mono" # Force mono. Excellent for voice, saves space.

    # --- THE FIX: Create an Audio Resampler ---
    # This guarantees every piece of audio perfectly matches the AAC stream's requirements
    resampler = av.AudioResampler(
        format=output_stream.format, 
        layout=output_stream.layout,
        rate=output_stream.rate
    )

    processed_count = 0
    skipped_count = 0

    for file in files:
        print(f"Processing {file}...")
        try:
            input_container = av.open(file)
            input_audio_stream = input_container.streams.audio[0]

            for frame in input_container.decode(input_audio_stream):
                # Pass the raw frame through our universal translator
                resampled_frames = resampler.resample(frame)
                
                for res_frame in resampled_frames:
                    res_frame.pts = None # Strip timestamp for sequential writing
                    
                    for packet in output_stream.encode(res_frame):
                        output_container.mux(packet)
            
            input_container.close()
            processed_count += 1
            
        except Exception as e:
            print(f" -> Skipping {file} due to error: {e}")
            skipped_count += 1

    # Flush the resampler (pushes out any last fragments of audio held in its buffer)
    for res_frame in resampler.resample(None):
        for packet in output_stream.encode(res_frame):
            output_container.mux(packet)

    # Flush the encoder (finalizes the file)
    for packet in output_stream.encode(None):
        output_container.mux(packet)

    output_container.close()
    
    print("\n--- Finished ---")
    print(f"Successfully combined {processed_count} files.")
    if skipped_count > 0:
        print(f"Skipped {skipped_count} corrupted files.")
        
    final_size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print(f"Output saved to: {output_file} ({final_size_mb:.2f} MB)")

if __name__ == "__main__":
    combine_to_m4a()
