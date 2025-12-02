"""Repository builder for organizing Fallout 4 audio files."""

import json
import logging
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class AudioFile:
    """Represents an audio file in the repository."""

    path: Path
    original_path: Optional[Path] = None
    form_id: Optional[str] = None
    voice_type: Optional[str] = None
    dialogue_text: Optional[str] = None


@dataclass
class Repository:
    """Audio repository structure."""

    name: str
    version: str
    files: list[AudioFile] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)


class RepositoryBuilder:
    """Build and organize a Fallout 4 audio repository."""

    # Fallout 4 audio directory structure
    FO4_SOUND_PATH = Path("Sound/Voice")

    def __init__(self, output_dir: Path) -> None:
        """
        Initialize the repository builder.

        Args:
            output_dir: Base directory for the repository
        """
        self.logger = logging.getLogger(__name__)
        self.output_dir = output_dir
        self.repository = Repository(
            name="FO3 Audio Repository",
            version="1.0.0",
        )

    def build(
        self,
        audio_files: list[Path],
        plugin_name: str = "Fallout3Audio.esp",
    ) -> Path:
        """
        Build the audio repository from converted files.

        Args:
            audio_files: List of converted audio file paths
            plugin_name: Name of the target ESP/ESM plugin

        Returns:
            Path to the built repository
        """
        self.logger.info(f"Building repository with {len(audio_files)} files")

        # Create repository structure
        repo_dir = self.output_dir / "repository"
        voice_dir = repo_dir / self.FO4_SOUND_PATH / plugin_name

        voice_dir.mkdir(parents=True, exist_ok=True)

        # Organize files by voice type
        organized_files = self._organize_by_voice_type(audio_files)

        # Copy files to repository
        for voice_type, files in organized_files.items():
            voice_type_dir = voice_dir / voice_type
            voice_type_dir.mkdir(parents=True, exist_ok=True)

            for audio_file in files:
                dest_path = voice_type_dir / audio_file.name
                shutil.copy2(audio_file, dest_path)

                self.repository.files.append(
                    AudioFile(
                        path=dest_path.relative_to(repo_dir),
                        original_path=audio_file,
                        voice_type=voice_type,
                    )
                )

        # Generate metadata
        self._generate_metadata(repo_dir)

        self.logger.info(f"Repository built at: {repo_dir}")
        return repo_dir

    def _organize_by_voice_type(
        self,
        audio_files: list[Path],
    ) -> dict[str, list[Path]]:
        """
        Organize audio files by voice type.

        Fallout 3 voice files follow naming conventions like:
        Sound/Voice/Fallout3.esm/MaleAdult01/DialogueGeneric_00012345_1.fuz

        Args:
            audio_files: List of audio file paths

        Returns:
            Dictionary mapping voice type to list of files
        """
        organized: dict[str, list[Path]] = {}

        for audio_file in audio_files:
            # Try to extract voice type from path
            voice_type = self._detect_voice_type(audio_file)

            if voice_type not in organized:
                organized[voice_type] = []

            organized[voice_type].append(audio_file)

        self.logger.debug(f"Organized into {len(organized)} voice types")
        return organized

    def _detect_voice_type(self, audio_path: Path) -> str:
        """
        Detect the voice type from the file path.

        Args:
            audio_path: Path to the audio file

        Returns:
            Voice type string
        """
        # Common Fallout 3 voice types
        voice_types = [
            "MaleAdult01",
            "MaleAdult02",
            "MaleAdult03",
            "MaleAdult04",
            "MaleAdult05",
            "MaleChild01",
            "MaleOld01",
            "MaleOld02",
            "FemaleAdult01",
            "FemaleAdult02",
            "FemaleAdult03",
            "FemaleAdult04",
            "FemaleAdult05",
            "FemaleChild01",
            "FemaleOld01",
            "FemaleOld02",
            "RobotMrHandy",
            "RobotProtectron",
            "SuperMutant01",
            "Ghoul01",
        ]

        # Check if any voice type is in the path
        path_str = str(audio_path).lower()
        for voice_type in voice_types:
            if voice_type.lower() in path_str:
                return voice_type

        # Default to generic
        return "Generic"

    def _generate_metadata(self, repo_dir: Path) -> None:
        """
        Generate repository metadata file.

        Args:
            repo_dir: Repository directory
        """
        metadata: dict[str, Any] = {
            "name": self.repository.name,
            "version": self.repository.version,
            "file_count": len(self.repository.files),
            "voice_types": list(
                set(f.voice_type for f in self.repository.files if f.voice_type)
            ),
            "files": [
                {
                    "path": str(f.path),
                    "voice_type": f.voice_type,
                    "form_id": f.form_id,
                }
                for f in self.repository.files
            ],
        }

        metadata_path = repo_dir / "repository.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        self.logger.info(f"Generated metadata: {metadata_path}")

    def create_fomod_installer(self, repo_dir: Path) -> Path:
        """
        Create a FOMOD installer for the audio repository.

        Args:
            repo_dir: Repository directory

        Returns:
            Path to the FOMOD directory
        """
        fomod_dir = repo_dir / "fomod"
        fomod_dir.mkdir(parents=True, exist_ok=True)

        # Create info.xml
        info_xml = """<?xml version="1.0" encoding="UTF-8"?>
<fomod>
    <Name>Fallout 3 Audio for Fallout 4</Name>
    <Author>FO3 Audio Repository Builder</Author>
    <Version>1.0.0</Version>
    <Description>Audio files from Fallout 3, converted for use in Fallout 4.</Description>
    <Website></Website>
</fomod>
"""
        (fomod_dir / "info.xml").write_text(info_xml, encoding="utf-8")

        # Create ModuleConfig.xml
        module_config = """<?xml version="1.0" encoding="UTF-8"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="http://qconsulting.ca/fo3/ModConfig5.0.xsd">
    <moduleName>Fallout 3 Audio for Fallout 4</moduleName>
    <installSteps order="Explicit">
        <installStep name="Install">
            <optionalFileGroups order="Explicit">
                <group name="Audio Files" type="SelectExactlyOne">
                    <plugins order="Explicit">
                        <plugin name="Install All Audio">
                            <description>Installs all Fallout 3 audio files.</description>
                            <files>
                                <folder source="Sound" destination="Sound" priority="0"/>
                            </files>
                            <typeDescriptor>
                                <type name="Recommended"/>
                            </typeDescriptor>
                        </plugin>
                    </plugins>
                </group>
            </optionalFileGroups>
        </installStep>
    </installSteps>
</config>
"""
        (fomod_dir / "ModuleConfig.xml").write_text(module_config, encoding="utf-8")

        self.logger.info(f"Created FOMOD installer: {fomod_dir}")
        return fomod_dir

    def validate_repository(self, repo_dir: Path) -> bool:
        """
        Validate the repository structure and files.

        Args:
            repo_dir: Repository directory

        Returns:
            True if valid, False otherwise
        """
        self.logger.info("Validating repository...")

        issues: list[str] = []

        # Check metadata file
        metadata_path = repo_dir / "repository.json"
        if not metadata_path.exists():
            issues.append("Missing repository.json")

        # Check Sound directory
        sound_dir = repo_dir / "Sound"
        if not sound_dir.exists():
            issues.append("Missing Sound directory")

        # Validate audio files
        audio_files = list(repo_dir.rglob("*.xwm")) + list(repo_dir.rglob("*.fuz"))
        for audio_file in audio_files:
            if audio_file.stat().st_size == 0:
                issues.append(f"Empty file: {audio_file}")

        if issues:
            for issue in issues:
                self.logger.warning(f"Validation issue: {issue}")
            return False

        self.logger.info("Repository validation passed")
        return True
