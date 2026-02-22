# CLAUDE.md — online-course

## Project Overview

Single-page HTML course site for **{{COURSE_TITLE_ZH-TW}}** (**{{COURSE_TITLE_EN-US}}**)
Deployed via GitHub Pages.

- **Live site:** https://cyng93.github.io/online-course/{{TITLE_EN-US}}
- **Course References** :
  0. `{{COURSE_TITLE_ZH-TW}}` - `{{COURSE_TITLE_EN-US}}`
      - Language: {{AUDIO_LANGUAGE}} audio, with embeded {{SUBTITLE_LANGUAGE}}
      - CoursePlatform (private) : [({{platform}}) {{course_name}}]({{URL}})
      - YouTube backup (unlisted):
        {{YOUTUBE_PLAYLIST}}
        {{YOUTUBE_STUDIO > Playlist videos TAB}}
  1. `科學的大腦鍛鍊法` - `scientific-brain-training-method`:
    - Language: Japanese audio, with embeded zh_tw subtitle
    - CoursePlatform (private) : [(PressPlay) 科學的大腦鍛鍊法｜記憶力冠軍 x 全腦開發技術](https://www.pressplay.cc/member/learning/projects/F4FF13466BE093F6D837D6CC232D4270)
    - YouTube backup (unlisted):
      https://www.youtube.com/playlist?list=PLKInOIgV1wdJCO2OC14czXZlveaPXijL6
      https://studio.youtube.com/playlist/PLKInOIgV1wdJCO2OC14czXZlveaPXijL6/videos (need switch user to cyng93.free@gmail.com)
  2. `打造第二大腦` - `building-a-second-brain`:
    - Language: English audio, with embeded zh_tw subtitle
    - CoursePlatform (private) : [({{platform}}) {{course_name}}]({{URL}})
    - YouTube backup (unlisted):
      https://www.youtube.com/playlist?list=PLKInOIgV1wdJsB1GDcWyFr01T4HGq3d8Y
      https://studio.youtube.com/playlist/PLKInOIgV1wdJsB1GDcWyFr01T4HGq3d8Y/videos (need switch user to cyng93.free@gmail.com)
  3. `停止內耗` - `break-inner-conflict-loop`:
    - Language: Chinese audio, with embeded zh_tw subtitle
    - CoursePlatform (private) : [({{platform}}) {{course_name}}]({{URL}})
    - YouTube backup (unlisted):
      https://www.youtube.com/playlist?list=PLKInOIgV1wdJSa1C-eKlnSGiVQzaK72ko
      https://studio.youtube.com/playlist/PLKInOIgV1wdJSa1C-eKlnSGiVQzaK72ko/videos (need switch user to cyng93.free@gmail.com)
  4. `打造一站式人生控制中心｜Notion Command Center` - `notion-command-center`:
    - Language: English audio, with embeded zh_tw subtitle
    - CoursePlatform (private) : [(PressPlay) 打造一站式人生控制中心｜Notion Command Center](https://www.pressplay.cc/member/learning/projects/5B5E0EDA44028281210B4E7F6C99BF95/articles)
    - YouTube backup (unlisted):
      https://www.youtube.com/playlist?list=PLKInOIgV1wdKkQ5Aw8UhCcsFybJMJ71EL (need switch user to cyng93.free@gmail.com)
      https://studio.youtube.com/playlist/PLKInOIgV1wdKkQ5Aw8UhCcsFybJMJ71EL/videos ()

  n. N/A (e.g., Mastering Claude Code)
    - Language:
    - CoursePlatform (private) : [({{platform}}) {{course_name}}]({{url}})
    - YouTube backup (unlisted):
      .
      .


## Directory Layout
The `online-course` directory consists of 1 or more online course,
with each courses as a sub-directory:
```sh
online-course
├── a-dummy-course-template/
├── scientific-brain-training-method/
├── break-inner-conflict-loop/
├── building-a-second-brain/
└── notion-command-center/
```

while the directory layout of each courses looks like:
```sh - old
building-a-second-brain/
├── .nojekyll                          # Bypass Jekyll processing for GitHub Pages
├── .gitignore                         # Ignores src/inputs/ and src/subtitle_frames_for_ocr/
├── CLAUDE.md                          # This file
├── index.html                         # Symlink → 打造第二大腦，資訊超載時代的高效能知識管理術_transcript.html
├── 打造第二大腦，資訊超載時代的高效能知識管理術_transcript.html     # Main HTML (single-file, self-contained)
└── src/
    ├── inputs/                        # (gitignored) Course MP4 files from PressPlay
    ├── tools/
    │   ├── extract_all.sh             # STEP 1: ffmpeg frame extraction + grid composites
    │   ├── make_grids.sh              # Helper: create 10-frame grid composites
    │   ├── parse_srt.py               # STEP 3: SRT → JSON
    │   └── generate_pages.py          # STEP 4: JSON → HTML
    ├── subtitle_frames_for_ocr/       # (gitignored) ~??K intermediate frame images
    ├── subtitles/
    │   └── *_en-us_visual.srt         # 28 files — curated OCR output (primary source)
    └── transcripts.json               # ??K — structured JSON of all 28 lesson transcripts
```

```sh - new
building-a-second-brain/
├── .nojekyll                          # Bypass Jekyll processing for GitHub Pages
├── .gitignore                         # Ignores src/inputs/ and src/subtitle_frames_for_ocr/
├── CLAUDE.md                          # This file
├── index.html                         # Symlink → building-a-second-brain.html
├── building-a-second-brain.html       # Main HTML (single-file, self-contained)
└── src/
    ├── inputs-and-output/             # (gitignored) Course MP4 files from PressPlay
    │   ├── step0-input
    │   ├── step0-output
    │   ├── step1-input
    │   ├── step1-output
    │   ├── step2-input                # Symlink -> step1-output
    │   ├── step2-output
    │   ├── step3-input                # Symlink -> step2-output
    │   ├── step3-output
    │   ├── step4-input                # Symlink -> step3-output
    │   ├── step4-output
    │   ├── stepN-input                # Symlink -> stepN-1-output
    │   └── stepN-output
    ├── tools/
    │   ├── extract_all.sh             # STEP 1: ffmpeg frame extraction + grid composites
    │   ├── make_grids.sh              # Helper: create 10-frame plain grid composites
    │   ├── make_annotated_grids.py    # STEP 2a: create grids + sidecar TSV
    │   ├── validate_srt.py            # Optional QA: validate SRT timestamp issues
    │   ├── fix_srt_end_times.py       # STEP 2c: set end_time = next block's start_time
    │   ├── parse_srt.py               # STEP 3: SRT → JSON
    │   └── generate_pages.py          # STEP 4: JSON → HTML
    ├── subtitle_frames_for_ocr/       # (gitignored) ~??K intermediate frame images
    ├── subtitles/
    │   └── *_en-us_visual.srt         # 28 files — curated OCR output (primary source)
    └── transcripts.json               # ??K — structured JSON of all 28 lesson transcripts
```

## Build Pipeline

```
Prerequisites:
  - Course's MP4 video files or YouTube URL
  - brew install ffmpeg tesseract
  - brew install yt-dlp (optional, for downloading YouTube auto-generated subtitles)
  - pip3 install Pillow (required by make_annotated_grids.py)

┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 0 (optional, one-time, independent)                                    │
│                                                                             │
│   yt-dlp --write-auto-sub --sub-lang [ja|en] ...                            │
│     └─► step0-output/subtitles/*_jp_youtube_autogen.srt (reference)         │
│                           or                                                │
│     └─► step0-output/subtitles/*_en_youtube_autogen.srt (reference)         │
│                                                                             │
│   Only needed if you want Japanese,English auto-generated subs              │
│   from YouTube as reference. Not part of the main pipeline.                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: Extract subtitle frames                                             │
│                                                                             │
│   src/tools/extract_all.sh                                                  │
│     Input:  step1-input/{chapter}-{name}*.mp4 (1+ course videos)            │
│     Output: step1-output/subtitle_frames_for_ocr/                           │
│             ├── {id}_{ssss}.jpg  (per-second frames)                        │
│             └── {id}_grid_{nn}.jpg (10-frame composites, plain)             │
│                                                                             │
│   Calls: src/tools/make_grids.sh (for plain grid composites)                │
│                                                                             │
│   ⚠ Frame-to-timestamp mapping (critical):                                  │
│     ffmpeg fps=1 outputs _0001.jpg at pts_time=0.                           │
│     Frame _NNNN.jpg = second (NNNN - 1) of the MP4.                         │
│     Plain grids do NOT show this mapping — use annotated grids instead.     │
└─────────────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: OCR → SRT (via Claude/Cydia, 3 sub-steps)                          │
│                                                                             │
│   2a. Generate annotated grids + sidecar TSV:                               │
│       python3 src/tools/make_annotated_grids.py \                           │
│         step1-output/subtitle_frames_for_ocr {video_id} \                   │
│         --output-dir <output_dir>                                           │
│       → {id}_annotated_grid_{nn}.jpg (visual reference for OCR)            │
│       → {id}_timestamps.tsv (frame→timestamp mapping, authoritative)       │
│                                                                             │
│   2b. OCR grid images using TSV timestamps → SRT:                          │
│                                                                             │
│       Overview: Read TSV for timestamps, read grid images for subtitle     │
│       TEXT only. Never read timestamps from images — use TSV exclusively.  │
│                                                                             │
│       Procedure:                                                            │
│       1. Read {id}_timestamps.tsv — this maps each grid row to its         │
│          exact SRT timestamp. Columns: grid_file, row, frame, second,      │
│          srt_timestamp. Example: "1-1_annotated_grid_01.jpg  1  _0001      │
│          0  00:00:00"                                                       │
│       2. Process grid images in order (grid_01, grid_02, ...):             │
│          - Each grid has 10 rows (last grid may have fewer)                │
│          - Each row = 1 second of video = 1 frame                          │
│          - OCR the subtitle text from each row (Chinese zh-TW text         │
│            typically at bottom of frame)                                    │
│          - Map row N in grid_XX to TSV entry: grid_file=grid_XX, row=N    │
│       3. Merge consecutive rows with IDENTICAL subtitle text:              │
│          - start_time = srt_timestamp of FIRST row with this text          │
│            (format: HH:MM:SS → HH:MM:SS,000)                              │
│          - end_time = srt_timestamp of LAST row with this text             │
│            (format: HH:MM:SS → HH:MM:SS,000)                              │
│          - If only 1 row has this text, start=end (fix_srt_end_times.py    │
│            will correct end times in step 2c)                              │
│       4. Number SRT blocks sequentially starting from 1                    │
│       5. Write output to step2-output/subtitles/{id}_{title}_zh-TW_       │
│          visual.srt                                                         │
│                                                                             │
│       Batching: Process 5-10 grids at a time to stay within context.       │
│       Accumulate SRT blocks across batches. Verify block continuity        │
│       between batches (last text of prev batch ≠ first text of next).     │
│                                                                             │
│       Rows with NO visible subtitle text → skip (no SRT block).           │
│       Rows where text is partially visible or unclear → best-effort OCR   │
│       with surrounding context for inference.                               │
│                                                                             │
│   2c. Fix SRT end times (seamless subtitles):                               │
│       python3 src/tools/fix_srt_end_times.py <srt_file>                     │
│       - Sets each block's end_time = next block's start_time               │
│       - Eliminates gaps between consecutive subtitle blocks                 │
│                                                                             │
│   2d. QA: Import SRT into YouTube (unlisted upload of same MP4)             │
│       - Verify text accuracy against embedded video subtitles               │
│       - Verify timing alignment (SRT subtitle should match speech)          │
│                                                                             │
│   Optional: validate_srt.py can be used to check for SRT issues:            │
│       python3 src/tools/validate_srt.py <srt_file>       (report only)     │
│       python3 src/tools/validate_srt.py <srt_file> --fix (auto-fix)        │
└─────────────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 3: SRT → JSON                                                          │
│                                                                             │
│   python3 src/tools/parse_srt.py                                            │
│     Input:  step3-input/subtitles/*_zh-TW_visual.srt (1+ files)             │
│     Output: step3-output/transcripts.json                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 4: JSON → HTML                                                         │
│                                                                             │
│   python3 src/tools/generate_pages.py                                       │
│     Input:  step4-input/transcripts.json                                    │
│     Output: step4-output/{{COURSE_TITLE_EN-US}}.html (repo root)            │
│             (index.html symlinks to this)                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 5: Deploy                                                              │
│                                                                             │
│   git push → GitHub Pages auto-deploys from {{COURSE_TITLE_EN-US}} branch   │
│     Live at: https://cyng93.github.io/online-courses/{{COURSE_TITLE_EN-US}} │
└─────────────────────────────────────────────────────────────────────────────┘
```

## HTML Features

1. Full 1+-lesson transcript with YouTube click-to-load embedding
2. Real-time search across all transcripts with highlight
3. Dark mode toggle
4. Font size controls (A-/A+) with presets (XS/S/M/L/XL)
5. Eye-care mode (eye-friendly-background + larger text, with proper state revert)
6. Expand all / Collapse all transcript sections
7. Scrollable transcript while video plays (auto-expand + 60vh scroll)
8. Floating TOC sidebar with chapter grouping + IntersectionObserver active tracking

## Subtitle File Naming Convention

- `{id}_{title}_en-us_visual.srt` — OCR-extracted zh-TW subtitles (primary, curated)

Where `{id}` is the lesson number (e.g., `1-1`, `7-3`) and `{title}` is the
canonical lesson title from the course curriculum.

## GitHub Pages

- Deployed from `main` branch
- `.nojekyll` file present to bypass Jekyll processing
- `index.html` is a symlink to `{{COURSE_TITLE_EN-US}}_transcript.html`
