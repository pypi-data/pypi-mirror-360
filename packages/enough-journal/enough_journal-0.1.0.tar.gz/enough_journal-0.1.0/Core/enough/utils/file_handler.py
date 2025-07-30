"""File handling utilities for the sentence completion program."""
import os
import json
import shutil
from typing import Dict, List, Any
from pathlib import Path
from .exceptions import FileOperationError, ExportError
from .logger import logger

class FileHandler:
    """Handles file operations for the sentence completion program."""
    
    def __init__(self, data_dir: str):
        """Initialize the file handler.
        
        Args:
            data_dir: Directory to store data files
            
        Raises:
            FileOperationError: If data directory cannot be created
        """
        try:
            self.data_dir = Path(data_dir)
            self.data_dir.mkdir(exist_ok=True)
            logger.info(f"Initialized file handler with data directory: {data_dir}")
        except Exception as e:
            logger.error(f"Failed to create data directory: {str(e)}")
            raise FileOperationError("Could not create data directory") from e
        
    def load_exercises(self) -> Dict[int, List[str]]:
        """Load exercise prompts from the exercises file.
        
        Returns:
            Dictionary mapping week numbers to lists of prompts
            
        Raises:
            FileOperationError: If exercise file cannot be read
        """
        exercises_file = Path("SentenceCompletion.txt")
        if not exercises_file.exists():
            logger.error("Exercise file not found")
            raise FileOperationError("Exercise file not found")
            
        try:
            exercises = {}
            current_week = None
            
            with exercises_file.open('r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("Week"):
                        current_week = int(line.split()[1])
                        exercises[current_week] = []
                    elif line.startswith("ID") and current_week is not None:
                        exercises[current_week].append(line[4:])
                        
            logger.info("Successfully loaded exercises")
            return exercises
            
        except Exception as e:
            logger.error(f"Failed to load exercises: {str(e)}")
            raise FileOperationError("Could not read exercise file") from e
        
    def save_responses(self, filename: str, data: bytes) -> None:
        """Save encrypted response data to a file.
        
        Args:
            filename: Name of the file to save
            data: Encrypted data to save
            
        Raises:
            FileOperationError: If data cannot be saved
        """
        try:
            file_path = self.data_dir / filename
            file_path.write_bytes(data)
            logger.info(f"Successfully saved responses to {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save responses to {filename}: {str(e)}")
            raise FileOperationError(f"Could not save responses to {filename}") from e
        
    def load_responses(self, filename: str) -> bytes:
        """Load encrypted response data from a file.
        
        Args:
            filename: Name of the file to load
            
        Returns:
            bytes: Encrypted data from the file
            
        Raises:
            FileOperationError: If data cannot be loaded
        """
        try:
            file_path = self.data_dir / filename
            if not file_path.exists():
                logger.error(f"Response file not found: {filename}")
                raise FileOperationError(f"Response file not found: {filename}")
                
            data = file_path.read_bytes()
            logger.info(f"Successfully loaded responses from {filename}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to load responses from {filename}: {str(e)}")
            raise FileOperationError(f"Could not load responses from {filename}") from e
        
    def create_backup(self, backup_file: str) -> None:
        """Create a backup of all response files.
        
        Args:
            backup_file: Path to save the backup zip file
            
        Raises:
            FileOperationError: If backup cannot be created
        """
        # Create a temporary directory for organizing files
        temp_dir = self.data_dir / "temp_backup"
        temp_dir.mkdir(exist_ok=True)
        
        try:
            # Copy all response files to temp directory
            files_copied = 0
            for file in self.data_dir.glob("Week*"):
                if file.is_file():
                    shutil.copy2(file, temp_dir)
                    files_copied += 1
                    
            if files_copied == 0:
                logger.warning("No files found to backup")
                return
                
            # Create zip archive
            shutil.make_archive(
                str(backup_file).replace('.zip', ''),
                'zip',
                str(temp_dir)
            )
            
            logger.info(f"Successfully created backup with {files_copied} files")
            
        except Exception as e:
            logger.error(f"Failed to create backup: {str(e)}")
            raise FileOperationError("Could not create backup") from e
            
        finally:
            # Clean up temp directory
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.warning(f"Failed to clean up temporary backup directory: {str(e)}")
            
    def export_data(self, export_file: str) -> None:
        """Export all response data to a JSON file.
        
        Args:
            export_file: Path to save the exported JSON file
            
        Raises:
            ExportError: If data cannot be exported
        """
        try:
            export_data = {
                "version": 1,
                "responses": {}
            }
            
            # Collect all response files
            files_exported = 0
            for file in self.data_dir.glob("Week*"):
                if file.is_file():
                    week_num = int(file.name.split('_')[0].replace('Week', ''))
                    export_data["responses"][week_num] = {
                        "filename": file.name,
                        "data": self.load_responses(file.name).decode('utf-8')
                    }
                    files_exported += 1
                    
            if files_exported == 0:
                logger.warning("No files found to export")
                return
                
            # Save as JSON
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)
                
            logger.info(f"Successfully exported {files_exported} files to {export_file}")
            
        except Exception as e:
            logger.error(f"Failed to export data: {str(e)}")
            raise ExportError("Could not export data") from e 