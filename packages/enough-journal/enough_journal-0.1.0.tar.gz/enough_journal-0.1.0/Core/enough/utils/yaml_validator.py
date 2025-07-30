"""YAML validator for exercise files."""
from typing import Dict, List, Any, Optional
import re
from pathlib import Path
import yaml

class ValidationError(Exception):
    """Raised when validation fails."""
    pass

def validate_prompt_id(prompt_id: str) -> bool:
    """Validate prompt ID follows p_XXX format."""
    return bool(re.match(r'^p_\d{3}$', prompt_id))

def validate_frequency(frequency: Dict[str, Any]) -> List[str]:
    """Validate frequency settings."""
    errors = []
    valid_days = range(1, 8)  # 1-7 for days of week
    valid_weeks = range(1, 53)  # 1-52 weeks
    valid_months = range(1, 13)  # 1-12 months

    if 'days' in frequency:
        if not all(d in valid_days for d in frequency['days']):
            errors.append("Days must be between 1 and 7")
            
    if 'weekly' in frequency:
        if not all(w > 0 for w in frequency['weekly']):
            errors.append("Weekly intervals must be positive numbers")
            
    if 'monthly' in frequency:
        if not all(m > 0 for m in frequency['monthly']):
            errors.append("Monthly intervals must be positive numbers")
            
    if 'months' in frequency:
        if not all(m in valid_months for m in frequency['months']):
            errors.append("Months must be between 1 and 12")
            
    return errors

def validate_exercise_file(file_path: Path) -> List[str]:
    """Validate an exercise YAML file."""
    errors = []
    
    try:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
            
        # Required fields
        if 'name' not in data:
            errors.append("Missing required field: name")
            
        if 'frequency' not in data:
            errors.append("Missing required field: frequency")
        elif not isinstance(data['frequency'], str):
            if isinstance(data['frequency'], dict):
                errors.extend(validate_frequency(data['frequency']))
            else:
                errors.append("Frequency must be a string or dictionary")
                
        if 'answers_required' not in data:
            errors.append("Missing required field: answers_required")
            
        # Validate prompts
        if 'prompts' not in data:
            errors.append("Missing required field: prompts")
        else:
            prompts = data['prompts']
            prompt_ids = []
            
            for prompt_id, prompt_data in prompts.items():
                # Validate prompt ID format
                if not validate_prompt_id(prompt_id):
                    errors.append(f"Invalid prompt ID format: {prompt_id}")
                prompt_ids.append(prompt_id)
                
                # Validate prompt has required fields
                if 'prompt' not in prompt_data:
                    errors.append(f"Missing prompt text for {prompt_id}")
                    
                # Validate follow-up references
                if 'follow_up' in prompt_data:
                    follow_up = prompt_data['follow_up']
                    if not validate_prompt_id(follow_up):
                        errors.append(f"Invalid follow-up ID format in {prompt_id}: {follow_up}")
                        
            # Validate prompt ID sequence
            expected_ids = [f"p_{str(i).zfill(3)}" for i in range(len(prompt_ids))]
            if sorted(prompt_ids) != expected_ids:
                errors.append("Prompt IDs must start at p_000 and increment sequentially")
                
        return errors
        
    except yaml.YAMLError as e:
        return [f"Invalid YAML format: {str(e)}"]
    except Exception as e:
        return [f"Validation error: {str(e)}"] 