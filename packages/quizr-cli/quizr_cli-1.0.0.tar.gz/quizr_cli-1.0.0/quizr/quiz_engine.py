"""
Quiz engine for QUIZR - handles question presentation and answer evaluation
"""

import os
import subprocess
import sys
import random
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from fuzzywuzzy import fuzz

from .models import Question, Quiz, QuestionProgress, SessionStats
from .data_manager import DataManager
from .config import Config


class QuizEngine:
    """Core quiz engine for running quiz sessions"""
    
    def __init__(self, config: Config, data_manager: DataManager):
        """Initialize quiz engine
        
        Args:
            config: Configuration object
            data_manager: Data manager for loading and saving data
        """
        self.config = config
        self.data_manager = data_manager
        self.current_session: Optional[SessionStats] = None
    
    def evaluate_answer(self, question: Question, user_answer: str) -> bool:
        """Evaluate if the user's answer is correct
        
        Args:
            question: Question being answered
            user_answer: User's answer attempt
            
        Returns:
            True if answer is correct, False otherwise
        """
        if not user_answer:
            print("\n❌ Incorrect. The correct answer is:", question.answer)
            return False
            
        # Get similarity threshold from config (default 90%)
        threshold = self.config.get('similarity_threshold', 90)
        
        # If question requires strict matching, use exact match
        if question.strict:
            is_correct = user_answer.lower() == question.answer.lower()
        else:
            # Use fuzzy matching with similarity threshold
            ratio = fuzz.ratio(user_answer.lower(), question.answer.lower())
            is_correct = ratio >= threshold
        
        if is_correct:
            print("\n✓ Correct!")
        else:
            print("\n❌ Incorrect. The correct answer is:", question.answer)
            
        return is_correct
    
    def display_image(self, image_path: str) -> bool:
        """Display an image using the system's default viewer
        
        Args:
            image_path: Path to the image file
            
        Returns:
            True if image was opened successfully, False otherwise
        """
        if not os.path.exists(image_path):
            print(f"Warning: Image not found: {image_path}")
            return False
        
        try:
            if sys.platform.startswith('win'):
                os.startfile(image_path)
            elif sys.platform.startswith('darwin'):  # macOS
                subprocess.run(['open', image_path])
            else:  # Linux and others
                subprocess.run(['xdg-open', image_path])
            return True
        except Exception as e:
            print(f"Error opening image: {e}")
            return False
    
    def present_question(self, question: Question) -> str:
        """Present a question to the user and get their answer
        
        Args:
            question: Question to present
            
        Returns:
            User's answer
        """
        # Display image if present
        if question.image:
            image_path = os.path.join(self.config.get_images_dir(), question.image)
            if not self.display_image(image_path):
                print(f"Warning: Could not display image: {question.image}")
        
        # Display question
        print("\n" + question.prompt)
        
        # Get user input
        try:
            answer = input("\nYour answer: ").strip()
            return answer
        except KeyboardInterrupt:
            return "!quit"
        except EOFError:
            return "!quit"
    
    def get_questions_for_mode(self, quizzes: List[Quiz], mode: str) -> List[Tuple[str, Question]]:
        """Get questions based on the selected mode
        
        Args:
            quizzes: List of loaded quizzes
            mode: Mode to use ('shuffle', 'quick', 'spaced')
            
        Returns:
            List of tuples (quiz_filepath, question)
        """
        all_questions = []
        
        # Collect all questions with their quiz file paths
        for quiz in quizzes:
            for question in quiz.questions.values():
                all_questions.append((quiz.filepath, question))
        
        if mode == 'quick':
            # Select random subset
            count = min(self.config.get('quick_mode_count', 10), len(all_questions))
            return random.sample(all_questions, count)
        
        elif mode == 'shuffle':
            # Randomize order but include all questions
            random.shuffle(all_questions)
            return all_questions
        
        elif mode == 'spaced':
            # Sort by spaced repetition priority
            return self._sort_by_spaced_repetition(all_questions)
        
        else:
            # Default to spaced repetition
            return self._sort_by_spaced_repetition(all_questions)
    
    def _sort_by_spaced_repetition(self, questions: List[Tuple[str, Question]]) -> List[Tuple[str, Question]]:
        """Sort questions by spaced repetition priority
        
        Args:
            questions: List of (quiz_filepath, question) tuples
            
        Returns:
            Sorted list with highest priority questions first
        """
        def calculate_priority(item: Tuple[str, Question]) -> float:
            quiz_filepath, question = item
            progress = self.data_manager.get_question_progress(quiz_filepath, question.id)
            
            # Never reviewed questions get highest priority
            if progress.attempts == 0:
                return 999999
            
            # Calculate days since last review
            if progress.last_review:
                try:
                    last_review = datetime.fromisoformat(progress.last_review)
                    days_since = (datetime.now() - last_review).days
                except:
                    days_since = 999  # Error parsing date, treat as very old
            else:
                days_since = 999
            
            # Calculate interval based on performance
            # Better performance = longer interval between reviews
            if progress.attempts > 0:
                success_rate = progress.correct / progress.attempts
                # Higher success rate = lower priority (longer intervals)
                interval_multiplier = 1 + (success_rate * 2)  # 1-3x multiplier
                base_interval = min(progress.correct + 1, 30)  # 1-30 days base
                target_interval = base_interval * interval_multiplier
            else:
                target_interval = 1
            
            # Questions overdue for review get higher priority
            priority = days_since - target_interval
            
            # Boost priority for questions with recent failures
            if progress.last_correct and progress.last_review:
                try:
                    last_correct = datetime.fromisoformat(progress.last_correct)
                    last_review = datetime.fromisoformat(progress.last_review)
                    if last_review > last_correct:  # Most recent attempt was wrong
                        priority += 10
                except:
                    pass
            
            return priority
        
        # Sort by priority (highest first)
        sorted_questions = sorted(questions, key=calculate_priority, reverse=True)
        return sorted_questions
    
    def run_quiz_session(self, target_name: str, mode: str = 'spaced') -> SessionStats:
        """Run a complete quiz session
        
        Args:
            target_name: Exact name of quiz file (without .yaml) or folder
            mode: Quiz mode ('shuffle', 'quick', 'spaced')
            
        Returns:
            Session statistics
        """
        # Start session tracking
        self.current_session = SessionStats(
            mode=mode,
            start_time=datetime.now()
        )
        
        try:
            # Load quizzes - will raise ValueError if name is ambiguous
            quiz_files = self.data_manager.find_quizzes_by_path(target_name, debug=False)
            
            if not quiz_files:
                print(f"No quiz found with name: {target_name}")
                print("\nPlease use one of these:")
                print("1. An exact quiz name (without .yaml)")
                print("2. An exact folder name")
                print("\nRun 'quizr list' to see available quizzes and folders.")
                self.current_session.finish_session()
                return self.current_session
            
            quizzes = []
            for quiz_file in quiz_files:
                quiz = self.data_manager.load_quiz(quiz_file)
                if quiz:
                    quizzes.append(quiz)
                    self.current_session.exercises_completed.append(quiz.name)
            
            if not quizzes:
                print("No valid quizzes could be loaded")
                self.current_session.finish_session()
                return self.current_session
            
            # Get questions based on mode
            questions = self.get_questions_for_mode(quizzes, mode)
            
            # Print session header
            print("\n" + "=" * 60)
            print(f"Starting {mode} mode session with {len(questions)} questions")
            print(f"Target: {target_name}")
            print("=" * 60 + "\n")
            
            # Run the quiz
            was_aborted = False
            for quiz_file, question in questions:
                answer = self.present_question(question)
                
                # Check for quit/abort commands with various prefixes
                quit_commands = ['quit', 'abort', '!quit', '!abort', '#quit', '#abort']
                if any(answer.lower().strip() == cmd for cmd in quit_commands):
                    was_aborted = True
                    break
                    
                is_correct = self.evaluate_answer(question, answer)
                self.current_session.record_answer(is_correct)
                
                # Update progress
                progress = self.data_manager.get_question_progress(quiz_file, question.id)
                progress.record_attempt(is_correct)
                self.data_manager.update_question_progress(quiz_file, question.id, progress)
                
                # Save progress periodically
                self.data_manager.save_progress()
                
                # Add a blank line for readability between questions
                print()
            
            # Print session results
            print("\n" + "=" * 60)
            print(f"Exercise Complete: {' + '.join(self.current_session.exercises_completed)}")
            print("=" * 60)
            print(f"Mode                  : {mode}")
            print(f"Questions Attempted   : {self.current_session.questions_attempted}")
            print(f"Correct Answers       : {self.current_session.questions_correct}")
            print(f"Correct Answers %     : {self.current_session.get_accuracy():.1f}%")
            print(f"Session Duration      : {self.current_session.get_duration()}")
            print("=" * 60)
            
            if was_aborted:
                print("Note: Session was aborted by user.")
            elif mode == 'quick':
                print("Note: Quick mode session completed with selected questions.")
            else:
                print("Note: Session completed with all available questions.")
            
        except ValueError as e:
            print(f"\nError: {str(e)}")
            print("\nPlease use a unique name that matches either:")
            print("1. A quiz file (without .yaml)")
            print("2. A folder")
            print("\nRun 'quizr list' to see available quizzes and folders.")
        
        self.current_session.finish_session()
        return self.current_session 