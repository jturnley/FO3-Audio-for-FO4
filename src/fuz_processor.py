"""FUZ file processing for Fallout lip sync audio files."""

import logging
import struct
from pathlib import Path
from typing import Optional, NamedTuple

logger = logging.getLogger(__name__)


class FUZHeader(NamedTuple):
    """FUZ file header structure."""

    magic: bytes  # "FUZE" for FO3/FO4
    version: int
    lip_size: int
    audio_size: int


class LipData(NamedTuple):
    """Lip sync data extracted from FUZ file."""

    data: bytes
    duration: float


class FUZProcessor:
    """Process Fallout FUZ files containing audio and lip sync data."""

    MAGIC_FO3 = b"FUZE"  # Fallout 3/NV FUZ magic
    MAGIC_FO4 = b"FUZE"  # Fallout 4 uses same magic

    def __init__(self) -> None:
        """Initialize the FUZ processor."""
        self.logger = logging.getLogger(__name__)

    def read_fuz(self, fuz_path: Path) -> tuple[bytes, Optional[bytes]]:
        """
        Read and extract audio and lip data from a FUZ file.

        Args:
            fuz_path: Path to the FUZ file

        Returns:
            Tuple of (audio_data, lip_data) where lip_data may be None
        """
        self.logger.debug(f"Reading FUZ file: {fuz_path}")

        if not fuz_path.exists():
            raise FileNotFoundError(f"FUZ file not found: {fuz_path}")

        with open(fuz_path, "rb") as f:
            # Read header
            magic = f.read(4)
            if magic != self.MAGIC_FO3:
                raise ValueError(f"Invalid FUZ file magic: {magic}")

            version = struct.unpack("<I", f.read(4))[0]
            self.logger.debug(f"FUZ version: {version}")

            # Read sizes
            lip_size = struct.unpack("<I", f.read(4))[0]

            # Read lip data if present
            lip_data: Optional[bytes] = None
            if lip_size > 0:
                lip_data = f.read(lip_size)
                self.logger.debug(f"Read {lip_size} bytes of lip data")

            # Read audio data (rest of file)
            audio_data = f.read()
            self.logger.debug(f"Read {len(audio_data)} bytes of audio data")

        return audio_data, lip_data

    def extract_audio(
        self,
        fuz_path: Path,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Extract audio from a FUZ file.

        Args:
            fuz_path: Path to the FUZ file
            output_path: Path for extracted audio (default: same name with .xwm extension)

        Returns:
            Path to the extracted audio file
        """
        if output_path is None:
            output_path = fuz_path.with_suffix(".xwm")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        audio_data, _ = self.read_fuz(fuz_path)

        with open(output_path, "wb") as f:
            f.write(audio_data)

        self.logger.info(f"Extracted audio to: {output_path}")
        return output_path

    def extract_lip(
        self,
        fuz_path: Path,
        output_path: Optional[Path] = None,
    ) -> Optional[Path]:
        """
        Extract lip sync data from a FUZ file.

        Args:
            fuz_path: Path to the FUZ file
            output_path: Path for extracted lip data (default: same name with .lip extension)

        Returns:
            Path to the extracted lip file, or None if no lip data
        """
        if output_path is None:
            output_path = fuz_path.with_suffix(".lip")

        _, lip_data = self.read_fuz(fuz_path)

        if lip_data is None or len(lip_data) == 0:
            self.logger.warning(f"No lip data in FUZ file: {fuz_path}")
            return None

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(lip_data)

        self.logger.info(f"Extracted lip data to: {output_path}")
        return output_path

    def create_fuz(
        self,
        audio_path: Path,
        lip_path: Optional[Path],
        output_path: Path,
    ) -> Path:
        """
        Create a FUZ file from audio and lip sync data.

        Args:
            audio_path: Path to the audio file (xWMA format)
            lip_path: Path to the lip sync file (optional)
            output_path: Path for the output FUZ file

        Returns:
            Path to the created FUZ file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Read audio data
        with open(audio_path, "rb") as f:
            audio_data = f.read()

        # Read lip data if provided
        lip_data = b""
        if lip_path and lip_path.exists():
            with open(lip_path, "rb") as f:
                lip_data = f.read()

        # Write FUZ file
        with open(output_path, "wb") as f:
            # Write header
            f.write(self.MAGIC_FO4)  # Magic
            f.write(struct.pack("<I", 1))  # Version
            f.write(struct.pack("<I", len(lip_data)))  # Lip size

            # Write lip data
            if lip_data:
                f.write(lip_data)

            # Write audio data
            f.write(audio_data)

        self.logger.info(f"Created FUZ file: {output_path}")
        return output_path

    def process_directory(
        self,
        input_dir: Path,
        output_dir: Optional[Path] = None,
    ) -> list[Path]:
        """
        Process all FUZ files in a directory.

        Args:
            input_dir: Directory containing FUZ files
            output_dir: Directory for extracted files (default: same as input)

        Returns:
            List of extracted audio file paths
        """
        if output_dir is None:
            output_dir = input_dir

        output_dir.mkdir(parents=True, exist_ok=True)

        extracted_files: list[Path] = []
        fuz_files = list(input_dir.rglob("*.fuz"))

        self.logger.info(f"Found {len(fuz_files)} FUZ files to process")

        for fuz_path in fuz_files:
            try:
                # Preserve directory structure
                relative_path = fuz_path.relative_to(input_dir)
                output_path = output_dir / relative_path.with_suffix(".xwm")

                audio_path = self.extract_audio(fuz_path, output_path)
                extracted_files.append(audio_path)

                # Also extract lip data
                lip_output = output_dir / relative_path.with_suffix(".lip")
                self.extract_lip(fuz_path, lip_output)

            except Exception as e:
                self.logger.error(f"Failed to process {fuz_path}: {e}")

        self.logger.info(f"Processed {len(extracted_files)} FUZ files")
        return extracted_files

    def convert_fo3_to_fo4(
        self,
        input_path: Path,
        output_path: Path,
    ) -> Path:
        """
        Convert a Fallout 3 FUZ file to Fallout 4 format.

        Note: FO3 and FO4 FUZ formats are very similar, but audio
        encoding may differ. This method handles the conversion.

        Args:
            input_path: Path to the FO3 FUZ file
            output_path: Path for the FO4 FUZ file

        Returns:
            Path to the converted FUZ file
        """
        self.logger.info(f"Converting FO3 FUZ to FO4 format: {input_path}")

        # Extract components
        audio_data, lip_data = self.read_fuz(input_path)

        # For FO3 to FO4, the format is essentially the same
        # The main difference is in audio encoding which is handled
        # by the AudioConverter

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(self.MAGIC_FO4)
            f.write(struct.pack("<I", 1))  # Version
            f.write(struct.pack("<I", len(lip_data) if lip_data else 0))

            if lip_data:
                f.write(lip_data)

            f.write(audio_data)

        self.logger.info(f"Converted FUZ file: {output_path}")
        return output_path
