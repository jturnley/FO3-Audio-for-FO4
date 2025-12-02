"""Test BSA extraction from Fallout 3 GOTY."""

import sys
sys.path.insert(0, 'src')

from pathlib import Path
from bsa_extractor import BSAExtractor

# Fallout 3 GOTY Data path
FO3_DATA = Path(r"D:\SteamLibrary\steamapps\common\Fallout 3 goty\Data")
OUTPUT_DIR = Path("output/test_extract")

def main():
    print("=" * 60)
    print("Testing BSA Extraction from Fallout 3 GOTY")
    print("=" * 60)
    
    # Check FO3 Data exists
    if not FO3_DATA.exists():
        print(f"ERROR: FO3 Data folder not found at: {FO3_DATA}")
        return 1
    
    print(f"FO3 Data folder: {FO3_DATA}")
    
    # List all BSA files
    bsa_files = list(FO3_DATA.glob("*.bsa"))
    print(f"\nFound {len(bsa_files)} BSA files:")
    for bsa in sorted(bsa_files):
        size_mb = bsa.stat().st_size / (1024 * 1024)
        print(f"  - {bsa.name} ({size_mb:.1f} MB)")
    
    # Test extraction of a small sample from the main Sound BSA
    sound_bsa = FO3_DATA / "Fallout - Sound.bsa"
    if not sound_bsa.exists():
        print(f"\nERROR: Sound BSA not found: {sound_bsa}")
        return 1
    
    print(f"\n--- Testing extraction from {sound_bsa.name} ---")
    
    extractor = BSAExtractor()
    
    # First, list contents to verify we can read the BSA structure
    print("Listing BSA contents...")
    try:
        contents = extractor.list_contents(sound_bsa)
        print(f"Found {len(contents)} files in BSA")
        if contents:
            print("Sample files in BSA:")
            for f in contents[:10]:
                print(f"  - {f}")
            if len(contents) > 10:
                print(f"  ... and {len(contents) - 10} more")
    except Exception as e:
        print(f"Error listing contents: {e}")
        import traceback
        traceback.print_exc()
    
    # Extract just a few files for testing (no filter to test basic extraction)
    test_output = OUTPUT_DIR / "sound_test"
    test_output.mkdir(parents=True, exist_ok=True)
    
    try:
        # Extract without filter to test
        result = extractor.extract(sound_bsa, test_output)
        print(f"Extraction completed to: {test_output}")
        
        # Count extracted files
        extracted = list(test_output.rglob("*"))
        files = [f for f in extracted if f.is_file()]
        print(f"Extracted {len(files)} files")
        
        # Show a few sample files
        if files:
            print("\nSample extracted files:")
            for f in files[:10]:
                rel_path = f.relative_to(test_output)
                size_kb = f.stat().st_size / 1024
                print(f"  - {rel_path} ({size_kb:.1f} KB)")
            if len(files) > 10:
                print(f"  ... and {len(files) - 10} more")
        
        print("\n[OK] BSA extraction test PASSED")
        return 0
        
    except Exception as e:
        print(f"\nERROR during extraction: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
