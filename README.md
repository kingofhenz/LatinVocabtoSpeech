# WARNING
Project is in early developement and hasnt been ran on any OS other than linux. Please create issues on github as you notice them
# Latin Vocabulary Audio Generator

Turns a Latin vocabulary CSV into spoken-word study audio then stitches the results into one file.

## Install

```bash
pip install pandas gTTS pydub av
```


## What Each File Does

### `main.py`
Reads `vocabulary.csv` (columns: `PRINCIPAL PARTS` and `DEFINITION`) and generates the audio. For each word, it uses Google TTS to read the Latin word out loud (converted to classical pronunciation ), then uses Google TTS again to read the English definition. It saves the results in batches of 50 words as `vocab_part_1.wav`, `vocab_part_2.wav`, etc. Works on any platform.

### `LINUXstitcher.py`
Combines whichever `vocab_part_X.wav` files you choose into one compressed `master.m4a` file. 
**Linux only** — it calls the `ffmpeg` command directly using a method that doesn't play nice with Windows file paths. If you're not on Linux, use `combine.py` instead. 

To use LUNUXstitcher you also need **FFmpeg** installed and on your system PATH:

- **Linux:** `sudo apt install ffmpeg`
- **macOS:** `brew install ffmpeg`
- **Windows:** download from ffmpeg.org and add its `bin` folder to your PATH (Wouldnt reccomenD installing FFMPEG just for this)

### `stitcher_cross_platform.py`
Does the same job as `LINUXcombine.py` — combines your `vocab_part_X.wav` files into one compressed file —  works identically on **Windows, macOS, and Linux**.

## How to Use

1. Put `vocabulary.csv` in the same folder as `main.py`, then run:
   ```bash
   python main.py
   ```
   This creates your `vocab_part_X.wav` files.

2. Run the stitcher that matches your OS:
   ```bash
   python LINUXcombine.py    # Linux only
   python combine.py         # any OS
   ```
   When prompted, enter which parts to combine, e.g. `1, 2, 3` or `1-300`.

3. You'll end up with one compressed audio file ready to play.

## Customization

changing this will change the speed on the LATIN ONLY:

 ```bash
   audio_la = change_speed(audio_la, speed=0.95)
   ```

Changing these will change the pause interval after each latin and english word, both times are in milliseconds

 ```bash
    pause_latin_to_eng = AudioSegment.silent(duration=600) 
    pause_between_words = AudioSegment.silent(duration=750)
    ```
