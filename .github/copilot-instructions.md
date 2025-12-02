# Fallout 3 Audio Repository Builder for Fallout 4

## Project Overview
This Python tool extracts Fallout 3 GOTY Edition audio and music from BSA archives and builds a complete Fallout 4 mod with BA2 archive and ESM/ESL plugin.

**Note**: Fallout 3 does not run on Windows 10/11, so automatic path detection is not possible. Users must manually specify the Fallout 3 installation path.

## Tech Stack
- **Language**: Python 3.10+
- **GUI Framework**: PyQt6
- **BSA Handling**: Custom BSA extraction utilities
- **BA2 Building**: Archive2.exe (from FO4 Creation Kit) - required
- **Plugin Generation**: ESM/ESL plugin creation for Fallout 4
- **Audio Processing**: pydub, soundfile (optional, for conversion)

## Project Structure
```
├── src/
│   ├── __init__.py
│   ├── main.py              # Entry point (CLI and GUI launcher)
│   ├── gui.py               # PyQt6 graphical interface
│   ├── bsa_extractor.py     # FO3 BSA archive extraction
│   ├── audio_converter.py   # Audio format conversion (optional)
│   ├── fuz_processor.py     # FUZ file processing (lip sync)
│   ├── ba2_builder.py       # FO4 BA2 archive creation + Archive2 wrapper
│   ├── plugin_generator.py  # ESM/ESL plugin generation
│   └── repository_builder.py # File organization utilities
├── tools/                   # External tools (optional)
├── output/                  # Generated mod files
├── requirements.txt
└── README.md
```

## Archive Format Notes
- **Fallout 3 BSA**: Version 104, contains xWMA audio and FUZ files
- **Fallout 4 BA2**: BTDX format with GNRL type for audio, **MUST be uncompressed** for audio
- **FUZ Files**: Container with lip sync data + xWMA audio
- **ESM/ESL**: Plugin with SNDR (sound descriptor) and MUSC (music) records
- **Audio Conversion**: NOT needed - FO4 BA2 supports FO3 audio formats natively

## Key Commands
- Launch GUI: `python src/main.py --gui`
- CLI with FO3 Data folder: `python src/main.py --fo3-data "path/to/fo3/Data"`
- CLI with Archive2: `python src/main.py --fo3-data "path" --archive2 "path/to/Archive2.exe"`
- Install dependencies: `pip install -r requirements.txt`

## Output Structure
```
output/final/Fallout3Audio/
├── Fallout3Audio.esm        # Plugin file (ESL-flagged)
└── Fallout3Audio - Main.ba2 # Audio archive (uncompressed)
```

## Development Guidelines
- Use type hints for all function parameters and return values
- Handle file paths with pathlib.Path for cross-platform compatibility
- Log all operations for debugging
- Use struct module for binary file format handling
- Audio BA2 archives MUST be uncompressed (-compression=None)
- Prefer Archive2.exe for BA2 creation (more reliable than custom implementation)
- Follow PyQt6 patterns from CC Packer for GUI consistency
