"""Exercise manager module for handling sentence completion exercises."""
from typing import Dict, List, Optional
import os
from datetime import datetime
from ..utils.encryption import encrypt_data, decrypt_data
from ..utils.file_handler import FileHandler
from ..utils.exceptions import (
    SentenceCompletionError,
    ValidationError,
    BackupError
)
from ..utils.logger import logger

class ExerciseManager:
    """Manages sentence completion exercises and responses."""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize the exercise manager.
        
        Args:
            data_dir: Directory to store exercise data
        """
        self.data_dir = data_dir
        self.file_handler = FileHandler(data_dir)
        
        try:
            self.exercises = self.file_handler.load_exercises()
            logger.info("Successfully loaded exercise data")
        except Exception as e:
            logger.error(f"Failed to load exercises: {str(e)}")
            raise SentenceCompletionError("Failed to initialize exercise manager") from e
        
    def get_daily_exercises(self, week: int, day: int) -> List[str]:
        """Get exercises for a specific day.
        
        Args:
            week: Week number (1-30)
            day: Day number (1-5)
            
        Returns:
            List of exercise prompts
            
        Raises:
            ValidationError: If week or day numbers are invalid
        """
        if not 1 <= week <= 30:
            logger.error(f"Invalid week number: {week}")
            raise ValidationError("Week must be between 1 and 30")
            
        if not 1 <= day <= 5:
            logger.error(f"Invalid day number: {day}")
            raise ValidationError("Day must be between 1 and 5")
            
        exercises = self.exercises.get(week, [])
        if not exercises:
            logger.warning(f"No exercises found for week {week}")
            
        return exercises
        
    def save_responses(self, week: int, day: int, responses: Dict[str, List[str]]) -> None:
        """Save user responses for a specific day.
        
        Args:
            week: Week number
            day: Day number
            responses: Dictionary mapping prompts to lists of responses
            
        Raises:
            SentenceCompletionError: If saving responses fails
        """
        try:
            filename = f"Week{week}_Day{day}_exercises.txt"
            encrypted_data = encrypt_data(str(responses))
            self.file_handler.save_responses(filename, encrypted_data)
            logger.info(f"Successfully saved responses for Week {week} Day {day}")
            
        except Exception as e:
            logger.error(f"Failed to save responses: {str(e)}")
            raise SentenceCompletionError("Failed to save responses") from e
        
    def compile_week(self, week: int) -> Dict[str, List[str]]:
        """Compile all responses for a specific week.
        
        Args:
            week: Week number
            
        Returns:
            Dictionary mapping prompts to lists of responses
            
        Raises:
            SentenceCompletionError: If compiling responses fails
        """
        try:
            compiled_data = {}
            
            for day in range(1, 6):
                filename = f"Week{week}_Day{day}_exercises.txt"
                if os.path.exists(os.path.join(self.data_dir, filename)):
                    encrypted_data = self.file_handler.load_responses(filename)
                    day_data = eval(decrypt_data(encrypted_data))  # Safe since we encrypted it
                    for prompt, responses in day_data.items():
                        compiled_data.setdefault(prompt, []).extend(responses)
                        
            if not compiled_data:
                logger.warning(f"No responses found for week {week}")
                
            return compiled_data
            
        except Exception as e:
            logger.error(f"Failed to compile week {week}: {str(e)}")
            raise SentenceCompletionError(f"Failed to compile responses for week {week}") from e
        
    def save_assessment(self, week: int, assessment: Dict[str, List[str]]) -> None:
        """Save weekly assessment responses.
        
        Args:
            week: Week number
            assessment: Dictionary mapping prompts to assessment responses
            
        Raises:
            SentenceCompletionError: If saving assessment fails
        """
        try:
            filename = f"Week{week}_assessment.txt"
            encrypted_data = encrypt_data(str(assessment))
            self.file_handler.save_responses(filename, encrypted_data)
            logger.info(f"Successfully saved assessment for Week {week}")
            
        except Exception as e:
            logger.error(f"Failed to save assessment: {str(e)}")
            raise SentenceCompletionError("Failed to save assessment") from e
        
    def backup_data(self) -> None:
        """Create a backup of all response data.
        
        Raises:
            BackupError: If creating backup fails
        """
        try:
            backup_dir = os.path.join(self.data_dir, "backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"backup_{timestamp}.zip")
            
            self.file_handler.create_backup(backup_file)
            logger.info(f"Successfully created backup: {backup_file}")
            
        except Exception as e:
            logger.error(f"Failed to create backup: {str(e)}")
            raise BackupError("Failed to create data backup") from e 