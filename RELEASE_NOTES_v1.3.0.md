# FO3 Audio Builder v1.3.0 Release Notes

## Self-Contained Audio Conversion

This release removes the ffmpeg dependency and makes the application fully standalone. Users no longer need to install any external tools for MP3 conversion.

### What's New

- **No External Dependencies**: MP3 to WAV conversion is now built-in using miniaudio (MIT licensed)
- **Fully Portable**: The executable now works out of the box without any additional software
- **Same Quality**: MP3 files are converted to 16-bit stereo WAV at 44.1kHz for optimal FO4 compatibility

### Technical Details

The previous version (v1.1.0) required ffmpeg to be installed and in PATH for MP3 conversion. This version uses miniaudio, a self-contained C library with Python bindings that handles MP3 decoding natively.

- miniaudio is MIT licensed (same as this project)
- No LGPL dependencies or licensing concerns
- Smaller total footprint than bundling ffmpeg

### Requirements

- **Archive2.exe** from the Fallout 4 Creation Kit (still required for BA2 creation)
- **Python 3.10+** (if running from source)

### Upgrading from v1.1.0

No changes needed! The new version is a drop-in replacement. The only difference is you no longer need ffmpeg installed.

### Known Issues

None at this time.

---

For the full changelog, see [CHANGELOG.md](CHANGELOG.md).
