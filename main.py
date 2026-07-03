import pandas as pd
from gtts import gTTS
from pydub import AudioSegment
import io
import time

def clean_latin(text):
    return text.strip()

def make_classical_phonetics(text):
    """
    Swaps ecclesiastical Latin spelling for classical phonetics 
    (ONLY in memory)
    """
    phonetic = text.lower()
    phonetic = phonetic.replace('v', 'w')
    phonetic = phonetic.replace('c', 'k')
    
    # Optional Classical Latin tones:
    phonetic = phonetic.replace('ae', 'ai') # Makes 'ae' sound like 'eye'
    phonetic = phonetic.replace('oe', 'oi') # Makes 'oe' sound like 'oy'
    
    return phonetic

def change_speed(audio, speed=1.0):
    """
    Changes the speed of the audio by modifying the frame rate.
    Note: Lowering the speed with pydub will also lower the pitch
    """
    new_sample_rate = int(audio.frame_rate * speed)
    
    slowed_audio = audio._spawn(audio.raw_data, overrides={'frame_rate': new_sample_rate})
    
    return slowed_audio.set_frame_rate(audio.frame_rate)

# Load file
df = pd.read_csv('vocabulary.csv')

# Create silences in milliseconds
pause_latin_to_eng = AudioSegment.silent(duration=600)  # 0.6 seconds
pause_between_words = AudioSegment.silent(duration=750) # 0.75 seconds

# Process in chunks of 50
chunk_size = 50

for i in range(0, len(df), chunk_size):
    chunk = df.iloc[i:i + chunk_size]
    
    # Initialize an empty container 
    combined_audio = AudioSegment.empty()
    chunk_index = i // chunk_size + 1
    
    print(f"\n--- Processing Chunk {chunk_index} (Words {i+1} to {min(i+chunk_size, len(df))}) ---")
    
    for index, row in chunk.iterrows():
        # Pull data from CSV
        latin_word = clean_latin(row.get('PRINCIPAL PARTS', ''))
        definition = str(row.get('DEFINITION', '')).strip()
        
        # Skip if data is missing
        if not latin_word or not definition or latin_word.lower() == 'nan':
            continue
            
        print(f" Reading: {latin_word}")
        
        try:
            # 1a. Convert to classical phonetics in memory
            phonetic_latin = make_classical_phonetics(latin_word)
            
            # 1b. Generate Latin Audio into memory 
            tts_la = gTTS(text=phonetic_latin, lang='la')
            la_fp = io.BytesIO()
            tts_la.write_to_fp(la_fp)
            la_fp.seek(0)
            audio_la = AudioSegment.from_file(la_fp, format="mp3")
            
            # 1c. Slow down ONLY the Latin audio to 0.65x
            audio_la = change_speed(audio_la, speed=0.95)
            
            # 2. Generate English Audio into memory
            tts_en = gTTS(text=definition, lang='en')
            en_fp = io.BytesIO()
            tts_en.write_to_fp(en_fp)
            en_fp.seek(0)
            audio_en = AudioSegment.from_file(en_fp, format="mp3")
            
            # 3. Stitch them together
            combined_audio += audio_la + pause_latin_to_eng + audio_en + pause_between_words
            
            # Small delay to prevent rate limits
            time.sleep(0.9)
            
        except Exception as e:
            print(f" -> Error reading '{latin_word}': {e}")
            
    # Export  as WAV
    output_filename_wav = f"vocab_part_{chunk_index}.wav"
    print(f"Exporting {output_filename_wav}...")
    combined_audio.export(output_filename_wav, format="wav")

print("\nAll done! Your audio files have been created.")
