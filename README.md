# Fallout 3 Audio Repository Builder for Fallout 4

A Python tool to extract Fallout 3 audio and music from BSA archives and build a ready-to-use Fallout 4 mod with BA2 archive and ESM/ESL plugin.

## Features

- **GUI Interface**: User-friendly PyQt6 graphical interface
- **BSA Extraction**: Extract audio files from Fallout 3 BSA archives
- **FUZ Processing**: Handle FUZ files containing audio and lip sync data
- **Music Support**: Extract and include Fallout 3 music files
- **BA2 Building**: Create Fallout 4 BA2 archives using Archive2.exe
- **ESM/ESL Generation**: Generate plugin files with ESL flag for light plugin support
- **Ready-to-Install Output**: Creates a complete mod folder structure

## Requirements

- Python 3.10 or higher
- **Fallout 3 Game of the Year Edition** (includes all DLC audio)
- **Archive2.exe** (from Fallout 4 Creation Kit - **required** for BA2 creation)

### Why Fallout 3 GOTY?

The Game of the Year Edition includes audio from all five DLCs:
- Operation: Anchorage
- The Pitt
- Broken Steel
- Point Lookout
- Mothership Zeta

### Windows 10/11 Note

Fallout 3 does not run natively on Windows 10 or 11, so it cannot create the registry keys needed for automatic path detection. You will need to **manually specify the path** to your Fallout 3 installation (where `Fallout3.exe` is located).

### Installing Archive2.exe

Archive2.exe comes with the **Fallout 4 Creation Kit**, available free on Steam:

1. Open Steam
2. Install "Fallout 4 Creation Kit" (App ID: 1946160)
3. Archive2.exe will be at: `Fallout 4/Tools/Archive2/Archive2.exe`

## Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd FO3-Audio-for-FO4
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/macOS
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### GUI Mode (Recommended)

```bash
python src/main.py --gui
```

Or run the GUI directly:
```bash
python src/gui.py
```

The GUI will:
- Auto-detect Fallout 3 and Archive2.exe paths
- Let you browse for input/output directories
- Show progress and log output

### Command Line Mode

#### Quick Start (Auto-detect FO3 files)

```bash
# Point to your Fallout 3 Data folder - auto-detects BSA files and music
python src/main.py --fo3-data "C:/Games/Fallout 3/Data"
```

#### With Archive2.exe (Recommended)

```bash
python src/main.py --fo3-data "C:/Games/Fallout 3/Data" \
                   --archive2 "C:/Games/Fallout 4/Tools/Archive2/Archive2.exe"
```

#### Specify Individual BSA Files

```bash
python src/main.py --sound-bsa "path/to/Fallout - Sound.bsa" \
                   --voices-bsa "path/to/Fallout - Voices.bsa" \
                   --music-dir "path/to/Music"
```

### Command Line Options

#### Mode Options
| Option | Description |
|--------|-------------|
| `--gui` | Launch the graphical user interface |

#### Input Options
| Option | Description |
|--------|-------------|
| `--fo3-data` | Path to Fallout 3 Data folder (auto-detects BSA files) |
| `--sound-bsa` | Path to Fallout 3 Sound BSA |
| `--voices-bsa` | Path to Fallout 3 Voices BSA |
| `--music-dir` | Path to Fallout 3 Music folder |
| `--input-dir` | Path to pre-extracted audio files |

#### Output Options
| Option | Description |
|--------|-------------|
| `--output-dir` | Output directory (default: `output`) |
| `--mod-name` | Name for the generated mod (default: `Fallout3Audio`) |
| `--no-esl` | Don't flag the ESM as ESL (creates full ESM) |
| `--compress` | Compress files in BA2 (NOT recommended for audio) |

#### Tool Options
| Option | Description |
|--------|-------------|
| `--archive2` | Path to Archive2.exe (from FO4 Creation Kit) |
| `--tools-dir` | Directory containing external tools (default: `tools`) |
| `-v, --verbose` | Enable verbose logging |
| `--convert` | Convert audio to xWMA (usually not needed) |

## Project Structure

```
FO3-Audio-for-FO4/
├── src/
│   ├── __init__.py          # Package initialization
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
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Output Structure

After running the tool, you'll find your ready-to-install mod in:

```
output/final/Fallout3Audio/
├── Fallout3Audio.esm        # Plugin file (ESL-flagged by default)
└── Fallout3Audio - Main.ba2 # Audio archive with all sounds/music
```

## Audio Format Notes

### Why No Conversion Is Needed

Fallout 4's BA2 v8 format natively supports Fallout 3's audio formats:
- xWMA audio files work directly
- WAV and MP3 files are compatible
- FUZ file format is the same between games

The tool preserves original audio files without conversion for best compatibility.

### Archive Requirements

**Important**: Audio BA2 archives must be **uncompressed**. The tool automatically:
- Uses `-compression=None` when building with Archive2.exe
- Falls back to uncompressed mode with the built-in BA2 builder

### Directory Structure

Voice files follow Bethesda's standard layout:
```
Sound/Voice/<PluginName>/<VoiceType>/<filename>.xwm
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

## License

This project is provided as-is for modding purposes. Fallout 3 and Fallout 4 are trademarks of Bethesda Softworks.

## Acknowledgments

- Bethesda Softworks for the Fallout series
- The Fallout modding community
