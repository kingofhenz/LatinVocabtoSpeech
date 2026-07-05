import pandas as pd
from gtts import gTTS
from pydub import AudioSegment
import io
import time
import random

def clean_latin(text):
    return str(text).strip()

def make_classical_phonetics(text):
    """
    Swaps ecclesiastical Latin spelling for classical phonetics in memory
    """
    phonetic = text.lower()
    phonetic = phonetic.replace('v', 'w')
    phonetic = phonetic.replace('c', 'k')
    phonetic = phonetic.replace('ae', 'ai') # Makes 'ae' sound like 'eye'
    phonetic = phonetic.replace('oe', 'oi') # Makes 'oe' sound like 'oy'
    return phonetic

def change_speed(audio, speed=1.0):
    """
    Changes the speed of the audio by modifying the frame rate.
    """
    new_sample_rate = int(audio.frame_rate * speed)
    slowed_audio = audio._spawn(audio.raw_data, overrides={'frame_rate': new_sample_rate})
    return slowed_audio.set_frame_rate(audio.frame_rate)

def ensure_column(df, target_name):
    """
    Finds a column matching target_name (case/whitespace-insensitive).
    If it doesn't exist, creates it empty so the script can still run.
    """
    normalized = {c.strip().lower(): c for c in df.columns}
    key = target_name.strip().lower()
    if key in normalized:
        return normalized[key]
    df[target_name] = ''
    return target_name

# Load file
df = pd.read_csv('vocabulary.csv')
df.columns = df.columns.str.strip()

LATIN_COL = ensure_column(df, 'PRINCIPAL PARTS')
DEF_COL = ensure_column(df, 'DEFINITION')

# Create silences in milliseconds
pause_latin_to_eng = AudioSegment.silent(duration=600)  # 0.6 seconds
pause_between_words = AudioSegment.silent(duration=750) # 0.75 seconds

# Process in chunks of 50
chunk_size = 50

for i in range(0, len(df), chunk_size):
    chunk = df.iloc[i:i + chunk_size]
    combined_audio = AudioSegment.empty()
    chunk_index = i // chunk_size + 1
    words_in_chunk = 0

    print(f"\n--- Processing Chunk {chunk_index} (Words {i+1} to {min(i+chunk_size, len(df))}) ---")

    for index, row in chunk.iterrows():
        latin_word = clean_latin(row.get(LATIN_COL, ''))
        definition = str(row.get(DEF_COL, '')).strip()

        if not latin_word or not definition or latin_word.lower() == 'nan' or definition.lower() == 'nan':
            continue

        print(f" Reading: {latin_word}")

        try:
            # Latin audio
            phonetic_latin = make_classical_phonetics(latin_word)
            tts_la = gTTS(text=phonetic_latin, lang='la')
            la_fp = io.BytesIO()
            tts_la.write_to_fp(la_fp)
            la_fp.seek(0)
            audio_la = AudioSegment.from_file(la_fp, format="mp3")
            audio_la = change_speed(audio_la, speed=0.95)

            # English audio
            tts_en = gTTS(text=definition, lang='en')
            en_fp = io.BytesIO()
            tts_en.write_to_fp(en_fp)
            en_fp.seek(0)
            audio_en = AudioSegment.from_file(en_fp, format="mp3")

            # Stitch together
            combined_audio += audio_la + pause_latin_to_eng + audio_en + pause_between_words
            words_in_chunk += 1

            # Random delay to prevent rate limits
            time.sleep(random.uniform(0.25, 0.75))

        except Exception as e:
            print(f" -> Error reading '{latin_word}': {e}")

    if words_in_chunk == 0:
        continue

    output_filename_wav = f"vocab_part_{chunk_index}.wav"
    print(f"Exporting {output_filename_wav}...")
    combined_audio.export(output_filename_wav, format="wav")

print("\nAll done! Your audio files have been created.")
