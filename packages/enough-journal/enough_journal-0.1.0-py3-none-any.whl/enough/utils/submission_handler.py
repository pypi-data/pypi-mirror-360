"""Handles saving and loading exercise submissions."""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import yaml

class SubmissionHandler:
    """Handles exercise submissions and responses."""
    
    def __init__(self, submissions_dir: Path):
        """Initialize submission handler.
        
        Args:
            submissions_dir: Root directory for submissions
        """
        self.submissions_dir = submissions_dir
        
    def get_submission_path(self, exercise_name: str, date: datetime, number: int = 1) -> Path:
        """Get path for a submission file.
        
        Args:
            exercise_name: Name of the exercise
            date: Date of submission
            number: Submission number for the day (defaults to 1)
        """
        # Convert exercise name to folder name
        folder_name = f"{exercise_name.replace(' ', '_')}_Submissions"
        exercise_dir = self.submissions_dir / folder_name
        exercise_dir.mkdir(parents=True, exist_ok=True)
        
        # Create filename with date and number
        filename = f"{date.strftime('%Y_%m_%d')}_{number}.yaml"
        return exercise_dir / filename
        
    def get_next_submission_number(self, exercise_name: str, date: datetime) -> int:
        """Get the next available submission number for the day."""
        folder_name = f"{exercise_name.replace(' ', '_')}_Submissions"
        exercise_dir = self.submissions_dir / folder_name
        
        if not exercise_dir.exists():
            return 1
            
        date_prefix = date.strftime('%Y_%m_%d')
        existing = list(exercise_dir.glob(f"{date_prefix}_*.yaml"))
        
        if not existing:
            return 1
            
        numbers = [int(p.stem.split('_')[-1]) for p in existing]
        return max(numbers) + 1
        
    def save_submission(self, exercise_name: str, responses: Dict[str, Any]) -> Path:
        """Save a submission.
        
        Args:
            exercise_name: Name of the exercise
            responses: Dictionary containing responses
            
        Returns:
            Path to saved submission file
        """
        now = datetime.now()
        number = self.get_next_submission_number(exercise_name, now)
        path = self.get_submission_path(exercise_name, now, number)
        
        submission_data = {
            'exercise': exercise_name,
            'timestamp': now.isoformat(),
            'responses': responses
        }
        
        with open(path, 'w') as f:
            yaml.safe_dump(submission_data, f)
            
        return path
        
    def load_submissions_for_week(self, exercise_name: str, start_date: datetime) -> List[Dict[str, Any]]:
        """Load all submissions for a week.
        
        Args:
            exercise_name: Name of the exercise
            start_date: Start date of the week
            
        Returns:
            List of submission data dictionaries
        """
        folder_name = f"{exercise_name.replace(' ', '_')}_Submissions"
        exercise_dir = self.submissions_dir / folder_name
        
        if not exercise_dir.exists():
            return []
            
        submissions = []
        for i in range(7):  # Check each day of the week
            date = start_date + timedelta(days=i)
            date_prefix = date.strftime('%Y_%m_%d')
            
            # Get all submissions for this day
            day_files = exercise_dir.glob(f"{date_prefix}_*.yaml")
            
            for file_path in day_files:
                with open(file_path, 'r') as f:
                    submission = yaml.safe_load(f)
                    submissions.append(submission)
                    
        return submissions
        
    def group_responses_by_prompt(self, submissions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group responses by prompt ID.
        
        Args:
            submissions: List of submission data
            
        Returns:
            Dictionary mapping prompt IDs to lists of responses
        """
        grouped = {}
        
        for submission in submissions:
            for prompt_id, response_data in submission['responses'].items():
                if prompt_id not in grouped:
                    grouped[prompt_id] = []
                grouped[prompt_id].append({
                    'timestamp': submission['timestamp'],
                    'response': response_data
                })
                
        return grouped
        
    def save_review(self, exercise_name: str, review_data: Dict[str, Any]) -> Path:
        """Save a weekly review.
        
        Args:
            exercise_name: Name of the exercise
            review_data: Review responses and insights
            
        Returns:
            Path to saved review file
        """
        now = datetime.now()
        folder_name = f"{exercise_name.replace(' ', '_')}_Submissions"
        exercise_dir = self.submissions_dir / folder_name
        
        filename = f"{now.strftime('%Y_%m_%d')}_review.yaml"
        path = exercise_dir / filename
        
        review_data['timestamp'] = now.isoformat()
        review_data['exercise'] = exercise_name
        
        with open(path, 'w') as f:
            yaml.safe_dump(review_data, f)
            
        return path 