"""BSA archive extraction utilities for Fallout 3 archives."""

import logging
import struct
import zlib
from pathlib import Path
from typing import BinaryIO, Optional

logger = logging.getLogger(__name__)


class BSAHeader:
    """BSA file header structure."""

    def __init__(self, data: bytes) -> None:
        """Parse BSA header from raw bytes."""
        (
            self.file_id,
            self.version,
            self.offset,
            self.archive_flags,
            self.folder_count,
            self.file_count,
            self.total_folder_name_length,
            self.total_file_name_length,
            self.file_flags,
        ) = struct.unpack("<4sIIIIIIII", data[:36])

    @property
    def is_valid(self) -> bool:
        """Check if this is a valid BSA file."""
        return self.file_id == b"BSA\x00"

    @property
    def has_folder_names(self) -> bool:
        """Check if archive includes folder names."""
        return bool(self.archive_flags & 0x1)

    @property
    def has_file_names(self) -> bool:
        """Check if archive includes file names."""
        return bool(self.archive_flags & 0x2)

    @property
    def is_compressed(self) -> bool:
        """Check if files are compressed by default."""
        return bool(self.archive_flags & 0x4)

    @property
    def is_xbox(self) -> bool:
        """Check if this is an Xbox archive."""
        return bool(self.archive_flags & 0x40)

    @property
    def has_embedded_names(self) -> bool:
        """Check if file names are embedded in file data."""
        return bool(self.archive_flags & 0x100)

    @property
    def uses_xmem(self) -> bool:
        """Check if archive uses XMem compression."""
        return bool(self.archive_flags & 0x200)


class BSAFolderRecord:
    """Folder record in BSA archive."""
    
    def __init__(self, name_hash: int, count: int, offset: int):
        self.name_hash = name_hash
        self.count = count
        self.offset = offset
        self.name = ""


class BSAFileRecord:
    """File record in BSA archive."""
    
    def __init__(self, name_hash: int, size: int, offset: int, default_compressed: bool):
        self.name_hash = name_hash
        # Size field: bit 30 = compression toggle, bits 0-29 = size
        self.compression_toggle = bool(size & 0x40000000)
        self.size = size & 0x3FFFFFFF
        self.offset = offset
        self.name = ""
        self.default_compressed = default_compressed
    
    @property
    def is_compressed(self) -> bool:
        """Check if this specific file is compressed."""
        # If toggle bit is set, flip the default compression state
        return self.default_compressed != self.compression_toggle


class BSAExtractor:
    """Extract files from Bethesda Softworks Archive (BSA) files."""

    SUPPORTED_VERSIONS = [103, 104, 105]  # Fallout 3/NV uses version 104

    def __init__(self) -> None:
        """Initialize the BSA extractor."""
        self.logger = logging.getLogger(__name__)

    def extract(
        self,
        bsa_path: Path,
        output_dir: Path,
        filter_pattern: Optional[str] = None,
    ) -> Path:
        """
        Extract files from a BSA archive.

        Args:
            bsa_path: Path to the BSA file
            output_dir: Directory to extract files to
            filter_pattern: Optional glob pattern to filter files (e.g., "*.wav")

        Returns:
            Path to the extraction directory
        """
        self.logger.info(f"Extracting BSA: {bsa_path}")

        if not bsa_path.exists():
            raise FileNotFoundError(f"BSA file not found: {bsa_path}")

        output_dir.mkdir(parents=True, exist_ok=True)

        with open(bsa_path, "rb") as bsa_file:
            # Read and validate header
            header_data = bsa_file.read(36)
            header = BSAHeader(header_data)

            if not header.is_valid:
                raise ValueError(f"Invalid BSA file: {bsa_path}")

            if header.version not in self.SUPPORTED_VERSIONS:
                self.logger.warning(
                    f"BSA version {header.version} may not be fully supported"
                )

            self.logger.debug(
                f"BSA contains {header.folder_count} folders, "
                f"{header.file_count} files, compressed={header.is_compressed}"
            )

            # Extract files
            extracted_count = self._extract_files(
                bsa_file, header, output_dir, filter_pattern
            )

        self.logger.info(f"Extracted {extracted_count} files to {output_dir}")
        return output_dir

    def _extract_files(
        self,
        bsa_file: BinaryIO,
        header: BSAHeader,
        output_dir: Path,
        filter_pattern: Optional[str],
    ) -> int:
        """Extract files from the BSA archive."""
        extracted_count = 0

        # Read folder records
        folder_records: list[BSAFolderRecord] = []
        for _ in range(header.folder_count):
            name_hash = struct.unpack("<Q", bsa_file.read(8))[0]
            count = struct.unpack("<I", bsa_file.read(4))[0]
            offset = struct.unpack("<I", bsa_file.read(4))[0]
            folder_records.append(BSAFolderRecord(name_hash, count, offset))

        # Read file record blocks (folder name + file records for each folder)
        all_file_records: list[tuple[str, BSAFileRecord]] = []
        
        for folder in folder_records:
            # Read folder name
            if header.has_folder_names:
                name_len = struct.unpack("<B", bsa_file.read(1))[0]
                folder_name = bsa_file.read(name_len).decode("cp1252", errors="replace")
                folder.name = folder_name.rstrip("\x00")
            
            # Read file records for this folder
            for _ in range(folder.count):
                file_hash = struct.unpack("<Q", bsa_file.read(8))[0]
                size = struct.unpack("<I", bsa_file.read(4))[0]
                offset = struct.unpack("<I", bsa_file.read(4))[0]
                
                file_record = BSAFileRecord(file_hash, size, offset, header.is_compressed)
                all_file_records.append((folder.name, file_record))

        # Read file names from the file name block
        if header.has_file_names:
            for folder_name, file_record in all_file_records:
                # Read null-terminated string
                name_bytes = b""
                while True:
                    char = bsa_file.read(1)
                    if char == b"\x00" or char == b"":
                        break
                    name_bytes += char
                file_record.name = name_bytes.decode("cp1252", errors="replace")

        # Now extract the actual file data
        for folder_name, file_record in all_file_records:
            full_path = f"{folder_name}\\{file_record.name}" if folder_name else file_record.name
            
            # Apply filter if specified
            if filter_pattern:
                if not Path(full_path).match(filter_pattern):
                    continue
            
            # Seek to file data
            bsa_file.seek(file_record.offset)
            
            # Handle embedded file name (for archives with flag 0x100)
            actual_size = file_record.size
            if header.has_embedded_names:
                embedded_len = struct.unpack("<B", bsa_file.read(1))[0]
                bsa_file.read(embedded_len)  # Skip embedded name
                actual_size -= (1 + embedded_len)
            
            # Read file data
            if file_record.is_compressed:
                # First 4 bytes are the uncompressed size
                uncompressed_size = struct.unpack("<I", bsa_file.read(4))[0]
                compressed_data = bsa_file.read(actual_size - 4)
                try:
                    file_data = zlib.decompress(compressed_data)
                except zlib.error as e:
                    self.logger.warning(f"Failed to decompress {full_path}: {e}")
                    continue
            else:
                file_data = bsa_file.read(actual_size)
            
            # Write file
            output_path = output_dir / full_path.replace("\\", "/")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, "wb") as out_file:
                out_file.write(file_data)
            
            extracted_count += 1

        return extracted_count

    def list_contents(self, bsa_path: Path) -> list[str]:
        """
        List all files in a BSA archive.

        Args:
            bsa_path: Path to the BSA file

        Returns:
            List of file paths within the archive
        """
        self.logger.info(f"Listing contents of: {bsa_path}")
        files: list[str] = []

        with open(bsa_path, "rb") as bsa_file:
            header_data = bsa_file.read(36)
            header = BSAHeader(header_data)

            if not header.is_valid:
                raise ValueError(f"Invalid BSA file: {bsa_path}")

            # Read folder records
            folder_records: list[BSAFolderRecord] = []
            for _ in range(header.folder_count):
                name_hash = struct.unpack("<Q", bsa_file.read(8))[0]
                count = struct.unpack("<I", bsa_file.read(4))[0]
                offset = struct.unpack("<I", bsa_file.read(4))[0]
                folder_records.append(BSAFolderRecord(name_hash, count, offset))

            # Read file records
            all_records: list[tuple[str, BSAFileRecord]] = []
            for folder in folder_records:
                if header.has_folder_names:
                    name_len = struct.unpack("<B", bsa_file.read(1))[0]
                    folder_name = bsa_file.read(name_len).decode("cp1252", errors="replace")
                    folder.name = folder_name.rstrip("\x00")
                
                for _ in range(folder.count):
                    file_hash = struct.unpack("<Q", bsa_file.read(8))[0]
                    size = struct.unpack("<I", bsa_file.read(4))[0]
                    offset = struct.unpack("<I", bsa_file.read(4))[0]
                    file_record = BSAFileRecord(file_hash, size, offset, header.is_compressed)
                    all_records.append((folder.name, file_record))

            # Read file names
            if header.has_file_names:
                for folder_name, file_record in all_records:
                    name_bytes = b""
                    while True:
                        char = bsa_file.read(1)
                        if char == b"\x00" or char == b"":
                            break
                        name_bytes += char
                    file_record.name = name_bytes.decode("cp1252", errors="replace")
                    files.append(f"{folder_name}\\{file_record.name}" if folder_name else file_record.name)

        return files

    def extract_audio_only(self, bsa_path: Path, output_dir: Path) -> Path:
        """
        Extract only audio files from a BSA archive.

        Args:
            bsa_path: Path to the BSA file
            output_dir: Directory to extract files to

        Returns:
            Path to the extraction directory
        """
        return self.extract(bsa_path, output_dir, filter_pattern="sound/*")
