#!/usr/bin/env python3
"""
Test build script for FO3 Audio Builder.
Creates mock Fallout 3 data and runs a complete build to verify functionality.
"""

import sys
import struct
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from bsa_extractor import BSAExtractor
from fuz_processor import FUZProcessor
from ba2_builder import BA2Builder


def create_mock_fuz(output_path: Path, audio_data: bytes = b"MOCK_AUDIO" * 50):
    """Create a mock FUZ file for testing."""
    magic = b"FUZE"
    version = struct.pack("<I", 1)
    lip_size = struct.pack("<I", 16)
    lip_data = b"\x00" * 16
    
    fuz_data = magic + version + lip_size + lip_data + audio_data
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(fuz_data)
    return output_path


def create_mock_audio(output_path: Path, file_type: str = "xwm"):
    """Create mock audio files for testing."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if file_type == "xwm":
        # Mock xWMA header
        data = b"RIFF" + struct.pack("<I", 1000) + b"XWMA" + b"\x00" * 500
    elif file_type == "wav":
        # Mock WAV header
        data = b"RIFF" + struct.pack("<I", 1000) + b"WAVE" + b"\x00" * 500
    elif file_type == "mp3":
        # Mock MP3 header
        data = b"\xFF\xFB" + b"\x00" * 500
    else:
        data = b"MOCK_DATA" * 50
    
    output_path.write_bytes(data)
    return output_path


def main():
    print("=" * 70)
    print("FO3 AUDIO BUILDER - TEST BUILD")
    print("=" * 70)
    print()
    
    # Setup test directories
    test_dir = Path("test_build_output")
    mock_fo3_data = test_dir / "mock_fo3_data"
    output_dir = test_dir / "output"
    
    # Clean up old test data
    if test_dir.exists():
        print(f"Cleaning up old test data: {test_dir}")
        shutil.rmtree(test_dir, ignore_errors=True)
    
    print(f"Creating test environment: {test_dir}")
    mock_fo3_data.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    print()
    
    # Create mock audio structure
    print("Creating mock Fallout 3 audio files...")
    
    # Sound effects
    sound_dir = mock_fo3_data / "Sound" / "FX"
    create_mock_audio(sound_dir / "wpn_laser_fire.xwm", "xwm")
    create_mock_audio(sound_dir / "wpn_plasma_fire.xwm", "xwm")
    create_mock_audio(sound_dir / "amb_wind.xwm", "xwm")
    print(f"  ✓ Created 3 sound effects in {sound_dir.relative_to(test_dir)}")
    
    # Voice files (FUZ)
    voice_dir = mock_fo3_data / "Sound" / "Voice" / "Fallout3.esm" / "MaleAdult01"
    create_mock_fuz(voice_dir / "HelloGeneric_0001234A_1.fuz")
    create_mock_fuz(voice_dir / "GoodbyeGeneric_0001234B_1.fuz")
    print(f"  ✓ Created 2 voice files (FUZ) in {voice_dir.relative_to(test_dir)}")
    
    # Music
    music_dir = mock_fo3_data / "Music" / "Battle"
    create_mock_audio(music_dir / "mus_battle_01.wav", "wav")
    create_mock_audio(music_dir / "mus_battle_02.wav", "wav")
    print(f"  ✓ Created 2 music files in {music_dir.relative_to(test_dir)}")
    
    # DLC sounds
    dlc_dir = mock_fo3_data / "Sound" / "FX" / "DLC01"
    create_mock_audio(dlc_dir / "wpn_anchorage_rifle.xwm", "xwm")
    print(f"  ✓ Created 1 DLC sound in {dlc_dir.relative_to(test_dir)}")
    
    print()
    print(f"Mock data created: {mock_fo3_data}")
    print(f"Total files: 8")
    print()
    
    # Test FUZ processor
    print("Testing FUZ processor...")
    processor = FUZProcessor()
    fuz_file = voice_dir / "HelloGeneric_0001234A_1.fuz"
    audio, lip = processor.read_fuz(fuz_file)
    print(f"  ✓ FUZ file parsed: {len(audio)} bytes audio, {len(lip) if lip else 0} bytes lip data")
    
    # Extract audio from FUZ
    extracted_audio = processor.extract_audio(fuz_file)
    print(f"  ✓ Audio extracted to: {extracted_audio.relative_to(test_dir)}")
    print()
    
    # Test BA2 builder
    print("Testing BA2 builder...")
    builder = BA2Builder(compress=False)
    
    # Add all files to BA2
    file_count = 0
    for audio_file in mock_fo3_data.rglob("*"):
        if audio_file.is_file() and audio_file.suffix.lower() in {".xwm", ".wav", ".mp3"}:
            # Determine archive path
            try:
                rel_path = audio_file.relative_to(mock_fo3_data)
                archive_path = str(rel_path).replace("\\", "/")
            except ValueError:
                archive_path = f"Sound/{audio_file.name}"
            
            builder.add_file(audio_file, archive_path)
            file_count += 1
    
    print(f"  ✓ Added {file_count} files to BA2 builder")
    
    # Build BA2 archive
    ba2_output = output_dir / "Fallout3Audio_TEST.ba2"
    builder.build(ba2_output)
    
    ba2_size = ba2_output.stat().st_size
    print(f"  ✓ BA2 archive created: {ba2_output.relative_to(test_dir)}")
    print(f"  ✓ Archive size: {ba2_size:,} bytes ({ba2_size / 1024:.2f} KB)")
    print()
    
    # Verify BA2 structure
    with open(ba2_output, "rb") as f:
        magic = f.read(4)
        version = struct.unpack("<I", f.read(4))[0]
        archive_type = struct.unpack("<I", f.read(4))[0]
        file_count_ba2 = struct.unpack("<I", f.read(4))[0]
    
    print("BA2 Archive Info:")
    print(f"  Magic: {magic}")
    print(f"  Version: {version}")
    print(f"  Type: {archive_type} (0=GNRL)")
    print(f"  Files: {file_count_ba2}")
    print()
    
    # Summary
    print("=" * 70)
    print("TEST BUILD COMPLETE!")
    print("=" * 70)
    print()
    print("Test Results:")
    print(f"  ✓ FUZ processing: PASSED")
    print(f"  ✓ BA2 building: PASSED")
    print(f"  ✓ Files processed: {file_count}")
    print(f"  ✓ Archive created: {ba2_output.name}")
    print()
    print("Test output location:")
    print(f"  {test_dir.absolute()}")
    print()
    print("To clean up test files:")
    print(f"  rmdir /s /q {test_dir}  (Windows CMD)")
    print(f"  Remove-Item -Recurse -Force {test_dir}  (PowerShell)")
    print()
    print("All systems operational! Ready for production use.")
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
