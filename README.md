# Latin Vocabulary Audio Generator

Turns a Latin vocabulary CSV into spoken-word study audio then stitches the results into one file.

## Install

```bash
pip install pandas gTTS pydub av
```


## What Each File Does

### `f4.py`
Reads `vocabulary.csv` (columns: `PRINCIPAL PARTS` and `DEFINITION`) and generates the audio. For each word, it uses Google TTS to read the Latin word out loud (converted to classical pronunciation first), then uses Google TTS again to read the English definition. It saves the results in batches of 50 words as `vocab_part_1.wav`, `vocab_part_2.wav`, etc. Works on any platform.

### `LINUXstitcher.py`
Combines whichever `vocab_part_N.wav` files you choose into one compressed `master.m4a` file. **Linux only** — it calls the `ffmpeg` command directly using a method that doesn't play nice with Windows file paths. If you're not on Linux, use `stitcher_cross_platform.py` instead. 

To use LUNUXstitcher you also need **FFmpeg** installed and on your system PATH:

- **Linux:** `sudo apt install ffmpeg`
- **macOS:** `brew install ffmpeg`
- **Windows:** download from ffmpeg.org and add its `bin` folder to your PATH

### `stitcher_cross_platform.py`
Does the same job as `LINUXstitcher.py` — combines your `vocab_part_N.wav` files into one compressed file — but works identically on **Windows, macOS, and Linux**.

## How to Use

1. Put `vocabulary.csv` in the same folder as `f4.py`, then run:
   ```bash
   python f4.py
   ```
   This creates your `vocab_part_N.wav` files.

2. Run the stitcher that matches your OS:
   ```bash
   python LINUXstitcher.py            # Linux only
   python stitcher_cross_platform.py  # any OS
   ```
   When prompted, enter which parts to combine, e.g. `1, 2, 3` or `1-300`.

3. You'll end up with one compressed audio file ready to load onto a phone or player.

## customization

changing this will change the speed on the LATIN ONLY:

 ```bash
   audio_la = change_speed(audio_la, speed=0.95)
   ```
Changing these will change the pause interval after each latin and english word, both times are in milliseconds

 ```bash
    pause_latin_to_eng = AudioSegment.silent(duration=600) 
    pause_between_words = AudioSegment.silent(duration=750)
    ```
