"""ESM/ESL plugin generator for Fallout 4."""

import logging
import struct
from dataclasses import dataclass, field
from enum import IntFlag
from pathlib import Path
from typing import BinaryIO, Optional

logger = logging.getLogger(__name__)


class RecordFlags(IntFlag):
    """Record header flags."""
    MASTER = 0x00000001  # ESM flag
    LOCALIZED = 0x00000080  # Uses localized strings
    LIGHT = 0x00000200  # ESL flag (FO4 1.10.163+)
    COMPRESSED = 0x00040000  # Record data is compressed


class GroupType(IntFlag):
    """GRUP record types."""
    TOP = 0  # Top-level group
    WORLD_CHILDREN = 1
    INTERIOR_CELL_BLOCK = 2
    INTERIOR_CELL_SUBBLOCK = 3
    EXTERIOR_CELL_BLOCK = 4
    EXTERIOR_CELL_SUBBLOCK = 5
    CELL_CHILDREN = 6
    TOPIC_CHILDREN = 7
    CELL_PERSISTENT_CHILDREN = 8
    CELL_TEMPORARY_CHILDREN = 9


@dataclass
class Record:
    """Base record structure."""
    
    type: bytes  # 4-byte record type
    data_size: int
    flags: int
    form_id: int
    timestamp: int = 0
    version_control: int = 0
    internal_version: int = 44  # FO4 version
    unknown: int = 0
    data: bytes = b""


@dataclass
class Subrecord:
    """Subrecord structure within a record."""
    
    type: bytes  # 4-byte subrecord type
    data: bytes


@dataclass
class PluginInfo:
    """Plugin metadata."""
    
    name: str
    author: str = "FO3 Audio Repository Builder"
    description: str = "Fallout 3 audio files for Fallout 4"
    master_files: list[str] = field(default_factory=list)


class PluginGenerator:
    """Generate Fallout 4 ESM/ESL plugins."""
    
    # Record type signatures
    TES4 = b"TES4"  # Plugin header
    GRUP = b"GRUP"  # Group
    GMST = b"GMST"  # Game setting
    SNDR = b"SNDR"  # Sound descriptor
    SOUN = b"SOUN"  # Sound marker
    MUSC = b"MUSC"  # Music type
    
    def __init__(self, plugin_name: str, as_esl: bool = True) -> None:
        """
        Initialize the plugin generator.
        
        Args:
            plugin_name: Name of the plugin (without extension)
            as_esl: Whether to flag the plugin as ESL (light plugin)
        """
        self.logger = logging.getLogger(__name__)
        self.plugin_name = plugin_name
        self.as_esl = as_esl
        self.records: list[Record] = []
        self.next_form_id = 0x800  # Start form IDs at 0x800 for ESL range
        
        # Plugin info
        self.info = PluginInfo(
            name=plugin_name,
            master_files=["Fallout4.esm"],
        )
    
    def _get_next_form_id(self) -> int:
        """Get the next available form ID."""
        form_id = self.next_form_id
        self.next_form_id += 1
        return form_id
    
    def add_sound_descriptor(
        self,
        editor_id: str,
        sound_files: list[str],
        category: str = "AudioCategoryWPNFire",
    ) -> int:
        """
        Add a sound descriptor record.
        
        Args:
            editor_id: Editor ID for the record
            sound_files: List of sound file paths (relative to Data/)
            category: Sound category
            
        Returns:
            Form ID of the created record
        """
        form_id = self._get_next_form_id()
        
        # Build subrecords
        subrecords: list[Subrecord] = []
        
        # EDID - Editor ID
        edid_data = editor_id.encode("utf-8") + b"\x00"
        subrecords.append(Subrecord(b"EDID", edid_data))
        
        # CNAM - Category (simplified - just use form ID placeholder)
        # In a real implementation, this would reference actual category form IDs
        subrecords.append(Subrecord(b"CNAM", struct.pack("<I", 0)))
        
        # ANAM - Sound files
        for sound_file in sound_files:
            file_data = sound_file.encode("utf-8") + b"\x00"
            subrecords.append(Subrecord(b"ANAM", file_data))
        
        # Build record data
        record_data = self._build_subrecords(subrecords)
        
        record = Record(
            type=self.SNDR,
            data_size=len(record_data),
            flags=0,
            form_id=form_id,
            data=record_data,
        )
        
        self.records.append(record)
        self.logger.debug(f"Added sound descriptor: {editor_id} (FormID: {form_id:08X})")
        
        return form_id
    
    def add_music_track(
        self,
        editor_id: str,
        music_file: str,
        loop: bool = True,
    ) -> int:
        """
        Add a music track record.
        
        Args:
            editor_id: Editor ID for the record
            music_file: Path to the music file (relative to Data/)
            loop: Whether the track should loop
            
        Returns:
            Form ID of the created record
        """
        form_id = self._get_next_form_id()
        
        subrecords: list[Subrecord] = []
        
        # EDID - Editor ID
        edid_data = editor_id.encode("utf-8") + b"\x00"
        subrecords.append(Subrecord(b"EDID", edid_data))
        
        # FNAM - Flags
        flags = 0x01 if loop else 0x00
        subrecords.append(Subrecord(b"FNAM", struct.pack("<I", flags)))
        
        # ANAM - Music file
        file_data = music_file.encode("utf-8") + b"\x00"
        subrecords.append(Subrecord(b"ANAM", file_data))
        
        record_data = self._build_subrecords(subrecords)
        
        record = Record(
            type=self.MUSC,
            data_size=len(record_data),
            flags=0,
            form_id=form_id,
            data=record_data,
        )
        
        self.records.append(record)
        self.logger.debug(f"Added music track: {editor_id} (FormID: {form_id:08X})")
        
        return form_id
    
    def _build_subrecords(self, subrecords: list[Subrecord]) -> bytes:
        """Build binary data from subrecords."""
        data = b""
        for sr in subrecords:
            data += sr.type
            data += struct.pack("<H", len(sr.data))
            data += sr.data
        return data
    
    def _build_tes4_record(self) -> Record:
        """Build the TES4 header record."""
        subrecords: list[Subrecord] = []
        
        # HEDR - Header
        hedr_data = struct.pack("<f", 0.95)  # Version
        hedr_data += struct.pack("<I", len(self.records))  # Record count
        hedr_data += struct.pack("<I", self.next_form_id)  # Next object ID
        subrecords.append(Subrecord(b"HEDR", hedr_data))
        
        # CNAM - Author
        author_data = self.info.author.encode("utf-8") + b"\x00"
        subrecords.append(Subrecord(b"CNAM", author_data))
        
        # SNAM - Description
        desc_data = self.info.description.encode("utf-8") + b"\x00"
        subrecords.append(Subrecord(b"SNAM", desc_data))
        
        # MAST/DATA - Master files
        for master in self.info.master_files:
            master_data = master.encode("utf-8") + b"\x00"
            subrecords.append(Subrecord(b"MAST", master_data))
            subrecords.append(Subrecord(b"DATA", struct.pack("<Q", 0)))
        
        # INTV - Internal version
        subrecords.append(Subrecord(b"INTV", struct.pack("<I", 1)))
        
        record_data = self._build_subrecords(subrecords)
        
        # Set flags for ESM and optionally ESL
        flags = RecordFlags.MASTER
        if self.as_esl:
            flags |= RecordFlags.LIGHT
        
        return Record(
            type=self.TES4,
            data_size=len(record_data),
            flags=int(flags),
            form_id=0,
            data=record_data,
        )
    
    def _write_record(self, f: BinaryIO, record: Record) -> None:
        """Write a record to the file."""
        f.write(record.type)
        f.write(struct.pack("<I", record.data_size))
        f.write(struct.pack("<I", record.flags))
        f.write(struct.pack("<I", record.form_id))
        f.write(struct.pack("<H", record.timestamp))
        f.write(struct.pack("<H", record.version_control))
        f.write(struct.pack("<H", record.internal_version))
        f.write(struct.pack("<H", record.unknown))
        f.write(record.data)
    
    def _write_group(
        self,
        f: BinaryIO,
        group_label: bytes,
        records: list[Record],
        group_type: int = 0,
    ) -> None:
        """Write a GRUP record."""
        # Calculate group size (header + all record sizes)
        group_size = 24  # GRUP header size
        for record in records:
            group_size += 24 + record.data_size  # Record header + data
        
        f.write(self.GRUP)
        f.write(struct.pack("<I", group_size))
        f.write(group_label)  # 4 bytes
        f.write(struct.pack("<I", group_type))
        f.write(struct.pack("<H", 0))  # Timestamp
        f.write(struct.pack("<H", 0))  # Version control
        f.write(struct.pack("<I", 0))  # Unknown
        
        for record in records:
            self._write_record(f, record)
    
    def generate(self, output_path: Path) -> Path:
        """
        Generate the plugin file.
        
        Args:
            output_path: Path for the output file (should end in .esm)
            
        Returns:
            Path to the created plugin
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Generating plugin: {output_path}")
        
        with open(output_path, "wb") as f:
            # Write TES4 header
            tes4 = self._build_tes4_record()
            self._write_record(f, tes4)
            
            # Group records by type
            sndr_records = [r for r in self.records if r.type == self.SNDR]
            musc_records = [r for r in self.records if r.type == self.MUSC]
            
            # Write SNDR group if any
            if sndr_records:
                self._write_group(f, self.SNDR, sndr_records)
            
            # Write MUSC group if any
            if musc_records:
                self._write_group(f, self.MUSC, musc_records)
        
        self.logger.info(
            f"Created plugin: {output_path} "
            f"({len(self.records)} records, ESL={self.as_esl})"
        )
        
        return output_path
    
    def generate_from_audio_files(
        self,
        audio_files: list[Path],
        base_path: Path,
        output_path: Path,
    ) -> Path:
        """
        Generate a plugin from a list of audio files.
        
        Args:
            audio_files: List of audio file paths
            base_path: Base path to make paths relative to
            output_path: Path for the output plugin
            
        Returns:
            Path to the created plugin
        """
        for audio_file in audio_files:
            # Create editor ID from filename
            editor_id = f"FO3Audio_{audio_file.stem}"
            editor_id = "".join(c if c.isalnum() else "_" for c in editor_id)
            
            # Get relative path for the sound file
            try:
                relative_path = audio_file.relative_to(base_path)
            except ValueError:
                relative_path = audio_file.name
            
            sound_path = str(relative_path).replace("/", "\\")
            
            # Determine if this is music or a sound effect
            if "music" in str(audio_file).lower():
                self.add_music_track(editor_id, sound_path)
            else:
                self.add_sound_descriptor(editor_id, [sound_path])
        
        return self.generate(output_path)


def create_audio_plugin(
    plugin_name: str,
    audio_dir: Path,
    output_dir: Path,
    as_esl: bool = True,
) -> Path:
    """
    Convenience function to create an audio plugin.
    
    Args:
        plugin_name: Name for the plugin (without extension)
        audio_dir: Directory containing audio files
        output_dir: Output directory for the plugin
        as_esl: Whether to flag as ESL
        
    Returns:
        Path to the created plugin
    """
    generator = PluginGenerator(plugin_name, as_esl=as_esl)
    
    # Find all audio files
    audio_extensions = [".xwm", ".wav", ".fuz", ".mp3"]
    audio_files: list[Path] = []
    
    for ext in audio_extensions:
        audio_files.extend(audio_dir.rglob(f"*{ext}"))
    
    logger.info(f"Found {len(audio_files)} audio files")
    
    output_path = output_dir / f"{plugin_name}.esm"
    return generator.generate_from_audio_files(audio_files, audio_dir, output_path)
