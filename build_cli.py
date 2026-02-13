#!/usr/bin/env python3
"""
Command-line interface for FO3 Audio Builder.
Run this script directly for CLI-only operation without GUI.

Examples:
    # Build from FO3 Data folder (auto-detects BSA files)
    python build_cli.py --fo3-data "C:/Games/Fallout 3/Data"
    
    # Build with specific output location
    python build_cli.py --fo3-data "C:/Games/Fallout 3/Data" --output "C:/FO4/Data"
    
    # Build with Archive2.exe (recommended)
    python build_cli.py --fo3-data "C:/Games/Fallout 3/Data" --archive2 "path/to/Archive2.exe"
    
    # Build with compression (not recommended for audio)
    python build_cli.py --fo3-data "C:/Games/Fallout 3/Data" --compress
    
    # Verbose output for debugging
    python build_cli.py --fo3-data "C:/Games/Fallout 3/Data" -v
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from main import main

if __name__ == "__main__":
    # Force CLI mode (no GUI)
    if "--gui" in sys.argv:
        sys.argv.remove("--gui")
        print("Note: build_cli.py is for command-line use. For GUI, run: python -m src.main --gui")
        print()
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBuild cancelled by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
