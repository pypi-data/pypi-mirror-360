"""Handles scheduling of exercises based on frequency settings."""
from typing import Dict, List, Any
from datetime import datetime, timedelta
import calendar

class FrequencyHandler:
    """Handles exercise scheduling based on frequency settings."""
    
    def __init__(self, frequency_settings: Dict[str, Any]):
        """Initialize frequency handler.
        
        Args:
            frequency_settings: Dictionary containing frequency configuration
        """
        self.settings = frequency_settings
        
    def should_run_today(self, last_run: datetime = None) -> bool:
        """Check if exercise should run today based on frequency settings."""
        today = datetime.now()
        
        # Simple frequency strings
        if isinstance(self.settings, str):
            if self.settings == "daily":
                return True
            if self.settings == "weekly" and today.weekday() == 0:  # Monday
                return True
            if self.settings == "monthly" and today.day == 1:
                return True
            return False
            
        # Complex frequency settings
        if isinstance(self.settings, dict):
            # Check days of week
            if 'days' in self.settings:
                if today.weekday() + 1 not in self.settings['days']:
                    return False
                    
            # Check week intervals
            if 'weekly' in self.settings and last_run:
                weeks_diff = (today - last_run).days // 7
                if not any(weeks_diff % interval == 0 for interval in self.settings['weekly']):
                    return False
                    
            # Check month intervals
            if 'monthly' in self.settings and last_run:
                months_diff = (today.year - last_run.year) * 12 + today.month - last_run.month
                if not any(months_diff % interval == 0 for interval in self.settings['monthly']):
                    return False
                    
            # Check specific months
            if 'months' in self.settings:
                if today.month not in self.settings['months']:
                    return False
                    
            return True
            
        return False
        
    def next_run_date(self, last_run: datetime = None) -> datetime:
        """Calculate the next run date based on frequency settings."""
        if not last_run:
            last_run = datetime.now()
            
        next_date = last_run + timedelta(days=1)  # Start with tomorrow
        
        while not self.should_run_today(last_run):
            next_date += timedelta(days=1)
            
        return next_date
        
    def get_review_day(self) -> int:
        """Get the day of week for reviews (default Sunday)."""
        if isinstance(self.settings, dict) and 'review_day' in self.settings:
            return self.settings['review_day']
        return 7  # Default to Sunday
        
    def is_review_day(self) -> bool:
        """Check if today is a review day."""
        return datetime.now().weekday() + 1 == self.get_review_day() 