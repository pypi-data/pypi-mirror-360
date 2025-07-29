"""
Data models for QUIZR quiz system
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, date
import os


@dataclass
class Question:
    """Represents a single quiz question"""
    id: str
    prompt: str
    answer: str
    image: Optional[str] = None
    strict: bool = False  # If True, no fuzzy matching
    
    def has_image(self) -> bool:
        """Check if question has an associated image"""
        return self.image is not None
    
    def get_image_path(self, images_dir: str) -> Optional[str]:
        """Get full path to image file"""
        if not self.has_image():
            return None
        return os.path.join(images_dir, self.image)


@dataclass 
class QuestionProgress:
    """Tracks progress for a single question"""
    attempts: int = 0
    correct: int = 0
    last_review: Optional[str] = None
    last_correct: Optional[str] = None
    
    def get_accuracy(self) -> float:
        """Calculate accuracy percentage"""
        if self.attempts == 0:
            return 0.0
        return (self.correct / self.attempts) * 100
    
    def record_attempt(self, is_correct: bool) -> None:
        """Record a new attempt"""
        now = datetime.now().isoformat()
        self.attempts += 1
        self.last_review = now
        
        if is_correct:
            self.correct += 1
            self.last_correct = now


@dataclass
class Quiz:
    """Represents a quiz loaded from a YAML file"""
    name: str
    filepath: str
    questions: Dict[str, Question]
    
    def get_question_count(self) -> int:
        """Get total number of questions in quiz"""
        return len(self.questions)
    
    def get_question_ids(self) -> List[str]:
        """Get list of all question IDs"""
        return list(self.questions.keys())


@dataclass
class SessionStats:
    """Tracks statistics for a quiz session"""
    mode: str
    start_time: datetime
    end_time: Optional[datetime] = None
    questions_attempted: int = 0
    questions_correct: int = 0
    exercises_completed: List[str] = field(default_factory=list)
    
    def get_duration(self) -> str:
        """Get formatted session duration"""
        if self.end_time is None:
            duration = datetime.now() - self.start_time
        else:
            duration = self.end_time - self.start_time
        
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def get_accuracy(self) -> float:
        """Get accuracy percentage"""
        if self.questions_attempted == 0:
            return 0.0
        return (self.questions_correct / self.questions_attempted) * 100
    
    def record_answer(self, is_correct: bool) -> None:
        """Record an answer attempt"""
        self.questions_attempted += 1
        if is_correct:
            self.questions_correct += 1
    
    def finish_session(self) -> None:
        """Mark session as finished"""
        self.end_time = datetime.now()


@dataclass
class GlobalProgress:
    """Global progress tracking across all quizzes"""
    total_questions_seen: int = 0
    total_reviews: int = 0
    first_use: Optional[str] = None
    last_session: Optional[str] = None
    daily_log: Dict[str, int] = field(default_factory=dict)
    
    def update_session_stats(self, questions_reviewed: int) -> None:
        """Update global stats after a session"""
        now = datetime.now()
        today = now.date().isoformat()
        
        if self.first_use is None:
            self.first_use = today
            
        self.last_session = now.isoformat()
        self.total_reviews += questions_reviewed
        
        if today in self.daily_log:
            self.daily_log[today] += questions_reviewed
        else:
            self.daily_log[today] = questions_reviewed 