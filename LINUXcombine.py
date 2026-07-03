import os
import subprocess

def parse_user_input(user_input):
    parts = set()
    try:
        for item in user_input.split(','):
            item = item.strip()
            if '-' in item:
                start, end = map(int, item.split('-'))
                parts.update(range(start, end + 1))
            elif item.isdigit():
                parts.add(int(item))
        return sorted(list(parts))
    except ValueError:
        print("Error: Please enter numbers in a valid format (e.g., 1, 2, 3 or 1-5).")
        return []

def stitch_to_native_aac(file_list, output_filename="master.m4a"):
    """
    Uses FFmpeg's native built-in encoder. This avoids requiring external codec libraries (like libmp3lame or libopus).
    """
    # Filter out files that don't exist
    valid_files = [f for f in file_list if os.path.exists(f)]
    
    if not valid_files:
        print("No valid files found to stitch. Please check your part numbers.")
        return

    list_filename = "concat_list.txt"
    with open(list_filename, 'w') as f:
        for file in valid_files:
            f.write(f"file '{file}'\n")

    print(f"\nStitching and compressing {len(valid_files)} files into {output_filename}...")
    print("Using built-in native encoder. Please wait...\n")
    
    # -c:a aac: Uses FFmpeg's native internal AAC encoder (always exists)
    # -b:a 32k: Capped at a very low bitrate for highly efficient file sizes
    command = [
        "ffmpeg", 
        "-y",               
        "-f", "concat", 
        "-safe", "0", 
        "-i", list_filename, 
        "-c:a", "aac", 
        "-b:a", "32k", 
        output_filename
    ]

    try:
        
        result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        
        if result.returncode == 0:
            print(f"✅ Success! Your highly compressed file is ready: {output_filename}")
            print("File compression completed natively.")
        else:
            print("\n[!] FFmpeg encountered an error:")
            print(result.stderr.decode('utf-8', errors='ignore'))
            
    except FileNotFoundError:
        print("\n[!] Error: FFmpeg is not installed or not in your system PATH.")
    finally:
        # Clean up the temporary text file
        if os.path.exists(list_filename):
            os.remove(list_filename)

if __name__ == "__main__":
    print("--- Native Compression Audio Stitcher ---")
    user_input = input("Enter the vocab parts you want to stitch (e.g., '1, 2, 3' or '1-300'): ")
    
    parts = parse_user_input(user_input)
    
    if parts:
        filenames = [f"vocab_part_{p}.wav" for p in parts]
        stitch_to_native_aac(filenames)
