"""
PyQt6 GUI for Fallout 3 Audio Repository Builder.
Provides a user-friendly interface for extracting FO3 audio and building FO4 mods.
"""

import sys
import os
import logging
import webbrowser
import ctypes
from pathlib import Path
from typing import Optional, Callable

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QFileDialog, QMessageBox, QGroupBox,
    QProgressBar, QCheckBox
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt


class ExtractWorker(QThread):
    """Background worker for extracting FO3 audio and building FO4 mod."""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(
        self,
        fo3_data_path: str,
        output_path: str,
        archive2_path: str,
        convert_audio: bool = False
    ):
        super().__init__()
        self.fo3_data_path = fo3_data_path
        self.output_path = output_path
        self.archive2_path = archive2_path
        self.convert_audio = convert_audio

    def run(self):
        try:
            # Handle imports for both source and frozen executable
            if getattr(sys, 'frozen', False):
                from src.bsa_extractor import BSAExtractor
                from src.fuz_processor import FUZProcessor
                from src.repository_builder import RepositoryBuilder
                from src.plugin_generator import PluginGenerator
            else:
                from bsa_extractor import BSAExtractor
                from fuz_processor import FUZProcessor
                from repository_builder import RepositoryBuilder
                from plugin_generator import PluginGenerator

            fo3_data = Path(self.fo3_data_path)
            output_dir = Path(self.output_path)
            
            # Create output directories
            # Use a temp folder outside the output (FO4 Data) folder to avoid clutter
            temp_dir = Path(os.environ.get('TEMP', output_dir.parent)) / "FO3AudioBuilder_temp"
            # Final files go directly to output (which should be FO4 Data folder)
            final_dir = output_dir
            temp_dir.mkdir(parents=True, exist_ok=True)
            final_dir.mkdir(parents=True, exist_ok=True)

            extractor = BSAExtractor()

            # Find and extract main game BSA files
            sound_bsa = fo3_data / "Fallout - Sound.bsa"
            voices_bsa = fo3_data / "Fallout - Voices.bsa"
            menu_voices_bsa = fo3_data / "Fallout - MenuVoices.bsa"
            music_dir = fo3_data / "Music"

            # Extract main sound BSA
            if sound_bsa.exists():
                self.progress.emit(f"Extracting {sound_bsa.name}...")
                extractor.extract(sound_bsa, temp_dir / "sound")
                self.progress.emit(f"  Extracted {sound_bsa.name}")
            else:
                self.progress.emit(f"Warning: {sound_bsa.name} not found")

            # Extract voices BSA
            if voices_bsa.exists():
                self.progress.emit(f"Extracting {voices_bsa.name}...")
                extractor.extract(voices_bsa, temp_dir / "voices")
                self.progress.emit(f"  Extracted {voices_bsa.name}")
            else:
                self.progress.emit(f"Warning: {voices_bsa.name} not found")

            # Extract menu voices BSA
            if menu_voices_bsa.exists():
                self.progress.emit(f"Extracting {menu_voices_bsa.name}...")
                extractor.extract(menu_voices_bsa, temp_dir / "menu_voices")
                self.progress.emit(f"  Extracted {menu_voices_bsa.name}")

            # Extract DLC sound BSAs
            dlc_bsas = [
                ("Anchorage - Sounds.bsa", "Anchorage"),
                ("ThePitt - Sounds.bsa", "ThePitt"),
                ("BrokenSteel - Sounds.bsa", "BrokenSteel"),
                ("PointLookout - Sounds.bsa", "PointLookout"),
                ("Zeta - Sounds.bsa", "Zeta"),
            ]
            
            for bsa_name, dlc_name in dlc_bsas:
                dlc_bsa = fo3_data / bsa_name
                if dlc_bsa.exists():
                    self.progress.emit(f"Extracting {bsa_name}...")
                    extractor.extract(dlc_bsa, temp_dir / "dlc" / dlc_name)
                    self.progress.emit(f"  Extracted {bsa_name}")

            # Copy music files
            if music_dir.exists():
                self.progress.emit("Copying music files...")
                import shutil
                music_output = temp_dir / "music"
                if music_output.exists():
                    shutil.rmtree(music_output)
                shutil.copytree(music_dir, music_output)
                self.progress.emit("  Copied music files")
            else:
                self.progress.emit(f"Warning: Music folder not found at {music_dir}")

            # Convert MP3 files to xWMA (FO4 doesn't support MP3 in BA2)
            self.progress.emit("Converting MP3 files to xWMA...")
            mp3_files = list(temp_dir.rglob("*.mp3"))
            if mp3_files:
                converted_count = self._convert_mp3_files(mp3_files)
                self.progress.emit(f"  Converted {converted_count} MP3 files to xWMA")
            else:
                self.progress.emit("  No MP3 files to convert")

            # Process FUZ files
            self.progress.emit("Processing FUZ files...")
            fuz_processor = FUZProcessor()
            for fuz_file in temp_dir.rglob("*.fuz"):
                try:
                    fuz_processor.extract_audio(str(fuz_file))
                except Exception as e:
                    self.progress.emit(f"  Warning: Could not process {fuz_file.name}: {e}")

            # Build BA2 using Archive2.exe
            self.progress.emit("Building BA2 archive...")
            self._build_ba2_with_archive2(temp_dir, final_dir)

            # Generate ESM plugin
            self.progress.emit("Generating ESM plugin...")
            esm_path = final_dir / "Fallout3Audio.esm"
            generator = PluginGenerator("Fallout3Audio", as_esl=True)
            generator.generate_from_audio_files(
                list(temp_dir.rglob("*.*")),  # All extracted files
                temp_dir,
                esm_path
            )
            self.progress.emit(f"  Created {esm_path.name}")

            # Cleanup temp directory
            self.progress.emit("Cleaning up...")
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

            self.finished.emit(True, f"Mod created successfully at:\n{final_dir}")

        except Exception as e:
            import traceback
            self.progress.emit(f"Error: {traceback.format_exc()}")
            self.finished.emit(False, str(e))

    def _build_ba2_with_archive2(self, source_dir: Path, output_dir: Path):
        """Build BA2 archive using Archive2.exe."""
        import subprocess

        ba2_path = output_dir / "Fallout3Audio - Main.ba2"

        # Archive2 command for uncompressed audio
        cmd = [
            self.archive2_path,
            str(source_dir),
            f"-c={ba2_path}",
            "-f=General",
            "-compression=None",
            f"-r={source_dir}"
        ]

        self.progress.emit(f"  Running Archive2.exe (this may take 5-10 minutes for ~90k files)...")
        
        # Use Popen so we can show it's still running
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait with extended timeout (30 minutes for large archives)
        try:
            stdout, stderr = process.communicate(timeout=1800)
        except subprocess.TimeoutExpired:
            process.kill()
            raise RuntimeError("Archive2.exe timed out after 30 minutes")

        if process.returncode != 0:
            raise RuntimeError(
                f"Archive2 failed (code {process.returncode}): "
                f"{stderr or stdout}"
            )

        self.progress.emit(f"  Created {ba2_path.name}")

    def _convert_mp3_files(self, mp3_files: list) -> int:
        """Convert MP3 files to WAV format for FO4 compatibility.
        
        FO4's BA2 archives don't properly support MP3 files for music/radio.
        Converting to WAV ensures proper playback.
        
        Uses miniaudio (MIT licensed) for self-contained MP3 decoding.
        
        Returns:
            Number of files successfully converted
        """
        import wave
        import miniaudio
        
        converted = 0
        
        for mp3_file in mp3_files:
            try:
                # Decode MP3 to raw PCM using miniaudio
                decoded = miniaudio.decode_file(str(mp3_file))
                
                # Convert to WAV
                wav_file = mp3_file.with_suffix(".wav")
                
                with wave.open(str(wav_file), 'wb') as wav:
                    wav.setnchannels(decoded.nchannels)
                    wav.setsampwidth(2)  # 16-bit
                    wav.setframerate(decoded.sample_rate)
                    wav.writeframes(decoded.samples)
                
                # Remove original MP3
                mp3_file.unlink()
                converted += 1
                
            except Exception as e:
                self.progress.emit(f"  Warning: Error converting {mp3_file.name}: {e}")
        
        return converted


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.detect_archive2_path()

    def init_ui(self):
        self.setWindowTitle("FO3 Audio for FO4 v1.3.0")
        self.setMinimumSize(700, 550)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Header
        header = QLabel("Fallout 3 Audio Repository Builder")
        header.setStyleSheet(
            "font-size: 18px; font-weight: bold; margin-bottom: 10px;"
        )
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        subtitle = QLabel("Extract FO3 audio and build a FO4 mod")
        subtitle.setStyleSheet("color: gray; margin-bottom: 15px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        # Input paths group
        input_group = QGroupBox("Input Paths")
        input_layout = QVBoxLayout(input_group)

        # FO3 Data Path
        input_layout.addWidget(QLabel("Fallout 3 GOTY Data Directory:"))
        fo3_layout = QHBoxLayout()
        self.fo3_input = QLineEdit()
        self.fo3_input.setPlaceholderText("e.g., D:\\SteamLibrary\\steamapps\\common\\Fallout 3 goty\\Data")
        fo3_btn = QPushButton("Browse")
        fo3_btn.clicked.connect(self.browse_fo3)
        fo3_layout.addWidget(self.fo3_input)
        fo3_layout.addWidget(fo3_btn)
        input_layout.addLayout(fo3_layout)

        # Output Path
        input_layout.addWidget(QLabel("Output Directory:"))
        output_layout = QHBoxLayout()
        self.output_input = QLineEdit()
        self.output_input.setPlaceholderText("Where to save the generated mod")
        output_btn = QPushButton("Browse")
        output_btn.clicked.connect(self.browse_output)
        output_layout.addWidget(self.output_input)
        output_layout.addWidget(output_btn)
        input_layout.addLayout(output_layout)

        layout.addWidget(input_group)

        # Tools group
        tools_group = QGroupBox("Tools")
        tools_layout = QVBoxLayout(tools_group)

        # Archive2 Path
        tools_layout.addWidget(QLabel("Archive2.exe Path (from FO4 Creation Kit):"))
        a2_layout = QHBoxLayout()
        self.a2_input = QLineEdit()
        self.a2_input.setPlaceholderText("Required for building BA2 archives")
        a2_btn = QPushButton("Browse")
        a2_btn.clicked.connect(self.browse_archive2)
        a2_layout.addWidget(self.a2_input)
        a2_layout.addWidget(a2_btn)
        tools_layout.addLayout(a2_layout)

        layout.addWidget(tools_group)

        # Options group
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)

        self.convert_checkbox = QCheckBox(
            "Convert audio to WAV (not recommended - FO4 supports FO3 formats natively)"
        )
        self.convert_checkbox.setChecked(False)
        options_layout.addWidget(self.convert_checkbox)

        layout.addWidget(options_group)

        # Build button
        self.build_btn = QPushButton("Build FO4 Mod")
        self.build_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; "
            "font-weight: bold; padding: 12px; font-size: 14px;"
        )
        self.build_btn.clicked.connect(self.start_build)
        layout.addWidget(self.build_btn)

        # Progress/Log
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("font-family: Consolas, monospace;")
        layout.addWidget(self.log_output)

    def log(self, message: str):
        """Append message to log output."""
        self.log_output.append(message)
        # Auto-scroll to bottom
        scrollbar = self.log_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def detect_archive2_path(self):
        """Try to auto-detect Fallout 4 and Archive2.exe paths.
        
        Note: Fallout 3 cannot be auto-detected on Windows 10/11 as the game
        doesn't run on these OSes and cannot create the needed registry keys.
        Users must manually specify the FO3 path.
        """
        self.log("Note: Fallout 3 GOTY path must be set manually (FO3 doesn't run on Win10/11)")
        
        # Try to detect Fallout 4 installation first (same as CC Packer)
        fo4_paths = [
            r"C:\Program Files (x86)\Steam\steamapps\common\Fallout 4",
            r"C:\Program Files\Steam\steamapps\common\Fallout 4",
            r"D:\SteamLibrary\steamapps\common\Fallout 4",
            r"E:\SteamLibrary\steamapps\common\Fallout 4",
        ]
        
        fo4_found = None
        for fo4_path in fo4_paths:
            if os.path.exists(fo4_path):
                fo4_found = fo4_path
                self.log(f"Found Fallout 4 at: {fo4_path}")
                break
        
        if fo4_found:
            # Check for Archive2.exe in FO4's Tools folder
            self._check_archive2(fo4_found)
            # Set default output to FO4 Data folder (final mod files go directly there)
            fo4_data = os.path.join(fo4_found, "Data")
            self.output_input.setText(fo4_data)
            self.log(f"Output set to Fallout 4 Data folder")
        else:
            self.log("Fallout 4 not found. Archive2.exe must be located manually.")
            self.log("Install the FO4 Creation Kit from Steam to get Archive2.exe.")
            # Fallback output path
            default_output = str(Path.home() / "Documents" / "FO3AudioMod")
            self.output_input.setText(default_output)
    
    def _check_archive2(self, fo4_path: str):
        """Check for Archive2.exe in Fallout 4's Tools folder."""
        default_a2 = os.path.join(fo4_path, "Tools", "Archive2", "Archive2.exe")
        if os.path.exists(default_a2):
            self.a2_input.setText(default_a2)
            self.log("Archive2.exe found automatically.")
        else:
            self.log("Archive2.exe not found in default location.")
            reply = QMessageBox.question(
                self,
                "Archive2 Missing",
                "Archive2.exe was not found in the Fallout 4 Tools folder.\n\n"
                "It is required to build BA2 files. It comes with the Creation Kit.\n\n"
                "Would you like to open the Steam page for the Creation Kit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                webbrowser.open("steam://install/1946160")

    def browse_fo3(self):
        path = QFileDialog.getExistingDirectory(
            self, "Select Fallout 3 Data Directory"
        )
        if path:
            self.fo3_input.setText(path)
            self._validate_fo3_path(path)

    def browse_output(self):
        path = QFileDialog.getExistingDirectory(
            self, "Select Output Directory"
        )
        if path:
            self.output_input.setText(path)

    def browse_archive2(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Archive2.exe", filter="Executables (*.exe)"
        )
        if path:
            self.a2_input.setText(path)

    def _validate_fo3_path(self, path: str) -> bool:
        """Validate FO3 GOTY Data directory has expected files."""
        data_path = Path(path)
        
        # Main game files
        main_files = [
            ("Fallout - Sound.bsa", "Main Sound"),
            ("Fallout - Voices.bsa", "Main Voices"),
            ("Fallout - MenuVoices.bsa", "Menu Voices"),
        ]
        
        # DLC sound files (GOTY Edition)
        dlc_files = [
            ("Anchorage - Sounds.bsa", "Operation Anchorage"),
            ("ThePitt - Sounds.bsa", "The Pitt"),
            ("BrokenSteel - Sounds.bsa", "Broken Steel"),
            ("PointLookout - Sounds.bsa", "Point Lookout"),
            ("Zeta - Sounds.bsa", "Mothership Zeta"),
        ]

        found_main = []
        found_dlc = []
        missing = []

        # Check main game files
        for filename, desc in main_files:
            if (data_path / filename).exists():
                found_main.append(desc)
            else:
                missing.append(desc)

        # Check DLC files
        for filename, desc in dlc_files:
            if (data_path / filename).exists():
                found_dlc.append(desc)

        # Check music folder
        if (data_path / "Music").exists():
            found_main.append("Music folder")
        else:
            missing.append("Music folder")

        # Report findings
        if found_main:
            self.log(f"Found main game: {', '.join(found_main)}")
        if found_dlc:
            self.log(f"Found DLC audio: {', '.join(found_dlc)} ({len(found_dlc)}/5)")
        if not found_dlc:
            self.log("Warning: No DLC audio found - is this GOTY Edition?")
        if missing:
            self.log(f"Missing: {', '.join(missing)}")

        return len(found_main) > 0

    def start_build(self):
        """Start the build process."""
        fo3_path = self.fo3_input.text()
        output_path = self.output_input.text()
        a2_path = self.a2_input.text()

        # Validate inputs
        if not fo3_path or not os.path.exists(fo3_path):
            QMessageBox.warning(self, "Error", "Invalid Fallout 3 Data path.")
            return

        if not output_path:
            QMessageBox.warning(self, "Error", "Please specify an output directory.")
            return

        if not a2_path or not os.path.exists(a2_path):
            reply = QMessageBox.question(
                self,
                "Archive2.exe Missing",
                "Archive2.exe is required to build BA2 archives.\n\n"
                "It comes with the Fallout 4 Creation Kit.\n\n"
                "Would you like to open the Steam page?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                webbrowser.open("steam://install/1946160")
            return

        # Disable button during build
        self.build_btn.setEnabled(False)
        self.build_btn.setText("Building...")
        self.log("\n" + "="*50)
        self.log("Starting build process...")
        self.log("="*50)

        # Start worker thread
        self.worker = ExtractWorker(
            fo3_path,
            output_path,
            a2_path,
            self.convert_checkbox.isChecked()
        )
        self.worker.progress.connect(self.log)
        self.worker.finished.connect(self.on_build_finished)
        self.worker.start()

    def on_build_finished(self, success: bool, message: str):
        """Handle build completion."""
        self.build_btn.setEnabled(True)
        self.build_btn.setText("Build FO4 Mod")

        if success:
            self.log("\n" + "="*50)
            self.log("BUILD SUCCESSFUL!")
            self.log("="*50)
            QMessageBox.information(self, "Success", message)
        else:
            self.log("\n" + "="*50)
            self.log(f"BUILD FAILED: {message}")
            self.log("="*50)
            QMessageBox.critical(self, "Error", f"Build failed:\n{message}")


def main():
    """Main entry point for GUI application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
