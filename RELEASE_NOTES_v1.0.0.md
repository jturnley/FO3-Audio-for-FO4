# FO3 Audio for FO4 v1.0.0 Release Notes

**Release Date:** December 1, 2025

## Overview

Initial release of the Fallout 3 Audio Repository Builder for Fallout 4. This tool extracts all audio content from Fallout 3 Game of the Year Edition and packages it as a ready-to-install Fallout 4 mod.

## Features

### GUI Application
- User-friendly PyQt6 interface
- Browse buttons for all path inputs
- Auto-detection of Fallout 4 and Archive2.exe
- Real-time progress logging
- Validation of Fallout 3 GOTY Edition (checks for DLC BSAs)

### Audio Extraction
- **Main Game BSAs:**
  - Fallout - Sound.bsa (sound effects)
  - Fallout - Voices.bsa (NPC dialogue)
  - Fallout - MenuVoices.bsa (menu/radio voices)
- **DLC BSAs (all 5 included):**
  - Anchorage - Sounds.bsa
  - ThePitt - Sounds.bsa
  - BrokenSteel - Sounds.bsa
  - PointLookout - Sounds.bsa
  - Zeta - Sounds.bsa
- **Music folder:** All loose music files

### Mod Generation
- **BA2 Archive:** Uncompressed General archive (required for audio)
- **ESM Plugin:** ESL-flagged for light plugin support
- **SNDR Records:** Sound descriptor records for all audio files

## Requirements

- **Fallout 3 Game of the Year Edition** - Source of audio files
- **Fallout 4 Creation Kit** - Provides Archive2.exe for BA2 creation
- **Windows 10/11** - Note: FO3 path must be set manually (FO3 doesn't run on Win10/11)

## Installation

### From Executable
1. Download `FO3AudioBuilder.exe` from the release
2. Double-click to run
3. Set your Fallout 3 Data folder path
4. Set output directory
5. Click "Build Mod"

### From Source
```bash
git clone https://github.com/jturnley/FO3-Audio-for-FO4.git
cd FO3-Audio-for-FO4
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python src/main.py --gui
```

## Output

The tool creates a ready-to-install mod at:
```
<output>/final/Fallout3Audio/
├── Fallout3Audio.esm        # ESL-flagged plugin
└── Fallout3Audio - Main.ba2 # Audio archive (~2.3 GB)
```

## Installing the Generated Mod

1. Copy the `Fallout3Audio` folder to your `Fallout 4/Data/` directory
2. Enable `Fallout3Audio.esm` in your mod manager or add to `plugins.txt`

## Technical Notes

- **No audio conversion:** FO4's BA2 v8 format natively supports FO3 audio formats
- **Uncompressed archive:** Audio must be uncompressed in BA2 archives
- **ESL flag:** Plugin uses minimal load order slot
- **~48,500 audio files:** Includes all voices, sound effects, and music

## Known Limitations

- Fallout 3 path cannot be auto-detected on Windows 10/11
- Archive2.exe is required (no fallback for large archives)
- Build process takes 10-15 minutes due to archive size

## File Checksums

```
FO3AudioBuilder.exe: [SHA256 to be added after build]
```

## Changelog

### v1.0.0 (2025-12-01)
- Initial release
- Full BSA extraction support
- All 5 DLC audio archives included
- PyQt6 GUI
- Archive2.exe integration
- ESM/ESL plugin generation
