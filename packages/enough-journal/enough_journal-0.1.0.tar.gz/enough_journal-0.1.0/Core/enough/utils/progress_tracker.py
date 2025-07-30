"""Tracks progress of exercises and submissions."""
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import yaml

class ProgressTracker:
    """Tracks exercise progress and completion."""
    
    def __init__(self, progress_file: Path):
        """Initialize progress tracker.
        
        Args:
            progress_file: Path to progress.yaml
        """
        self.progress_file = progress_file
        self.load_progress()
        
    def load_progress(self) -> None:
        """Load progress data from file."""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                self.data = yaml.safe_load(f)
        else:
            self.data = {
                'version': '1.0',
                'last_updated': datetime.now().isoformat(),
                'active_exercises': [],
                'completed_exercises': [],
                'settings': {
                    'backup_frequency': 'weekly',
                    'reminder_time': '08:00'
                }
            }
            self.save_progress()
            
    def save_progress(self) -> None:
        """Save progress data to file."""
        self.data['last_updated'] = datetime.now().isoformat()
        with open(self.progress_file, 'w') as f:
            yaml.safe_dump(self.data, f)
            
    def get_active_exercise(self, name: str) -> Optional[Dict[str, Any]]:
        """Get progress data for an active exercise."""
        for exercise in self.data['active_exercises']:
            if exercise['name'] == name:
                return exercise
        return None
        
    def start_exercise(self, name: str) -> None:
        """Start tracking a new exercise."""
        if self.get_active_exercise(name):
            return
            
        self.data['active_exercises'].append({
            'name': name,
            'started': datetime.now().isoformat(),
            'entries_completed': 0,
            'last_reflection': None
        })
        self.save_progress()
        
    def record_submission(self, exercise_name: str) -> None:
        """Record a submission for an exercise."""
        exercise = self.get_active_exercise(exercise_name)
        if exercise:
            exercise['entries_completed'] += 1
            self.save_progress()
            
    def record_review(self, exercise_name: str) -> None:
        """Record a review completion."""
        exercise = self.get_active_exercise(exercise_name)
        if exercise:
            exercise['last_reflection'] = datetime.now().isoformat()
            self.save_progress()
            
    def complete_exercise(self, name: str) -> None:
        """Mark an exercise as completed."""
        exercise = self.get_active_exercise(name)
        if exercise:
            self.data['active_exercises'].remove(exercise)
            exercise['completed'] = datetime.now().isoformat()
            self.data['completed_exercises'].append(exercise)
            self.save_progress()
            
    def get_exercise_stats(self, name: str) -> Dict[str, Any]:
        """Get statistics for an exercise."""
        exercise = self.get_active_exercise(name)
        if not exercise:
            return {}
            
        started = datetime.fromisoformat(exercise['started'])
        days_active = (datetime.now() - started).days
        
        return {
            'days_active': days_active,
            'entries_completed': exercise['entries_completed'],
            'entries_per_day': exercise['entries_completed'] / max(days_active, 1),
            'last_reflection': exercise['last_reflection']
        } 