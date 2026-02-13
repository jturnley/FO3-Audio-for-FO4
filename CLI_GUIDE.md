# FO3 Audio Builder - CLI Guide

## Quick Start (Command Line)

### Basic Usage

```bash
# Launch GUI (easiest option)
python -m src.main --gui

# Build from Fallout 3 Data folder (CLI)
python build_cli.py --fo3-data "C:/Games/Fallout 3 GOTY/Data"

# Build with custom output directory
python build_cli.py --fo3-data "C:/Games/Fallout 3/Data" --output "C:/FO4/Data"
```

### With Archive2.exe (Recommended)

For best compatibility, use Archive2.exe from the Fallout 4 Creation Kit:

```bash
python build_cli.py --fo3-data "C:/Games/Fallout 3/Data" \
    --archive2 "C:/Program Files (x86)/Steam/steamapps/common/Fallout 4/Tools/Archive2/Archive2.exe"
```

The tool will auto-detect Archive2.exe if it's in standard Steam locations.

## Command Line Options

### Input Options

| Option | Description | Example |
|--------|-------------|---------|
| `--fo3-data PATH` | Path to Fallout 3 Data folder (auto-detects BSAs) | `--fo3-data "C:/Games/FO3/Data"` |
| `--sound-bsa PATH` | Specific sound BSA file | `--sound-bsa "Fallout - Sound.bsa"` |
| `--voices-bsa PATH` | Specific voices BSA file | `--voices-bsa "Fallout - Voices.bsa"` |
| `--music-dir PATH` | Music folder (loose files) | `--music-dir "C:/Games/FO3/Data/Music"` |
| `--input-dir PATH` | Pre-extracted audio files | `--input-dir "extracted_audio"` |

### Output Options

| Option | Description | Default |
|--------|-------------|---------|
| `--output-dir PATH` | Output directory for all files | `output` |
| `--compress` | Compress BA2 archive (NOT recommended for audio) | Disabled |

### Tool Options

| Option | Description |
|--------|-------------|
| `--archive2 PATH` | Path to Archive2.exe (FO4 Creation Kit) |
| `--tools-dir PATH` | Directory with external tools |
| `-v, --verbose` | Enable verbose/debug logging |
| `--convert` | Force audio conversion to xWMA (usually not needed) |

### GUI Option

| Option | Description |
|--------|-------------|
| `--gui` | Launch graphical user interface |

## Usage Examples

### Example 1: Simple Build

Extract from Fallout 3 and build BA2 archive:

```bash
python build_cli.py --fo3-data "C:/Program Files (x86)/Steam/steamapps/common/Fallout 3 goty/Data"
```

Output will be in: `output/final/Fallout3Audio/`

### Example 2: Custom Output Location

Build directly into Fallout 4's Data folder:

```bash
python build_cli.py \
    --fo3-data "C:/Games/Fallout 3/Data" \
    --output "C:/Program Files (x86)/Steam/steamapps/common/Fallout 4/Data"
```

### Example 3: With Archive2.exe

For maximum compatibility with Fallout 4:

```bash
python build_cli.py \
    --fo3-data "C:/Games/Fallout 3/Data" \
    --archive2 "C:/Steam/steamapps/common/Fallout 4/Tools/Archive2/Archive2.exe"
```

### Example 4: Verbose Mode

Get detailed progress information:

```bash
python build_cli.py --fo3-data "C:/Games/Fallout 3/Data" --verbose
```

### Example 5: Specific BSA Files

Extract from specific BSA files:

```bash
python build_cli.py \
    --sound-bsa "C:/Games/FO3/Data/Fallout - Sound.bsa" \
    --voices-bsa "C:/Games/FO3/Data/Fallout - Voices.bsa" \
    --music-dir "C:/Games/FO3/Data/Music"
```

### Example 6: Pre-Extracted Files

If you already extracted BSA files manually:

```bash
python build_cli.py --input-dir "my_extracted_audio" --output "output"
```

## Output Structure

The tool creates this structure:

```
output/
├── extracted/          # Temporary: extracted BSA files
├── converted/          # Temporary: processed audio
└── final/
    └── Fallout3Audio/
        ├── Fallout3Audio.esm          # Plugin file (optional)
        └── Fallout3Audio - Main.ba2   # Audio archive ⭐
```

The **Fallout3Audio** folder is your final mod output.

## Tips & Best Practices

### ✅ DO:
- Use `--fo3-data` for automatic BSA detection
- Use `--archive2` for best BA2 compatibility
- Leave audio uncompressed (default) for FO4 compatibility
- Use verbose mode (`-v`) when troubleshooting

### ❌ DON'T:
- Don't use `--compress` for audio BA2 archives (breaks in-game audio)
- Don't convert audio unless necessary (FO4 supports FO3 formats)

## Troubleshooting

### "No Fallout 3 BSA files found"

Make sure you're pointing to the correct Data folder:
```bash
# CORRECT
--fo3-data "C:/Games/Fallout 3 GOTY/Data"

# WRONG
--fo3-data "C:/Games/Fallout 3 GOTY"
```

### "Archive2.exe not found"

Install the Fallout 4 Creation Kit from Steam (App ID: 1946160), or specify the path manually:
```bash
--archive2 "path/to/Archive2.exe"
```

### Slow performance

Archive2.exe can take 5-10 minutes for 90,000+ audio files. This is normal.

### Python not found

Make sure Python 3.10+ is installed and in your PATH:
```bash
python --version  # Should show 3.10 or higher
```

## Advanced Usage

### Running as Python Module

You can also run the main module directly:

```bash
# CLI mode
python -m src.main --fo3-data "C:/Games/FO3/Data"

# GUI mode
python -m src.main --gui
```

### Getting Help

```bash
# Show all options
python build_cli.py --help

# Show version
python build_cli.py --version  # (if implemented)
```

## Scripting & Automation

### Batch Script Example (Windows)

```batch
@echo off
set FO3_DATA=C:\Games\Fallout 3 GOTY\Data
set OUTPUT=C:\Games\Fallout 4\Data
set ARCHIVE2=C:\Steam\steamapps\common\Fallout 4\Tools\Archive2\Archive2.exe

python build_cli.py ^
    --fo3-data "%FO3_DATA%" ^
    --output "%OUTPUT%" ^
    --archive2 "%ARCHIVE2%" ^
    --verbose

pause
```

### PowerShell Example

```powershell
$fo3Data = "C:\Games\Fallout 3 GOTY\Data"
$output = "C:\Games\Fallout 4\Data"
$archive2 = "C:\Steam\steamapps\common\Fallout 4\Tools\Archive2\Archive2.exe"

python build_cli.py `
    --fo3-data $fo3Data `
    --output $output `
    --archive2 $archive2 `
    --verbose
```

## Need GUI Instead?

For a user-friendly graphical interface:

```bash
python -m src.main --gui
```

Or double-click `FO3AudioBuilder.exe` if using the compiled version.

---

**For more information, see README.md**
