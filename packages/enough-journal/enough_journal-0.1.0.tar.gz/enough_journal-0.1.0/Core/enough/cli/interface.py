"""Command line interface for the journal system."""
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import click
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table

from ..core.review_manager import ReviewManager
from ..utils.submission_handler import SubmissionHandler
from ..utils.yaml_validator import validate_exercise_file

console = Console()

def load_exercise(exercise_path: Path) -> Dict[str, Any]:
    """Load and validate exercise file."""
    errors = validate_exercise_file(exercise_path)
    if errors:
        console.print("[red]Exercise file validation failed:[/red]")
        for error in errors:
            console.print(f"[red]- {error}[/red]")
        raise click.Abort()
        
    with open(exercise_path, 'r') as f:
        return yaml.safe_load(f)

@click.group()
def cli():
    """Personal Growth Journal CLI."""
    pass

@cli.command()
@click.argument('exercise_file', type=click.Path(exists=True))
def start(exercise_file):
    """Start a journaling session."""
    exercise_path = Path(exercise_file)
    exercise_data = load_exercise(exercise_path)
    
    submission_handler = SubmissionHandler(Path("Submissions"))
    
    responses = {}
    for prompt_id, prompt_data in exercise_data['prompts'].items():
        console.print(f"\n[bold]{prompt_data['prompt']}[/bold]")
        
        answers = []
        answers_required = prompt_data.get('answers_required', 
                                         exercise_data.get('answers_required', 1))
        
        if answers_required == "submit":
            console.print("Enter responses (press Enter twice to finish):")
            empty_lines = 0
            while empty_lines < 2:
                answer = Prompt.ask(f"{len(answers) + 1}")
                if answer.strip():
                    answers.append({
                        'text': answer,
                        'word_count': len(answer.split()),
                        'time_taken': 0  # TODO: Implement timing
                    })
                    empty_lines = 0
                else:
                    empty_lines += 1
        else:
            console.print(f"Enter {answers_required} responses:")
            for i in range(answers_required):
                answer = Prompt.ask(f"{i + 1}")
                answers.append({
                    'text': answer,
                    'word_count': len(answer.split()),
                    'time_taken': 0  # TODO: Implement timing
                })
                
        responses[prompt_id] = {
            'tags': prompt_data.get('tags', []),
            'answers': answers
        }
        
        # Handle follow-up prompts
        if 'follow_up' in prompt_data:
            follow_up_id = prompt_data['follow_up']
            if follow_up_id in exercise_data['prompts']:
                responses[prompt_id]['follow_up_completed'] = follow_up_id
                
                follow_up = exercise_data['prompts'][follow_up_id]
                console.print(f"\n[bold]Follow-up: {follow_up['prompt']}[/bold]")
                
                follow_up_answers = []
                follow_up_required = follow_up.get('answers_required',
                                                 exercise_data.get('answers_required', 1))
                
                for i in range(follow_up_required):
                    answer = Prompt.ask(f"{i + 1}")
                    follow_up_answers.append({
                        'text': answer,
                        'word_count': len(answer.split()),
                        'time_taken': 0
                    })
                    
                responses[follow_up_id] = {
                    'tags': follow_up.get('tags', []),
                    'answers': follow_up_answers
                }
                
    # Save submission
    submission_path = submission_handler.save_submission(
        exercise_data['name'],
        responses
    )
    
    console.print(f"\n[green]Responses saved to {submission_path}[/green]")
    
@cli.command()
@click.argument('exercise_file', type=click.Path(exists=True))
def review(exercise_file):
    """Run weekly review for an exercise."""
    exercise_path = Path(exercise_file)
    review_manager = ReviewManager(exercise_path, Path("Submissions"))
    
    if not review_manager.run_weekly_review():
        console.print("[yellow]No submissions found for this week.[/yellow]")
        return
        
    console.print("[green]Weekly review completed and saved![/green]")
    
@cli.command()
@click.argument('text')
@click.option('--tags', help='Comma-separated tags')
@click.option('--answers', type=int, help='Number of answers required')
@click.option('--min-words', type=int, help='Minimum words per answer')
def add(text, tags, answers, min_words):
    """Add a custom journal entry."""
    submission_handler = SubmissionHandler(Path("Submissions"))
    
    responses = {}
    answers_list = []
    
    if answers:
        console.print(f"Enter {answers} responses:")
        for i in range(answers):
            answer = Prompt.ask(f"{i + 1}")
            answers_list.append({
                'text': answer,
                'word_count': len(answer.split()),
                'time_taken': 0
            })
    else:
        answer = Prompt.ask("Response")
        answers_list.append({
            'text': answer,
            'word_count': len(answer.split()),
            'time_taken': 0
        })
        
    responses['custom'] = {
        'prompt': text,
        'tags': tags.split(',') if tags else [],
        'answers': answers_list
    }
    
    submission_path = submission_handler.save_submission(
        "Custom_Entries",
        responses
    )
    
    console.print(f"[green]Entry saved to {submission_path}[/green]")
    
if __name__ == '__main__':
    cli() 