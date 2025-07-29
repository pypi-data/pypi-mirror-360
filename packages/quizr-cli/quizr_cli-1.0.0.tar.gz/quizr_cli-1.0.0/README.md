# QUIZR

A command-line quiz tool with spaced repetition and image support. Questions are stored in YAML files and organized in folders. Progress is tracked automatically.

## Installation

**Windows:**
```bash
.\install.bat
```

**Mac/Linux:**
```bash
chmod +x install.sh
./install.sh
```

For development:
```bash
pip install -r requirements.txt
pip install -e .
```

## Commands

### List Available Quizzes
```bash
python -m quizr list
```
Lists all quizzes with their question counts in a hierarchical view.

### Start Quiz
```bash
python -m quizr start <target> [mode]
```

Modes:
- `spaced` (default) - Uses spaced repetition algorithm
- `shuffle` - Randomizes all questions
- `quick` - Random subset of 10 questions

Examples:
```bash
python -m quizr start network+          # All Network+ quizzes in spaced mode
python -m quizr start comptia quick     # Quick mode for CompTIA folder
python -m quizr start port_numbers      # Specific quiz in spaced mode
```

### View Progress
```bash
python -m quizr progress [target]       # Global stats if no target
python -m quizr progress network+       # Stats for Network+ folder
python -m quizr progress port_numbers   # Stats for specific quiz
```

### Exit Session
Type any of: `quit`, `abort`, `!quit`, `!abort`, `#quit`, `#abort`

## Quiz File Format

Questions are defined in YAML files. Each question requires a unique ID and must include `prompt` and `answer`. Images and strict matching are optional.

```yaml
q_001:
  prompt: "What is the default port for HTTP?"
  answer: "80"
  strict: true  # Disables fuzzy matching for this question

q_002:
  prompt: "What protocol uses port 443?"
  answer: "HTTPS"
  # Fuzzy matching enabled (90% threshold)

q_003:
  image: "diagram1.png"  # Must exist in /images
  prompt: "What port is used for SSH in this diagram?"
  answer: "22"
```

## Directory Structure
```
workspace/
├── images/                    # Required for image questions
│   └── diagram1.png          # Use non-descriptive names
├── CompTIA/                  # Example organization
│   ├── Network+/
│   │   ├── Port_Numbers.yaml
│   │   └── Protocols.yaml
│   └── Security+/
│       └── Cryptography.yaml
└── progress.yaml             # Auto-generated progress data
```

## Progress Tracking

Progress is stored in `progress.yaml` with this structure:
```yaml
__meta__:
  total_questions_seen: 45
  total_reviews: 102
  first_use: "2024-03-21"
  last_session: "2024-03-21"
  daily_log:
    "2024-03-21": 32

CompTIA:
  Network+:
    Port_Numbers.yaml:
      q_001:
        attempts: 3
        correct: 2
        last_review: "2024-03-21"
        last_correct: "2024-03-21"
```

## Implementation Details

### Spaced Repetition
- Questions are scheduled based on performance history
- Never-seen questions get highest priority
- Correct answers increase review interval
- Failed questions return to the queue sooner

### Answer Evaluation
- Case-insensitive exact matching
- Fuzzy matching with 90% threshold (configurable)
- Strict mode available per question
- Immediate feedback with correct answers

### Image Questions
- Images must be in `/images` directory
- Use non-descriptive filenames
- Opens with system default viewer
- Continues after image is closed

## License

[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/)