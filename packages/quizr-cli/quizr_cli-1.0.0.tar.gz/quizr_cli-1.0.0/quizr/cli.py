"""
Command-line interface for QUIZR
"""

import click
import os
from typing import Dict, Any
from collections import defaultdict

from .config import Config
from .data_manager import DataManager
from .quiz_engine import QuizEngine


class QuizrCLI:
    """Main CLI class for QUIZR"""
    
    def __init__(self):
        """Initialize CLI"""
        self.config = Config()
        self._refresh()
    
    def _refresh(self):
        """Refresh data manager and quiz engine to ensure fresh data"""
        self.data_manager = DataManager(self.config)
        self.quiz_engine = QuizEngine(self.config, self.data_manager)
    
    def list_quizzes(self) -> None:
        """List all available quizzes in a hierarchical format"""
        self._refresh()  # Ensure fresh data
        quizzes = self.data_manager.discover_quizzes()
        
        if not quizzes:
            print("No quiz files found.")
            print(f"Create .yaml files in {self.config.get_exercises_dir()} or its subdirectories.")
            return
        
        print("Available Quizzes:")
        print("=" * 50)
        
        # Build a tree structure for better hierarchy display
        tree = {}
        for folder_path, quiz_files in sorted(quizzes.items()):
            if folder_path == 'root':
                continue
                
            # Split path into parts
            parts = folder_path.replace('\\', '/').split('/')
            current = tree
            
            # Build nested dictionary structure
            for part in parts:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Add quiz files to the last folder
            current['__files__'] = quiz_files
        
        def print_tree(node, prefix="", depth=0, path=""):
            """Recursively print the quiz tree"""
            # Sort folders first, then files
            items = sorted([(k, v) for k, v in node.items() if k != '__files__'])
            
            # Print folders
            for name, content in items:
                indent = "  " * depth
                
                # Print folder name
                current_path = f"{path}/{name}" if path else name
                if depth == 0:
                    print(f"{indent}{name}/")  # Root level
                else:
                    print(f"{indent}├── {name}/")  # Subfolders
                
                # Print files in this folder if any
                if '__files__' in content:
                    file_indent = "  " * (depth + 1)
                    for quiz_file in sorted(content['__files__']):
                        quiz_name = os.path.splitext(os.path.basename(quiz_file))[0]
                        
                        # Try to load quiz and get question count, but don't show errors
                        try:
                            quiz = self.data_manager.load_quiz(quiz_file)
                            question_count = quiz.get_question_count() if quiz else 0
                            print(f"{file_indent}├── {quiz_name} ({question_count} questions)")
                        except:
                            # Skip files that can't be loaded
                            continue
                
                # Then recursively print subfolders
                print_tree(content, prefix + "  ", depth + 1, current_path)
        
        # Print the tree
        print_tree(tree)
        
        print()
        print("Usage: start <folder_name> [mode]")
        print("Modes: spaced (default), shuffle, quick")
        print()
        print("Examples:")
        print("  start A+              - Start all quizzes in the A+ folder")
        print("  start Network+        - Start all quizzes in the Network+ folder")
        print("  start Port_Numbers    - Start a specific quiz file")
        print("  start CompTIA        - Start all quizzes in the CompTIA folder and subfolders")
    
    def start_quiz(self, target: str, mode: str = 'spaced') -> None:
        """Start a quiz session
        
        Args:
            target: Exact name of quiz file (without .yaml) or folder
            mode: Quiz mode (spaced, shuffle, quick)
        """
        self._refresh()  # Ensure fresh data
        valid_modes = ['spaced', 'shuffle', 'quick']
        if mode not in valid_modes:
            print(f"Invalid mode: {mode}")
            print(f"Valid modes: {', '.join(valid_modes)}")
            return
        
        # Ensure directories exist
        self.config.create_missing_directories()
        
        try:
            # Find matching quizzes - only show debug if no matches found
            quiz_files = self.data_manager.find_quizzes_by_path(target, debug=False)
            
            if not quiz_files:
                # If no matches found, try again with debug output
                print(f"\nNo quiz found with name: {target}")
                quiz_files = self.data_manager.find_quizzes_by_path(target, debug=True)
                print("\nPlease note:")
                print("1. Names are case-sensitive (e.g., 'A+' is different from 'a+')")
                print("2. Special characters must match exactly (including '+')")
                print("3. You can use either:")
                print("   - An exact quiz name (without .yaml)")
                print("   - An exact folder name")
                print("   - A full path (e.g., 'CompTIA/A+')")
                print("\nRun 'quizr list' to see available quizzes and folders.")
                return
            
            # Run the quiz session - error handling is done in quiz_engine
            session_stats = self.quiz_engine.run_quiz_session(target, mode)
            return session_stats
            
        except ValueError as e:
            print(f"\nError: {str(e)}")
            print("\nTo resolve this, you can:")
            print("1. Use a more specific path (e.g., 'CompTIA/A+' instead of just 'A+')")
            print("2. Use the exact quiz name if targeting a specific file")
            print("\nRun 'quizr list' to see the full folder structure.")
    
    def show_progress(self, target: str = 'global') -> None:
        """Show progress statistics
        
        Args:
            target: Target to show progress for ('global', folder name, or quiz name)
        """
        self._refresh()  # Ensure fresh data
        if target.lower() == 'global' or target == '':
            self._show_global_progress()
        else:
            self._show_target_progress(target)
    
    def _show_global_progress(self) -> None:
        """Show global progress statistics"""
        global_progress = self.data_manager.global_progress
        
        # Calculate total statistics
        all_quizzes = self.data_manager.discover_quizzes()
        total_folders = len(all_quizzes)
        total_exercises = sum(len(files) for files in all_quizzes.values())
        
        total_questions = 0
        questions_seen = 0
        correct_answers = 0
        total_attempts = 0
        
        for folder_path, quiz_files in all_quizzes.items():
            for quiz_file in quiz_files:
                full_path = os.path.join(folder_path, quiz_file) if folder_path != 'root' else quiz_file
                quiz = self.data_manager.load_quiz(full_path)
                if quiz:
                    for question_id in quiz.questions:
                        progress = self.data_manager.get_question_progress(full_path, question_id)
                        total_questions += 1
                        if progress.attempts > 0:
                            questions_seen += 1
                            total_attempts += progress.attempts
                            correct_answers += progress.correct
        
        print("Progress: All Topics")
        print("-" * 52)
        print(f"Total Folders         : {total_folders}")
        print(f"Total Exercises       : {total_exercises}")
        print(f"Total Questions       : {total_questions}")
        print(f"Questions Seen        : {questions_seen} ({questions_seen/total_questions*100:.1f}%)" if total_questions > 0 else "Questions Seen        : 0")
        print(f"Correct Answers       : {correct_answers}")
        print(f"Accuracy Rate         : {correct_answers/total_attempts*100:.1f}%" if total_attempts > 0 else "Accuracy Rate         : N/A")
        
        if global_progress.first_use:
            print(f"First Use Date        : {global_progress.first_use}")
        if global_progress.last_session:
            print(f"Last Session Date     : {global_progress.last_session}")
        print("-" * 52)
        
        # Show recent activity
        if global_progress.daily_log:
            recent_days = sorted(global_progress.daily_log.items(), reverse=True)[:7]
            print("Recent Activity:")
            for date, count in recent_days:
                print(f"  {date}: {count} questions")
    
    def _show_target_progress(self, target: str) -> None:
        """Show progress for a specific target
        
        Args:
            target: Folder or quiz name
        """
        matching_files = self.data_manager.find_quizzes_by_path(target, debug=False)
        
        if not matching_files:
            print(f"No quizzes found for: {target}")
            return
        
        # Determine if this is a single quiz or multiple
        if len(matching_files) == 1:
            self._show_quiz_progress(matching_files[0])
        else:
            self._show_folder_progress(target, matching_files)
    
    def _show_quiz_progress(self, quiz_filepath: str) -> None:
        """Show progress for a single quiz
        
        Args:
            quiz_filepath: Path to the quiz file
        """
        quiz = self.data_manager.load_quiz(quiz_filepath)
        if not quiz:
            print(f"Could not load quiz: {quiz_filepath}")
            return
        
        total_questions = quiz.get_question_count()
        questions_answered = 0
        correct_answers = 0
        total_attempts = 0
        last_session = None
        
        for question_id in quiz.questions:
            progress = self.data_manager.get_question_progress(quiz_filepath, question_id)
            if progress.attempts > 0:
                questions_answered += 1
                total_attempts += progress.attempts
                correct_answers += progress.correct
                if progress.last_review and (not last_session or progress.last_review > last_session):
                    last_session = progress.last_review
        
        print(f"Progress: {quiz_filepath}")
        print("-" * 52)
        print(f"Total Questions       : {total_questions}")
        print(f"Questions Answered    : {questions_answered} ({questions_answered/total_questions*100:.0f}%)")
        print(f"Correct Answers       : {correct_answers}")
        print(f"Accuracy Rate         : {correct_answers/total_attempts*100:.1f}%" if total_attempts > 0 else "Accuracy Rate         : N/A")
        if last_session:
            print(f"Last Session Date     : {last_session}")
        print("-" * 52)
    
    def _show_folder_progress(self, folder_name: str, quiz_files: list) -> None:
        """Show progress for a folder containing multiple quizzes
        
        Args:
            folder_name: Name of the folder
            quiz_files: List of quiz files in the folder
        """
        stats = self.data_manager.calculate_folder_stats(folder_name)
        
        print(f"Progress: {folder_name}/")
        print("-" * 52)
        print(f"Total Exercises       : {len(quiz_files)}")
        print(f"Total Questions       : {stats['total_questions']}")
        print(f"Questions Answered    : {stats['questions_seen']} ({stats['completion_rate']:.1f}%)")
        print(f"Correct Answers       : {stats['correct_answers']}")
        print(f"Accuracy Rate         : {stats['accuracy_rate']:.1f}%" if stats['total_attempts'] > 0 else "Accuracy Rate         : N/A")
        print("-" * 52)
        
        print("Exercises:")
        for quiz_file in sorted(quiz_files):
            quiz = self.data_manager.load_quiz(quiz_file)
            if quiz:
                quiz_stats = self._calculate_quiz_stats(quiz_file, quiz)
                accuracy = quiz_stats['accuracy'] if quiz_stats['attempts'] > 0 else 0
                print(f"  • {quiz.name:<25} — {quiz_stats['seen']:.0f}% seen | {accuracy:.1f}% accuracy")
    
    def _calculate_quiz_stats(self, quiz_filepath: str, quiz: 'Quiz') -> Dict[str, float]:
        """Calculate statistics for a single quiz
        
        Args:
            quiz_filepath: Path to quiz file
            quiz: Quiz object
            
        Returns:
            Dictionary with quiz statistics
        """
        total = quiz.get_question_count()
        seen = 0
        correct = 0
        attempts = 0
        
        for question_id in quiz.questions:
            progress = self.data_manager.get_question_progress(quiz_filepath, question_id)
            if progress.attempts > 0:
                seen += 1
                attempts += progress.attempts
                correct += progress.correct
        
        return {
            'total': total,
            'seen': (seen / total * 100) if total > 0 else 0,
            'accuracy': (correct / attempts * 100) if attempts > 0 else 0,
            'attempts': attempts
        }


# CLI command definitions
@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """QUIZR - Command-line quiz tool with spaced repetition"""
    if ctx.invoked_subcommand is None:
        print("QUIZR - Command-line quiz tool with spaced repetition")
        print()
        print("Available commands:")
        print("  list                    - List all available quizzes")
        print("  start <target> [mode]   - Start a quiz session")
        print("  progress [target]       - Show progress statistics")
        print("  quit                    - Exit the program")
        print()
        print("Modes: spaced (default), shuffle, quick")
        print("Examples:")
        print("  quizr list")
        print("  quizr start network+ spaced")
        print("  quizr start comptia quick")
        print("  quizr progress network+")


@main.command()
def list():
    """List all available quizzes"""
    cli = QuizrCLI()
    cli.list_quizzes()


@main.command()
@click.argument('target')
@click.argument('mode', default='spaced')
def start(target, mode):
    """Start a quiz session"""
    cli = QuizrCLI()
    cli.start_quiz(target, mode)


@main.command()
@click.argument('target', default='global')
def progress(target):
    """Show progress statistics"""
    cli = QuizrCLI()
    cli.show_progress(target)


@main.command()
def quit():
    """Exit the program"""
    print("Goodbye!")
    exit(0)


if __name__ == '__main__':
    main() 