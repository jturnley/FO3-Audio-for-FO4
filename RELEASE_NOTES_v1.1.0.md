# FO3 Audio for FO4 v1.1.0 Release Notes

**Release Date:** December 2, 2025

## Overview

This release improves the user experience by outputting mod files directly to the Fallout 4 Data folder and adds MP3 to WAV conversion for proper audio support.

## New Features

### Direct FO4 Data Output
- Default output directory is now the Fallout 4 Data folder
- ESM and BA2 files are placed directly where FO4 can use them
- No more manual copying required - just build and play!

### MP3 Conversion
- MP3 files (radio music) are now converted to WAV format
- FO4's BA2 archives don't properly support MP3 playback
- Conversion uses ffmpeg (must be installed and in PATH)

## Changes

- Temp files now stored in system TEMP folder instead of output directory
- Cleaner output with no intermediate folders

## Requirements

- **Fallout 3 Game of the Year Edition** - Source of audio files
- **Fallout 4 Creation Kit** - Provides Archive2.exe
- **ffmpeg** (optional) - Required for MP3 conversion
  - Download from https://ffmpeg.org/download.html
  - Add to system PATH

## Installation

### From Executable
1. Download `FO3AudioBuilder.exe` from the release
2. Double-click to run
3. Set your Fallout 3 Data folder path
4. Output will default to your FO4 Data folder
5. Click "Build FO4 Mod"
6. Enable `Fallout3Audio.esm` in your mod manager

### From Source
```bash
git clone https://github.com/jturnley/FO3-Audio-for-FO4.git
cd FO3-Audio-for-FO4
.\scripts\setup_venv.ps1
.\scripts\run_gui.ps1
```

## Output Files

After building, your Fallout 4 Data folder will contain:
```
Fallout 4/Data/
├── Fallout3Audio.esm        # ESL-flagged plugin
└── Fallout3Audio - Main.ba2 # Audio archive (~2.3 GB)
```

## Changelog

### v1.1.0 (2025-12-02)
- Default output to Fallout 4 Data folder
- MP3 to WAV conversion for music files
- Temp files moved to system TEMP folder

### v1.0.0 (2025-12-01)
- Initial release
- Full BSA extraction support
- All 5 DLC audio archives included
- PyQt6 GUI
- Archive2.exe integration
- ESM/ESL plugin generation
