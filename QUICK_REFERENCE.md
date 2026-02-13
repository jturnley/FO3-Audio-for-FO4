# FO3 Audio Builder - Quick Reference

## Launch Methods

| Method | Command | Best For |
|--------|---------|----------|
| **GUI** | `python -m src.main --gui` | Beginners, visual preference |
| **CLI** | `python build_cli.py --fo3-data "path"` | Automation, scripting |
| **Batch** | `build.bat` | Windows one-click |
| **PowerShell** | `.\build.ps1` | Windows automation |

## Common Commands

### GUI Mode
```bash
python -m src.main --gui
```

### CLI Quick Build
```bash
python build_cli.py --fo3-data "C:/Games/Fallout 3/Data"
```

### CLI with Archive2
```bash
python build_cli.py --fo3-data "C:/Games/FO3/Data" \
    --archive2 "C:/FO4/Tools/Archive2/Archive2.exe"
```

### CLI to FO4 Data Folder
```bash
python build_cli.py --fo3-data "C:/Games/FO3/Data" \
    --output "C:/Games/Fallout 4/Data"
```

### Verbose Mode
```bash
python build_cli.py --fo3-data "C:/Games/FO3/Data" -v
```

### Get Help
```bash
python build_cli.py --help
```

## Output Location

Default: `output/final/Fallout3Audio/`

Contains:
- `Fallout3Audio - Main.ba2` (audio archive)
- `Fallout3Audio.esm` (plugin, optional)

## Required Paths

### Fallout 3 Data Folder
- **Windows Steam**: `C:\Program Files (x86)\Steam\steamapps\common\Fallout 3 goty\Data`
- **Must contain**: `Fallout - Sound.bsa`, `Fallout - Voices.bsa`

### Archive2.exe
- **Location**: `<FO4 Install>\Tools\Archive2\Archive2.exe`
- **Install from**: Steam → Fallout 4 Creation Kit
- **Auto-detected**: Yes (if in standard Steam location)

## Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| Python not found | Install Python 3.10+ |
| BSA files not found | Check `--fo3-data` path points to Data folder |
| Archive2 not found | Install FO4 Creation Kit or use `--archive2` |
| Slow performance | Normal for 90k+ files (5-10 minutes) |
| Import errors | Run `pip install -r requirements.txt` |

## File Count

Expected audio files from Fallout 3 GOTY:
- **Sound Effects**: ~35,000 files
- **Voices**: ~50,000 files
- **Music**: ~100 files
- **DLC Audio**: ~10,000 files
- **Total**: ~90,000+ files

## Dependencies

```bash
pip install PyQt6>=6.6.0
pip install miniaudio>=1.61  # Optional, for MP3 conversion
```

## More Information

- **Full CLI Guide**: [CLI_GUIDE.md](CLI_GUIDE.md)
- **Main README**: [README.md](README.md)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
