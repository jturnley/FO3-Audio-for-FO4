"""BA2 archive builder for Fallout 4."""

import logging
import struct
import subprocess
import zlib
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import BinaryIO, Callable, Optional

logger = logging.getLogger(__name__)


class BA2Type(IntEnum):
    """BA2 archive types."""
    GNRL = 0  # General archive (loose files)
    DX10 = 1  # Texture archive
    GNMF = 2  # GNF textures (PS4)


class BA2CompressionType(IntEnum):
    """BA2 compression types."""
    NONE = 0
    ZLIB = 1
    LZ4 = 2


@dataclass
class BA2FileRecord:
    """Record for a file in a BA2 archive."""
    
    name_hash: int
    ext: bytes  # 4-byte extension
    dir_hash: int
    flags: int
    offset: int
    packed_size: int
    unpacked_size: int
    data: bytes
    path: str  # Full relative path


@dataclass
class BA2Header:
    """BA2 file header structure."""
    
    MAGIC = b"BTDX"
    VERSION = 1  # FO4 uses version 1
    
    archive_type: BA2Type
    file_count: int
    name_table_offset: int


class BA2Builder:
    """Build Fallout 4 BA2 archives."""
    
    def __init__(self, compress: bool = False) -> None:
        """
        Initialize the BA2 builder.
        
        Args:
            compress: Whether to compress files in the archive.
                      NOTE: Audio BA2 files for FO4 must be uncompressed!
        """
        self.logger = logging.getLogger(__name__)
        self.compress = compress
        self.files: list[BA2FileRecord] = []
    
    def add_file(self, file_path: Path, archive_path: str) -> None:
        """
        Add a file to the archive.
        
        Args:
            file_path: Path to the file on disk
            archive_path: Path within the archive (e.g., "Sound/Voice/...")
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, "rb") as f:
            data = f.read()
        
        # Normalize path separators
        archive_path = archive_path.replace("/", "\\")
        
        # Calculate hashes
        name_hash = self._hash_string(Path(archive_path).stem.lower())
        dir_hash = self._hash_string(str(Path(archive_path).parent).lower())
        
        # Get extension (padded to 4 bytes)
        ext = Path(archive_path).suffix[1:].lower().encode("ascii")[:4].ljust(4, b"\x00")
        
        record = BA2FileRecord(
            name_hash=name_hash,
            ext=ext,
            dir_hash=dir_hash,
            flags=0,
            offset=0,  # Set during build
            packed_size=0,  # Set during build
            unpacked_size=len(data),
            data=data,
            path=archive_path,
        )
        
        self.files.append(record)
        self.logger.debug(f"Added file: {archive_path}")
    
    def add_directory(self, source_dir: Path, archive_base: str = "") -> int:
        """
        Add all files from a directory to the archive.
        
        Args:
            source_dir: Directory containing files to add
            archive_base: Base path within the archive
            
        Returns:
            Number of files added
        """
        count = 0
        for file_path in source_dir.rglob("*"):
            if file_path.is_file():
                relative = file_path.relative_to(source_dir)
                archive_path = str(Path(archive_base) / relative) if archive_base else str(relative)
                self.add_file(file_path, archive_path)
                count += 1
        
        self.logger.info(f"Added {count} files from {source_dir}")
        return count
    
    def build(self, output_path: Path) -> Path:
        """
        Build the BA2 archive.
        
        Args:
            output_path: Path for the output BA2 file
            
        Returns:
            Path to the created archive
        """
        if not self.files:
            raise ValueError("No files added to archive")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Building BA2 archive with {len(self.files)} files")
        
        with open(output_path, "wb") as f:
            self._write_archive(f)
        
        self.logger.info(f"Created BA2 archive: {output_path}")
        return output_path
    
    def _write_archive(self, f: BinaryIO) -> None:
        """Write the BA2 archive to a file."""
        file_count = len(self.files)
        
        # Calculate header size
        header_size = 24  # Magic(4) + Version(4) + Type(4) + FileCount(4) + NameTableOffset(8)
        file_records_size = file_count * 36  # Each GNRL record is 36 bytes
        
        # Start of file data
        data_offset = header_size + file_records_size
        
        # Prepare file data and update records
        current_offset = data_offset
        file_data_blocks: list[bytes] = []
        
        for record in self.files:
            if self.compress:
                compressed = zlib.compress(record.data, level=6)
                # Only use compression if it actually saves space
                if len(compressed) < len(record.data):
                    record.packed_size = len(compressed)
                    file_data_blocks.append(compressed)
                else:
                    record.packed_size = 0  # 0 means uncompressed
                    file_data_blocks.append(record.data)
            else:
                record.packed_size = 0
                file_data_blocks.append(record.data)
            
            record.offset = current_offset
            current_offset += len(file_data_blocks[-1])
        
        # Name table offset is after all file data
        name_table_offset = current_offset
        
        # Write header
        f.write(BA2Header.MAGIC)
        f.write(struct.pack("<I", BA2Header.VERSION))
        f.write(struct.pack("<I", BA2Type.GNRL))
        f.write(struct.pack("<I", file_count))
        f.write(struct.pack("<Q", name_table_offset))
        
        # Write file records
        for record in self.files:
            f.write(struct.pack("<I", record.name_hash))
            f.write(record.ext)
            f.write(struct.pack("<I", record.dir_hash))
            f.write(struct.pack("<I", record.flags))
            f.write(struct.pack("<Q", record.offset))
            f.write(struct.pack("<I", record.packed_size))
            f.write(struct.pack("<I", record.unpacked_size))
            f.write(struct.pack("<I", 0xBAADF00D))  # Padding/alignment
        
        # Write file data
        for data_block in file_data_blocks:
            f.write(data_block)
        
        # Write name table
        for record in self.files:
            # Write length-prefixed string
            name_bytes = record.path.encode("utf-8")
            f.write(struct.pack("<H", len(name_bytes)))
            f.write(name_bytes)
    
    def _hash_string(self, s: str) -> int:
        """
        Calculate Bethesda-style hash for a string.
        
        This is a simplified version of the hash algorithm used by Bethesda.
        """
        if not s:
            return 0
        
        # Convert to lowercase and normalize
        s = s.lower().replace("/", "\\")
        
        # Simple hash algorithm (FNV-1a variant)
        hash_value = 0x811c9dc5
        for char in s.encode("utf-8"):
            hash_value ^= char
            hash_value = (hash_value * 0x01000193) & 0xFFFFFFFF
        
        return hash_value
    
    def clear(self) -> None:
        """Clear all files from the builder."""
        self.files.clear()


class BA2Reader:
    """Read Fallout 4 BA2 archives."""
    
    def __init__(self, ba2_path: Path) -> None:
        """
        Initialize the BA2 reader.
        
        Args:
            ba2_path: Path to the BA2 file
        """
        self.logger = logging.getLogger(__name__)
        self.ba2_path = ba2_path
        self.files: dict[str, BA2FileRecord] = {}
        self._parse()
    
    def _parse(self) -> None:
        """Parse the BA2 archive."""
        with open(self.ba2_path, "rb") as f:
            # Read header
            magic = f.read(4)
            if magic != BA2Header.MAGIC:
                raise ValueError(f"Invalid BA2 file: {self.ba2_path}")
            
            version = struct.unpack("<I", f.read(4))[0]
            archive_type = BA2Type(struct.unpack("<I", f.read(4))[0])
            file_count = struct.unpack("<I", f.read(4))[0]
            name_table_offset = struct.unpack("<Q", f.read(8))[0]
            
            self.logger.debug(
                f"BA2: version={version}, type={archive_type}, files={file_count}"
            )
            
            # Read file records
            records: list[BA2FileRecord] = []
            for _ in range(file_count):
                name_hash = struct.unpack("<I", f.read(4))[0]
                ext = f.read(4)
                dir_hash = struct.unpack("<I", f.read(4))[0]
                flags = struct.unpack("<I", f.read(4))[0]
                offset = struct.unpack("<Q", f.read(8))[0]
                packed_size = struct.unpack("<I", f.read(4))[0]
                unpacked_size = struct.unpack("<I", f.read(4))[0]
                _padding = f.read(4)  # Padding
                
                records.append(BA2FileRecord(
                    name_hash=name_hash,
                    ext=ext,
                    dir_hash=dir_hash,
                    flags=flags,
                    offset=offset,
                    packed_size=packed_size,
                    unpacked_size=unpacked_size,
                    data=b"",
                    path="",
                ))
            
            # Read name table
            f.seek(name_table_offset)
            for record in records:
                name_len = struct.unpack("<H", f.read(2))[0]
                record.path = f.read(name_len).decode("utf-8")
                self.files[record.path.lower()] = record
    
    def extract(self, output_dir: Path, filter_pattern: Optional[str] = None) -> int:
        """
        Extract files from the BA2 archive.
        
        Args:
            output_dir: Directory to extract files to
            filter_pattern: Optional glob pattern to filter files
            
        Returns:
            Number of files extracted
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        extracted = 0
        
        with open(self.ba2_path, "rb") as f:
            for path, record in self.files.items():
                if filter_pattern:
                    if not Path(path).match(filter_pattern):
                        continue
                
                # Read file data
                f.seek(record.offset)
                if record.packed_size > 0:
                    compressed_data = f.read(record.packed_size)
                    data = zlib.decompress(compressed_data)
                else:
                    data = f.read(record.unpacked_size)
                
                # Write to output
                output_path = output_dir / record.path
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "wb") as out:
                    out.write(data)
                
                extracted += 1
        
        self.logger.info(f"Extracted {extracted} files to {output_dir}")
        return extracted
    
    def list_files(self) -> list[str]:
        """List all files in the archive."""
        return list(self.files.keys())


class Archive2Error(Exception):
    """Exception for Archive2.exe operations."""

    def __init__(
        self,
        message: str,
        operation: str,
        archive_path: Optional[str] = None,
        return_code: Optional[int] = None,
        stdout: Optional[str] = None,
        stderr: Optional[str] = None,
    ):
        self.operation = operation
        self.archive_path = archive_path
        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr

        details = [f"Archive2 {operation} failed"]
        if archive_path:
            details.append(f"Archive: {archive_path}")
        if return_code is not None:
            details.append(f"Exit code: {return_code}")
        if stderr and stderr.strip():
            details.append(f"Error: {stderr.strip()}")
        if message:
            details.append(f"Details: {message}")

        super().__init__("\n".join(details))


class Archive2Builder:
    """
    Build Fallout 4 BA2 archives using Bethesda's Archive2.exe.
    
    This is the recommended method for creating BA2 archives as it ensures
    proper compatibility with Fallout 4.
    """

    def __init__(self, archive2_path: str | Path) -> None:
        """
        Initialize the Archive2 builder.
        
        Args:
            archive2_path: Path to Archive2.exe (from FO4 Creation Kit)
        """
        self.logger = logging.getLogger(__name__)
        self.archive2_path = Path(archive2_path)
        
        if not self.archive2_path.exists():
            raise FileNotFoundError(f"Archive2.exe not found: {archive2_path}")

    def create_archive(
        self,
        source_dir: Path,
        output_path: Path,
        archive_type: str = "General",
        compression: str = "None",
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> Path:
        """
        Create a BA2 archive from a directory.
        
        Args:
            source_dir: Directory containing files to archive
            output_path: Path for the output BA2 file
            archive_type: Archive type - "General" for audio/meshes, "DDS" for textures
            compression: Compression type - "None" for audio, "Default" for other files
            progress_callback: Optional callback for progress messages
            
        Returns:
            Path to the created archive
            
        Raises:
            Archive2Error: If archive creation fails
        """
        # Archive2.exe requires absolute paths
        source_dir = Path(source_dir).resolve()
        output_path = Path(output_path).resolve()
        
        if not source_dir.exists():
            raise FileNotFoundError(f"Source directory not found: {source_dir}")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            str(self.archive2_path),
            str(source_dir),
            f"-c={output_path}",
            f"-f={archive_type}",
            f"-compression={compression}",
            f"-r={source_dir}",
        ]
        
        if progress_callback:
            progress_callback(f"Creating archive: {output_path.name}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout for large archives
            )
            
            if result.returncode != 0:
                raise Archive2Error(
                    message=self._parse_error(result.stderr, result.stdout),
                    operation="create",
                    archive_path=str(output_path),
                    return_code=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr,
                )
            
            if progress_callback:
                progress_callback(f"Created: {output_path.name}")
            
            self.logger.info(f"Created BA2 archive: {output_path}")
            return output_path
            
        except subprocess.TimeoutExpired:
            raise Archive2Error(
                message="Operation timed out after 10 minutes",
                operation="create",
                archive_path=str(output_path),
            )
        except FileNotFoundError:
            raise Archive2Error(
                message=f"Archive2.exe not found: {self.archive2_path}",
                operation="create",
                archive_path=str(output_path),
            )

    def extract_archive(
        self,
        ba2_path: Path,
        output_dir: Path,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> Path:
        """
        Extract a BA2 archive to a directory.
        
        Args:
            ba2_path: Path to the BA2 file
            output_dir: Directory to extract files to
            progress_callback: Optional callback for progress messages
            
        Returns:
            Path to the output directory
            
        Raises:
            Archive2Error: If extraction fails
        """
        ba2_path = Path(ba2_path)
        output_dir = Path(output_dir)
        
        if not ba2_path.exists():
            raise FileNotFoundError(f"BA2 file not found: {ba2_path}")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            str(self.archive2_path),
            str(ba2_path),
            f"-e={output_dir}",
        ]
        
        if progress_callback:
            progress_callback(f"Extracting: {ba2_path.name}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,
            )
            
            if result.returncode != 0:
                raise Archive2Error(
                    message=self._parse_error(result.stderr, result.stdout),
                    operation="extract",
                    archive_path=str(ba2_path),
                    return_code=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr,
                )
            
            if progress_callback:
                progress_callback(f"Extracted: {ba2_path.name}")
            
            self.logger.info(f"Extracted BA2 archive to: {output_dir}")
            return output_dir
            
        except subprocess.TimeoutExpired:
            raise Archive2Error(
                message="Operation timed out after 10 minutes",
                operation="extract",
                archive_path=str(ba2_path),
            )

    def _parse_error(self, stderr: str, stdout: str) -> str:
        """Parse Archive2 output to provide user-friendly error messages."""
        combined = f"{stderr} {stdout}".lower()
        
        if "access" in combined and "denied" in combined:
            return "Access denied - file may be in use or needs Administrator privileges"
        elif "disk" in combined and ("full" in combined or "space" in combined):
            return "Insufficient disk space"
        elif "not found" in combined or "cannot find" in combined:
            return "Source file or directory not found"
        elif "corrupt" in combined or "invalid" in combined:
            return "Archive appears corrupted or invalid"
        elif stderr.strip():
            return stderr.strip()
        elif stdout.strip():
            return stdout.strip()
        else:
            return "Unknown error"

