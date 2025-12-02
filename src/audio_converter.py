"""Audio format conversion utilities for Fallout audio files."""

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class AudioConverter:
    """Convert audio files between formats for Fallout modding."""

    SUPPORTED_INPUT_FORMATS = [".wav", ".xwm", ".mp3", ".ogg", ".fuz"]
    SUPPORTED_OUTPUT_FORMATS = [".wav", ".xwm", ".fuz"]

    def __init__(self, tools_dir: Optional[Path] = None) -> None:
        """
        Initialize the audio converter.

        Args:
            tools_dir: Directory containing external tools (xWMAEncode, ffmpeg, etc.)
        """
        self.logger = logging.getLogger(__name__)
        self.tools_dir = tools_dir or Path("tools")
        self._xwma_encoder: Optional[Path] = None
        self._ffmpeg: Optional[Path] = None

    @property
    def xwma_encoder(self) -> Optional[Path]:
        """Get path to xWMAEncode executable."""
        if self._xwma_encoder is None:
            # Check tools directory first
            encoder_path = self.tools_dir / "xWMAEncode.exe"
            if encoder_path.exists():
                self._xwma_encoder = encoder_path
            else:
                # Check if in PATH
                found = shutil.which("xWMAEncode")
                if found:
                    self._xwma_encoder = Path(found)
        return self._xwma_encoder

    @property
    def ffmpeg(self) -> Optional[Path]:
        """Get path to ffmpeg executable."""
        if self._ffmpeg is None:
            # Check tools directory first
            ffmpeg_path = self.tools_dir / "ffmpeg.exe"
            if ffmpeg_path.exists():
                self._ffmpeg = ffmpeg_path
            else:
                # Check if in PATH
                found = shutil.which("ffmpeg")
                if found:
                    self._ffmpeg = Path(found)
        return self._ffmpeg

    def convert_to_xwma(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
        bitrate: int = 48000,
    ) -> Path:
        """
        Convert an audio file to xWMA format.

        Args:
            input_path: Path to input audio file
            output_path: Path for output file (default: same name with .xwm extension)
            bitrate: Target bitrate in bits per second

        Returns:
            Path to the converted file
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        if output_path is None:
            output_path = input_path.with_suffix(".xwm")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        self.logger.debug(f"Converting {input_path} to xWMA")

        # First convert to WAV if necessary
        if input_path.suffix.lower() != ".wav":
            wav_path = self._convert_to_wav(input_path)
        else:
            wav_path = input_path

        # Then convert WAV to xWMA
        if self.xwma_encoder:
            self._xwma_encode(wav_path, output_path, bitrate)
        else:
            raise RuntimeError(
                "xWMAEncode not found. Please place xWMAEncode.exe in the tools directory."
            )

        # Clean up temporary WAV if we created one
        if wav_path != input_path and wav_path.exists():
            wav_path.unlink()

        self.logger.info(f"Converted to xWMA: {output_path}")
        return output_path

    def convert_to_wav(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Convert an audio file to WAV format.

        Args:
            input_path: Path to input audio file
            output_path: Path for output file (default: same name with .wav extension)

        Returns:
            Path to the converted file
        """
        if output_path is None:
            output_path = input_path.with_suffix(".wav")

        return self._convert_to_wav(input_path, output_path)

    def _convert_to_wav(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
    ) -> Path:
        """Internal WAV conversion using ffmpeg."""
        if output_path is None:
            output_path = input_path.with_suffix(".wav")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.ffmpeg:
            raise RuntimeError(
                "ffmpeg not found. Please install ffmpeg or place it in the tools directory."
            )

        cmd = [
            str(self.ffmpeg),
            "-i", str(input_path),
            "-acodec", "pcm_s16le",
            "-ar", "44100",
            "-ac", "1",
            "-y",
            str(output_path),
        ]

        self.logger.debug(f"Running ffmpeg: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            self.logger.error(f"ffmpeg error: {result.stderr}")
            raise RuntimeError(f"ffmpeg conversion failed: {result.stderr}")

        return output_path

    def _xwma_encode(
        self,
        input_path: Path,
        output_path: Path,
        bitrate: int,
    ) -> None:
        """Encode a WAV file to xWMA using xWMAEncode."""
        if not self.xwma_encoder:
            raise RuntimeError("xWMAEncode not found")

        cmd = [
            str(self.xwma_encoder),
            str(input_path),
            str(output_path),
            "/b", str(bitrate),
        ]

        self.logger.debug(f"Running xWMAEncode: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            self.logger.error(f"xWMAEncode error: {result.stderr}")
            raise RuntimeError(f"xWMAEncode conversion failed: {result.stderr}")

    def convert_batch(
        self,
        input_files: list[Path],
        output_dir: Path,
        target_format: str = ".xwm",
    ) -> list[Path]:
        """
        Convert multiple audio files to the target format.

        Args:
            input_files: List of input file paths
            output_dir: Directory for output files
            target_format: Target format extension (default: .xwm)

        Returns:
            List of converted file paths
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        converted_files: list[Path] = []

        for input_file in input_files:
            try:
                output_path = output_dir / input_file.with_suffix(target_format).name

                if target_format == ".xwm":
                    converted = self.convert_to_xwma(input_file, output_path)
                elif target_format == ".wav":
                    converted = self.convert_to_wav(input_file, output_path)
                else:
                    self.logger.warning(f"Unsupported target format: {target_format}")
                    continue

                converted_files.append(converted)

            except Exception as e:
                self.logger.error(f"Failed to convert {input_file}: {e}")

        self.logger.info(
            f"Converted {len(converted_files)}/{len(input_files)} files"
        )
        return converted_files

    def validate_audio(self, file_path: Path) -> bool:
        """
        Validate an audio file.

        Args:
            file_path: Path to the audio file

        Returns:
            True if the file is valid, False otherwise
        """
        if not file_path.exists():
            return False

        if file_path.stat().st_size == 0:
            return False

        # Check file signature based on format
        try:
            with open(file_path, "rb") as f:
                header = f.read(4)

                if file_path.suffix.lower() == ".wav":
                    return header == b"RIFF"
                elif file_path.suffix.lower() == ".xwm":
                    return header == b"RIFF"  # xWMA also uses RIFF
                elif file_path.suffix.lower() == ".fuz":
                    return header == b"FUZE"

        except Exception as e:
            self.logger.error(f"Validation error for {file_path}: {e}")

        return False
