"""Manages weekly reviews of exercise submissions."""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import yaml

from ..utils.submission_handler import SubmissionHandler

class ReviewManager:
    """Manages weekly reviews of exercise submissions."""
    
    def __init__(self, exercise_file: Path, submissions_dir: Path):
        """Initialize review manager.
        
        Args:
            exercise_file: Path to exercise YAML file
            submissions_dir: Root directory for submissions
        """
        self.exercise_file = exercise_file
        self.submission_handler = SubmissionHandler(submissions_dir)
        
        with open(exercise_file, 'r') as f:
            self.exercise_data = yaml.safe_load(f)
            
    def get_week_start(self, date: Optional[datetime] = None) -> datetime:
        """Get the start of the week (Monday) for a given date."""
        if date is None:
            date = datetime.now()
        return date - timedelta(days=date.weekday())
        
    def run_weekly_review(self) -> Dict[str, Any]:
        """Run weekly review process.
        
        Returns:
            Dictionary containing review data and responses
        """
        # Get all submissions for this week
        week_start = self.get_week_start()
        submissions = self.submission_handler.load_submissions_for_week(
            self.exercise_data['name'],
            week_start
        )
        
        if not submissions:
            return {'error': 'No submissions found for this week'}
            
        # Group responses by prompt ID
        grouped_responses = self.submission_handler.group_responses_by_prompt(submissions)
        
        review_data = {
            'week_start': week_start.isoformat(),
            'prompt_reviews': {},
            'insights': []
        }
        
        # Review each prompt's responses
        for prompt_id in sorted(grouped_responses.keys()):
            responses = grouped_responses[prompt_id]
            prompt_text = self.exercise_data['prompts'][prompt_id]['prompt']
            
            print(f"\nReviewing responses for: {prompt_text}")
            print("\nYour responses this week:")
            
            for resp in responses:
                timestamp = datetime.fromisoformat(resp['timestamp'])
                print(f"\n{timestamp.strftime('%A')}:")
                for answer in resp['response']['answers']:
                    print(f"- {answer['text']}")
                    
            # Get reflection on this prompt's responses
            print("\nReflection:")
            reflection = input("What patterns or insights do you notice in these responses? ")
            
            review_data['prompt_reviews'][prompt_id] = {
                'responses': responses,
                'reflection': reflection
            }
            
        # Final insights
        print("\nOverall Review")
        print("Based on all your responses this week:")
        
        insights = []
        while True:
            insight = input("Enter an insight or observation (or press Enter to finish): ")
            if not insight:
                break
            insights.append(insight)
            
        review_data['insights'] = insights
        
        # Action items
        actions = []
        print("\nAction Planning")
        while True:
            action = input("Enter an action item for next week (or press Enter to finish): ")
            if not action:
                break
            actions.append(action)
            
        review_data['actions'] = actions
        
        # Save the review
        self.submission_handler.save_review(
            self.exercise_data['name'],
            review_data
        )
        
        return review_data
        
    def get_last_review(self) -> Optional[Dict[str, Any]]:
        """Get the most recent review data."""
        folder_name = f"{self.exercise_data['name'].replace(' ', '_')}_Submissions"
        exercise_dir = self.submission_handler.submissions_dir / folder_name
        
        if not exercise_dir.exists():
            return None
            
        review_files = list(exercise_dir.glob('*_review.yaml'))
        if not review_files:
            return None
            
        latest_review = max(review_files, key=lambda p: p.stem.split('_')[0])
        
        with open(latest_review, 'r') as f:
            return yaml.safe_load(f) 