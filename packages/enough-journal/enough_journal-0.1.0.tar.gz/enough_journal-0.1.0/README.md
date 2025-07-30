# ENOUGH- The CLI Journal

A flexible journaling system for personal growth and self-reflection, supporting customizable prompts, scheduled exercises, and structured reviews.

## TODO: Installation Setup
- [ ] Set up PyPI account and configure credentials
- [ ] Create and test PyPI package upload workflow
- [ ] Generate and verify package hash for AUR package
- [ ] Test installation scripts on different platforms
- [ ] Add version badges and PyPI status to README
- [ ] Create detailed installation troubleshooting guide

**Note:** Currently in development. Installation methods will be fully implemented in upcoming updates. For now, use the manual installation method:

```bash
git clone https://github.com/yourusername/personal-growth-journal.git
cd personal-growth-journal
pip install -e .
```

## Features

- Custom prompt scheduling (daily, weekly, monthly)
- Follow-up questions and response tracking
- Weekly review system
- Progress tracking and statistics
- Tag-based organization
- Flexible response formats

## Installation

### Option 1: PyPI (All Platforms)

Install directly from PyPI:
```bash
pip install sentence-completion
```

### Option 2: Arch Linux (AUR)

Install using your preferred AUR helper:
```bash
yay -S python-sentence-completion
```

Or manually:
```bash
git clone https://aur.archlinux.org/python-sentence-completion.git
cd python-sentence-completion
makepkg -si
```

### Option 3: Automatic Installation Scripts

#### Linux/macOS:
```bash
git clone https://github.com/yourusername/personal-growth-journal.git
cd personal-growth-journal
chmod +x install.sh
./install.sh
```

#### Windows:
```bash
git clone https://github.com/yourusername/personal-growth-journal.git
cd personal-growth-journal
install.bat
```

### Option 4: Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/personal-growth-journal.git
cd personal-growth-journal
```

2. Create and activate a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate.bat  # Windows
```

3. Install the package:
```bash
pip install -e .
```

## Usage

### Starting an Exercise

```bash
sentence-completion start exercises/daily.yaml
```

### Running Weekly Review

```bash
sentence-completion review exercises/daily.yaml
```

### Adding Custom Entries

```bash
sentence-completion add "What did I learn today?" --tags learning,reflection --answers 3
```

## Exercise File Format

Exercise files use YAML format with the following structure:

```yaml
name: "Daily Reflection"
frequency: "daily"  # or "weekly", "monthly", or custom settings

# For custom frequency, specify days, weeks and months
frequency:
  days: [1, 3, 5]  # 1=Monday, 7=Sunday
  weekly: [1, 3, 5] # 1=Every week, 3=Every 3 weeks
  monthly: [1, 3, 5] # 1=Every month, 3=Every 3 months
  months: [1, 3, 5] # 1=January, 12=December

# Default settings
answers_required: 1  # Number of responses required
min_words: 0       # Minimum words per response
max_time: 300      # Maximum time in seconds

# The actual prompts
prompts:
  p_000:  # You have to assign every question an ID like so
    prompt: "What's on my mind right now..."
    tags: ["reflection"]
    answers_required: 3  # Override default
    
  p_001:  # Sequential IDs required
    prompt: "What am I grateful for today?"
    tags: ["gratitude"]
    follow_up: "p_002"  # Reference to follow-up question
    
  p_002:
    prompt: "How can I express this gratitude?"
    tags: ["action", "gratitude"]
```

## Directory Structure

```
Core/
├── sentence_completion/     # Main package
│   ├── cli/               # Command line interface
│   ├── core/              # Core functionality
│   └── utils/             # Utility functions
│
├── Submissions/           # Journal entries
│   ├── Daily_Reflection/  # Organized by exercise
│   │   ├── YYYY_MM_DD_1.yaml
│   │   └── YYYY_MM_DD_review.yaml
│   └── Custom_Entries/    # Custom journal entries
│
└── Exercises/            # Exercise templates
    ├── daily.yaml
    └── weekly.yaml
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
