"""Main entry point for Fallout 3 Audio Repository Builder."""

import argparse
import logging
import sys
from pathlib import Path

# Handle imports for both source and frozen executable
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    from src.bsa_extractor import BSAExtractor
    from src.audio_converter import AudioConverter
    from src.fuz_processor import FUZProcessor
    from src.ba2_builder import BA2Builder, Archive2Builder
else:
    # Running from source
    from bsa_extractor import BSAExtractor
    from audio_converter import AudioConverter
    from fuz_processor import FUZProcessor
    from ba2_builder import BA2Builder, Archive2Builder


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the application."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("audio_builder.log"),
        ],
    )


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Extract Fallout 3 audio/music and build Fallout 4 BA2 archive"
    )
    
    # Mode selection
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch the graphical user interface",
    )
    
    # Input options
    input_group = parser.add_argument_group("Input Options")
    input_group.add_argument(
        "--fo3-data",
        type=Path,
        help="Path to Fallout 3 Data folder (auto-detects BSA files)",
    )
    input_group.add_argument(
        "--sound-bsa",
        type=Path,
        help="Path to Fallout 3 Sound BSA (e.g., 'Fallout - Sound.bsa')",
    )
    input_group.add_argument(
        "--voices-bsa",
        type=Path,
        help="Path to Fallout 3 Voices BSA (e.g., 'Fallout - Voices.bsa')",
    )
    input_group.add_argument(
        "--music-dir",
        type=Path,
        help="Path to Fallout 3 Music folder (loose files)",
    )
    input_group.add_argument(
        "--input-dir",
        type=Path,
        help="Path to pre-extracted audio files directory",
    )
    
    # Output options
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="Output directory for all generated files (default: output)",
    )
    output_group.add_argument(
        "--compress",
        action="store_true",
        help="Compress files in BA2 archive (NOT recommended for audio - FO4 requires uncompressed audio)",
    )
    
    # Tool options
    tool_group = parser.add_argument_group("Tool Options")
    tool_group.add_argument(
        "--tools-dir",
        type=Path,
        default=Path("tools"),
        help="Directory containing external tools (default: tools)",
    )
    tool_group.add_argument(
        "--archive2",
        type=Path,
        help="Path to Archive2.exe (from FO4 Creation Kit) for BA2 creation",
    )
    tool_group.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    tool_group.add_argument(
        "--convert",
        action="store_true",
        help="Convert audio files to xWMA (usually not needed - FO4 BA2 supports FO3 audio formats natively)",
    )
    
    return parser.parse_args()


def find_fo3_bsas(fo3_data: Path) -> dict[str, Path | list[Path]]:
    """Find Fallout 3 BSA files in the Data folder, including DLC audio."""
    bsas: dict[str, Path | list[Path]] = {}
    
    # Main game sound BSA
    sound_names = ["Fallout - Sound.bsa", "Fallout3 - Sound.bsa"]
    for name in sound_names:
        path = fo3_data / name
        if path.exists():
            bsas["sound"] = path
            break
    
    # Main game voices BSA
    voice_names = ["Fallout - Voices.bsa", "Fallout3 - Voices.bsa", "Fallout - Voices1.bsa"]
    for name in voice_names:
        path = fo3_data / name
        if path.exists():
            bsas["voices"] = path
            break
    
    # Menu voices (optional)
    menu_voices = fo3_data / "Fallout - MenuVoices.bsa"
    if menu_voices.exists():
        bsas["menu_voices"] = menu_voices
    
    # DLC sound BSAs - all files matching "* - Sounds.bsa" pattern
    dlc_sounds: list[Path] = []
    dlc_patterns = [
        "Anchorage - Sounds.bsa",
        "ThePitt - Sounds.bsa", 
        "BrokenSteel - Sounds.bsa",
        "PointLookout - Sounds.bsa",
        "Zeta - Sounds.bsa",
    ]
    for pattern in dlc_patterns:
        path = fo3_data / pattern
        if path.exists():
            dlc_sounds.append(path)
    
    if dlc_sounds:
        bsas["dlc_sounds"] = dlc_sounds
    
    # Check for music folder
    music_path = fo3_data / "Music"
    if music_path.exists():
        bsas["music"] = music_path
    
    return bsas


def find_archive2() -> Path | None:
    """Try to find Archive2.exe by first locating Fallout 4.
    
    Archive2.exe is located at: <FO4 Install>/Tools/Archive2/Archive2.exe
    It comes with the Fallout 4 Creation Kit (Steam App ID: 1946160).
    """
    # Common Fallout 4 installation paths
    fo4_paths = [
        r"C:\Program Files (x86)\Steam\steamapps\common\Fallout 4",
        r"C:\Program Files\Steam\steamapps\common\Fallout 4",
        r"D:\SteamLibrary\steamapps\common\Fallout 4",
        r"E:\SteamLibrary\steamapps\common\Fallout 4",
    ]
    
    for fo4_path in fo4_paths:
        if Path(fo4_path).exists():
            archive2 = Path(fo4_path) / "Tools" / "Archive2" / "Archive2.exe"
            if archive2.exists():
                return archive2
    
    return None


def main() -> None:
    """Main entry point."""
    args = parse_args()
    
    # Launch GUI if requested OR if running as frozen exe with no arguments
    # This makes double-clicking the exe launch the GUI
    launch_gui = args.gui
    if getattr(sys, 'frozen', False) and len(sys.argv) == 1:
        launch_gui = True
    
    if launch_gui:
        try:
            if getattr(sys, 'frozen', False):
                from src.gui import main as gui_main
            else:
                from gui import main as gui_main
            gui_main()
            return
        except ImportError as e:
            print(f"Error: PyQt6 is required for GUI mode. Install it with: pip install PyQt6")
            print(f"Details: {e}")
            sys.exit(1)
    
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("Fallout 3 Audio Repository Builder for Fallout 4")
    logger.info("=" * 60)

    # Initialize components
    bsa_extractor = BSAExtractor()
    audio_converter = AudioConverter(tools_dir=args.tools_dir)
    fuz_processor = FUZProcessor()
    ba2_builder = BA2Builder(compress=args.compress)

    # Create output directories
    output_dir = args.output_dir
    extracted_dir = output_dir / "extracted"
    converted_dir = output_dir / "converted"
    final_dir = output_dir / "final" / "Fallout3Audio"
    
    for d in [extracted_dir, converted_dir, final_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # Determine input sources
    bsa_files: dict[str, Path | list[Path]] = {}
    
    if args.fo3_data:
        logger.info(f"Scanning Fallout 3 Data folder: {args.fo3_data}")
        bsa_files = find_fo3_bsas(args.fo3_data)
        if not bsa_files:
            logger.error("No Fallout 3 BSA files found in the specified Data folder")
            return
        logger.info(f"Found BSA files: {list(bsa_files.keys())}")
    
    if args.sound_bsa:
        bsa_files["sound"] = args.sound_bsa
    if args.voices_bsa:
        bsa_files["voices"] = args.voices_bsa
    if args.music_dir:
        bsa_files["music"] = args.music_dir

    # Step 1: Extract BSA files
    all_extracted_files: list[Path] = []
    
    if "sound" in bsa_files:
        logger.info(f"Extracting sound BSA: {bsa_files['sound']}")
        sound_dir = extracted_dir / "sound"
        bsa_extractor.extract(bsa_files["sound"], sound_dir)
        all_extracted_files.extend(sound_dir.rglob("*"))
    
    if "voices" in bsa_files:
        logger.info(f"Extracting voices BSA: {bsa_files['voices']}")
        voices_dir = extracted_dir / "voices"
        bsa_extractor.extract(bsa_files["voices"], voices_dir)
        all_extracted_files.extend(voices_dir.rglob("*"))
    
    if "menu_voices" in bsa_files:
        logger.info(f"Extracting menu voices BSA: {bsa_files['menu_voices']}")
        menu_dir = extracted_dir / "menu_voices"
        bsa_extractor.extract(bsa_files["menu_voices"], menu_dir)
        all_extracted_files.extend(menu_dir.rglob("*"))
    
    # Extract DLC sound BSAs
    if "dlc_sounds" in bsa_files:
        dlc_list = bsa_files["dlc_sounds"]
        if isinstance(dlc_list, list):
            for dlc_bsa in dlc_list:
                dlc_name = dlc_bsa.stem.replace(" - Sounds", "")
                logger.info(f"Extracting DLC sound BSA: {dlc_bsa.name}")
                dlc_dir = extracted_dir / "dlc" / dlc_name
                bsa_extractor.extract(dlc_bsa, dlc_dir)
                all_extracted_files.extend(dlc_dir.rglob("*"))
    
    if "music" in bsa_files:
        music_source = bsa_files["music"]
        logger.info(f"Copying music files from: {music_source}")
        music_dest = extracted_dir / "Music"
        music_dest.mkdir(parents=True, exist_ok=True)
        
        # Copy music files (they're usually loose, not in BSA)
        import shutil
        if music_source.is_dir():
            for music_file in music_source.rglob("*"):
                if music_file.is_file():
                    rel_path = music_file.relative_to(music_source)
                    dest_file = music_dest / rel_path
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(music_file, dest_file)
                    all_extracted_files.append(dest_file)
    
    # Handle pre-extracted input
    if args.input_dir:
        logger.info(f"Using pre-extracted files from: {args.input_dir}")
        all_extracted_files.extend(args.input_dir.rglob("*"))

    if not all_extracted_files:
        logger.error("No input files found. Provide --fo3-data, BSA paths, or --input-dir")
        return

    # Step 2: Process FUZ files (extract audio from FUZ containers)
    logger.info("Processing FUZ files...")
    fuz_files = [f for f in all_extracted_files if f.suffix.lower() == ".fuz"]
    audio_files: list[Path] = []
    
    for fuz_file in fuz_files:
        try:
            audio_path = fuz_processor.extract_audio(
                fuz_file,
                converted_dir / fuz_file.relative_to(extracted_dir).with_suffix(".xwm")
            )
            audio_files.append(audio_path)
        except Exception as e:
            logger.warning(f"Failed to process FUZ: {fuz_file}: {e}")
    
    # Add non-FUZ audio files
    audio_extensions = {".xwm", ".wav", ".mp3", ".ogg"}
    for f in all_extracted_files:
        if f.is_file() and f.suffix.lower() in audio_extensions:
            audio_files.append(f)

    logger.info(f"Found {len(audio_files)} audio files to process")

    # Step 3: Convert audio only if explicitly requested
    if args.convert:
        logger.info("Converting audio files to xWMA format...")
        converted_files = audio_converter.convert_batch(
            audio_files, 
            converted_dir,
            target_format=".xwm"
        )
    else:
        logger.info("Using original audio files (no conversion needed for FO4 BA2)")
        converted_files = audio_files

    # Step 4: Build BA2 archive
    logger.info("Building BA2 archive...")

    ba2_path = final_dir / "Fallout3Audio - Main.ba2"
    
    # Use Archive2.exe if available (recommended)
    archive2_path = args.archive2 or find_archive2()
    
    if archive2_path and archive2_path.exists():
        logger.info(f"Using Archive2.exe: {archive2_path}")
        
        # Prepare files in a staging directory for Archive2
        staging_dir = output_dir / "staging"
        staging_dir.mkdir(parents=True, exist_ok=True)
        
        import shutil
        for audio_file in converted_files:
            # Determine archive path based on file type
            if "music" in str(audio_file).lower():
                archive_path = Path("Music") / audio_file.name
            elif "voice" in str(audio_file).lower():
                try:
                    rel = audio_file.relative_to(converted_dir)
                    archive_path = Path("Sound/Voice") / rel
                except ValueError:
                    archive_path = Path("Sound/Voice") / audio_file.name
            else:
                archive_path = Path("Sound/FX") / audio_file.name
            
            dest_path = staging_dir / archive_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(audio_file, dest_path)
        
        # Build with Archive2
        archive2_builder = Archive2Builder(archive2_path)
        compression = "Default" if args.compress else "None"
        archive2_builder.create_archive(
            staging_dir,
            ba2_path,
            archive_type="General",
            compression=compression,
            progress_callback=lambda msg: logger.info(msg),
        )
        
        # Clean up staging directory
        shutil.rmtree(staging_dir, ignore_errors=True)
    else:
        logger.info("Using built-in BA2 builder (Archive2.exe not found)")
        if not args.compress:
            logger.warning("For best compatibility, use --archive2 to specify Archive2.exe from FO4 Creation Kit")
        
        ba2_builder = BA2Builder(compress=args.compress)
        
        # Add all converted audio files to BA2
        for audio_file in converted_files:
            # Determine archive path based on file type
            if "music" in str(audio_file).lower():
                archive_path = f"Music/{audio_file.name}"
            elif "voice" in str(audio_file).lower():
                try:
                    rel = audio_file.relative_to(converted_dir)
                    archive_path = f"Sound/Voice/{rel}"
                except ValueError:
                    archive_path = f"Sound/Voice/{audio_file.name}"
            else:
                archive_path = f"Sound/FX/{audio_file.name}"
            
            ba2_builder.add_file(audio_file, archive_path)
        
        ba2_builder.build(ba2_path)


    # Summary
    logger.info("=" * 60)
    logger.info("BUILD COMPLETE!")
    logger.info("=" * 60)
    logger.info(f"Output directory: {final_dir}")
    logger.info(f"BA2 Archive: {ba2_path.name}")
    logger.info(f"Total audio files: {len(converted_files)}")
    logger.info("")
    logger.info("This is a modder's resource - integrate the BA2 into your own mods.")
    logger.info(f"Copy '{final_dir.name}' folder to Fallout 4/Data/ for reference.")


if __name__ == "__main__":
    main()
