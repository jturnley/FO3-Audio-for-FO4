# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
