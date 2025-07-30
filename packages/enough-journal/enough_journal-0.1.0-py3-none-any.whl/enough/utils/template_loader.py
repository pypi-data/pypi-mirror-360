"""
Template loader for journal prompts with validation.
"""
from dataclasses import dataclass
from typing import List, Optional, Union, Dict
from datetime import datetime
import yaml
from pathlib import Path
from .exceptions import FileOperationError
from .logger import logger

@dataclass
class FollowUpPrompt:
    prompt: str

@dataclass
class Prompt:
    prompt: str
    recurring: Union[str, int]  # "daily", "weekly", "monthly", "yearly" or number of days
    tags: List[str]
    min_words: Optional[int] = None
    max_time: Optional[int] = None  # in seconds
    answers_required: Optional[int] = None
    free_writing: bool = False
    follow_up: Optional[FollowUpPrompt] = None

    def validate(self) -> List[str]:
        """Validate prompt configuration."""
        errors = []
        
        # Validate recurring
        valid_recurring = ["daily", "weekly", "monthly", "yearly"]
        if isinstance(self.recurring, str) and self.recurring not in valid_recurring:
            errors.append(f"Invalid recurring value: {self.recurring}")
        elif isinstance(self.recurring, int) and self.recurring < 1:
            errors.append("Recurring days must be positive")
            
        # Validate numeric fields
        if self.min_words is not None and self.min_words < 1:
            errors.append("min_words must be positive")
        if self.max_time is not None and self.max_time < 1:
            errors.append("max_time must be positive")
        if self.answers_required is not None and self.answers_required < 1:
            errors.append("answers_required must be positive")
            
        # Validate tags
        if not self.tags:
            errors.append("At least one tag is required")
            
        return errors

@dataclass
class Section:
    name: str
    description: str
    prompts: List[Prompt]

    def validate(self) -> List[str]:
        """Validate section configuration."""
        errors = []
        
        if not self.name:
            errors.append("Section name is required")
        if not self.prompts:
            errors.append(f"Section '{self.name}' must have at least one prompt")
            
        # Validate all prompts
        for i, prompt in enumerate(self.prompts):
            prompt_errors = prompt.validate()
            if prompt_errors:
                errors.extend([f"Prompt {i+1}: {error}" for error in prompt_errors])
                
        return errors

@dataclass
class FrequencySettings:
    type: str
    settings: Dict

    def validate(self) -> List[str]:
        """Validate frequency settings."""
        errors = []
        valid_types = ["custom", "daily", "weekly", "spaced_repetition"]
        
        if self.type not in valid_types:
            errors.append(f"Invalid frequency type: {self.type}")
            
        if self.type == "custom":
            days = self.settings.get("days", [])
            if not days or not all(1 <= d <= 7 for d in days):
                errors.append("Custom frequency must specify valid days (1-7)")
                
        elif self.type == "spaced_repetition":
            review_after = self.settings.get("review_after")
            if not review_after or not isinstance(review_after, int) or review_after < 1:
                errors.append("spaced_repetition must specify positive review_after days")
                
        return errors

@dataclass
class Template:
    name: str
    frequency: FrequencySettings
    sections: List[Section]

    def validate(self) -> List[str]:
        """Validate entire template configuration."""
        errors = []
        
        if not self.name:
            errors.append("Template name is required")
            
        # Validate frequency
        errors.extend(self.frequency.validate())
        
        # Validate sections
        if not self.sections:
            errors.append("Template must have at least one section")
        else:
            for section in self.sections:
                errors.extend(section.validate())
                
        return errors

class TemplateLoader:
    """Handles loading and validating exercise templates."""
    
    def __init__(self, template_dir: str = "templates"):
        """Initialize the template loader.
        
        Args:
            template_dir: Directory containing template files
        """
        self.template_dir = Path(template_dir)
        if not self.template_dir.exists():
            raise FileNotFoundError(f"Templates directory not found: {template_dir}")
        
    def load_template(self, filename: str) -> Template:
        """Load and validate a template from a YAML file."""
        file_path = self.template_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Template file not found: {filename}")

        try:
            with file_path.open('r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            # Parse frequency settings
            frequency_data = data.pop("frequency")
            frequency = FrequencySettings(**frequency_data)

            # Parse sections
            sections_data = data.pop("sections")
            sections = [self._parse_section(s) for s in sections_data]

            # Create template
            template = Template(
                name=data.pop("name"),
                frequency=frequency,
                sections=sections
            )

            # Validate template
            errors = template.validate()
            if errors:
                raise ValueError("Template validation failed:\n" + "\n".join(errors))

            logger.info(f"Successfully loaded template: {filename}")
            return template

        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML format: {e}")
            raise ValueError(f"Invalid YAML format: {e}")
        except (KeyError, TypeError) as e:
            logger.error(f"Invalid template structure: {e}")
            raise ValueError(f"Invalid template structure: {e}")

    def _parse_prompt(self, data: dict) -> Prompt:
        """Parse prompt data into Prompt object."""
        follow_up = None
        if "follow_up" in data:
            follow_up = FollowUpPrompt(**data.pop("follow_up"))
            
        return Prompt(**data, follow_up=follow_up)

    def _parse_section(self, data: dict) -> Section:
        """Parse section data into Section object."""
        prompts_data = data.pop("prompts")
        prompts = [self._parse_prompt(p) for p in prompts_data]
        return Section(**data, prompts=prompts)

    def list_templates(self) -> List[str]:
        """List all available template files."""
        return [f.name for f in self.template_dir.glob("*.yaml")]

    def create_template(self, template: Template, filename: str) -> None:
        """Save a template to a YAML file."""
        # Validate template before saving
        errors = template.validate()
        if errors:
            raise ValueError("Template validation failed:\n" + "\n".join(errors))

        file_path = self.template_dir / filename
        
        # Convert template to dict
        template_dict = {
            "name": template.name,
            "frequency": {
                "type": template.frequency.type,
                "settings": template.frequency.settings
            },
            "sections": [{
                "name": section.name,
                "description": section.description,
                "prompts": [{
                    "prompt": prompt.prompt,
                    "recurring": prompt.recurring,
                    "tags": prompt.tags,
                    **({"min_words": prompt.min_words} if prompt.min_words else {}),
                    **({"max_time": prompt.max_time} if prompt.max_time else {}),
                    **({"answers_required": prompt.answers_required} if prompt.answers_required else {}),
                    **({"free_writing": prompt.free_writing} if prompt.free_writing else {}),
                    **({"follow_up": {"prompt": prompt.follow_up.prompt}} if prompt.follow_up else {})
                } for prompt in section.prompts]
            } for section in template.sections]
        }

        # Save to file
        with file_path.open('w', encoding='utf-8') as f:
            yaml.safe_dump(template_dict, f, sort_keys=False, allow_unicode=True)

    def get_week_prompts(self, template: Template, week: int) -> List[str]:
        """Get prompts for a specific week.
        
        Args:
            template: Loaded template data
            week: Week number (1-based)
            
        Returns:
            List of prompts for the week
            
        Raises:
            ValueError: If week number is invalid
        """
        if not 1 <= week <= len(template.sections):
            raise ValueError(f"Week must be between 1 and {len(template.sections)}")
            
        week_key = f"week{week}"
        prompts = template.sections[week - 1].prompts
        
        if not prompts:
            logger.warning(f"No prompts found for {week_key}")
            
        return [prompt.prompt for prompt in prompts]
        
    def get_assessment_config(self, template: Template) -> Dict[str, Any]:
        """Get assessment configuration from template.
        
        Args:
            template: Loaded template data
            
        Returns:
            Assessment configuration
        """
        return {} 