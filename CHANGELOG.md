# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-12-02

### Changed

- Replaced ffmpeg dependency with miniaudio for MP3 conversion
- MP3 to WAV conversion is now self-contained (no external tools required)
- Application is fully standalone - users don't need to install anything

### Technical Details

- miniaudio (MIT licensed) provides built-in MP3 decoding
- Converted MP3 files use 16-bit stereo PCM WAV format at 44.1kHz
- No external dependencies required for audio conversion

## [1.1.0] - 2025-12-02

### Added

- MP3 to WAV conversion for music files (FO4 BA2 doesn't properly support MP3)
- Uses ffmpeg for audio conversion (must be in PATH)

### Changed

- Default output directory now set to Fallout 4 Data folder
- ESM and BA2 files are placed directly in FO4 Data (no subfolder)
- Temp files moved to system TEMP folder to avoid clutter

### Improved

- Better FO4 integration - mod files ready to use immediately after build

## [1.0.0] - 2025-12-01

### Added

- Initial release of FO3 Audio Repository Builder for Fallout 4
- PyQt6 GUI with user-friendly interface
- BSA v104 extraction for Fallout 3 archives
- Support for all main game BSAs (Sound, Voices, MenuVoices)
- Support for all 5 DLC sound archives (Anchorage, ThePitt, BrokenSteel, PointLookout, Zeta)
- Music folder copying from FO3 Data directory
- BA2 archive creation using Archive2.exe (from FO4 Creation Kit)
- ESM plugin generation with ESL flag for light plugin support
- SNDR (Sound Descriptor) record generation for all audio files
- Auto-detection of Fallout 4 installation and Archive2.exe
- CLI mode for automation and scripting
- Comprehensive logging to `audio_builder.log`

### Technical Details

- Audio BA2 archives are created uncompressed (required for FO4 audio)
- No audio conversion needed - FO4 BA2 v8 supports FO3 audio formats natively
- ESM files are flagged as ESL (Light) for minimal load order impact
- FUZ files (voice + lip sync) are processed and included
