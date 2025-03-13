"""
Memory Manager for the Deep Thinking Chain.

This module contains the MemoryManager class which is responsible for loading,
updating, and saving memory for each analysis cycle in the DeepThinkingChain project.
"""

import os
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import time
from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class Question:
    """A question and its answers in the QA system."""
    
    id: str
    text: str
    timestamp: datetime
    status: str = "pending"  # pending, answered, failed
    is_original: bool = True  # Whether this is an original question or a follow-up
    current_question_in_investigate: bool = False  # Whether this question is currently being investigated
    answers: List[Tuple[str, str, datetime]] = field(default_factory=list)  # List of (answer_text, source, timestamp)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Question to a dictionary for serialization"""
        return {
            "id": self.id,
            "text": self.text,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status,
            "is_original": self.is_original,
            "current_question_in_investigate": self.current_question_in_investigate,
            "answers": [
                {
                    "text": answer[0],
                    "source": answer[1],
                    "timestamp": answer[2].isoformat()
                } 
                for answer in self.answers
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Question':
        """Create a Question from a dictionary"""
        question = cls(
            id=data["id"],
            text=data["text"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            status=data["status"],
            is_original=data["is_original"],
            current_question_in_investigate=data.get("current_question_in_investigate", False)
        )
        
        # Add answers if they exist
        if "answers" in data:
            question.answers = [
                (
                    answer_data["text"],
                    answer_data["source"],
                    datetime.fromisoformat(answer_data["timestamp"])
                )
                for answer_data in data["answers"]
            ]
            
        return question
    
    def add_answer(self, text: str, source: str) -> Tuple[str, str, datetime]:
        """
        Add an answer to this question
        
        Args:
            text: The answer text
            source: The source of the answer (search, browser, analysis, etc.)
            
        Returns:
            Tuple containing the answer text, source, and timestamp
        """
        answer = (text, source, datetime.now())
        self.answers.append(answer)
        self.status = "answered"
        return answer
    
    def get_latest_answer(self) -> Optional[Tuple[str, str, datetime]]:
        """
        Get the most recent answer for this question
        
        Returns:
            Optional[Tuple]: The latest answer as (text, source, timestamp), or None if no answers
        """
        if not self.answers:
            return None
        return sorted(self.answers, key=lambda a: a[2], reverse=True)[0]


@dataclass
class Link:
    """A link and its metadata in the link tracking system."""
    
    id: str
    url: str
    status: str  # pending, visited, failed, etc.
    content: str  # one sentence summary of the content
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Link to a dictionary for serialization"""
        return {
            "id": self.id,
            "url": self.url,
            "status": self.status,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Link':
        """Create a Link from a dictionary"""
        return cls(
            id=data["id"],
            url=data["url"],
            status=data["status"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )


class MemoryManager:
    """Manages memory operations for the DeepThinkingChain analysis process.
    
    This class provides methods to load, update, and save memory for each analysis cycle,
    ensuring persistence of analysis state across runs and iterations.
    """
    
    def __init__(self, symbol: str, memory_dir: str = "memory"):
        """Initialize the MemoryManager for a specific stock symbol.
        
        Args:
            symbol: The stock symbol being analyzed (e.g., 'NVDA')
            memory_dir: Directory where memory files are stored (default: 'memory')
        """
        self.symbol = symbol.upper()
        self.memory_dir = memory_dir
        self.memory_file = f"{memory_dir}/{self.symbol}_memory.json"
        self.memory = {}
        
        # Initialize sub-managers
        self.questions: List[Question] = []
        self.links: List[Link] = []
        self.categories: Dict[str, List[Dict[str, Any]]] = {}
        
        # Create memory directory if it doesn't exist
        os.makedirs(memory_dir, exist_ok=True)
        
        # Initialize or load memory
        self._load_memory()
    
    def _load_memory(self) -> Dict[str, Any]:
        """Load memory from disk if it exists, otherwise initialize a new memory structure.
        
        Returns:
            Dict containing the memory data
        """
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    self.memory = json.load(f)
                print(f"📂 Loaded existing memory for {self.symbol}")
                
                # Load sub-managers data if available
                if "questions" in self.memory:
                    self.questions = [Question.from_dict(q) for q in self.memory["questions"]]
                if "links" in self.memory:
                    self.links = [Link.from_dict(l) for l in self.memory["links"]]
                if "categories" in self.memory:
                    self.categories = self.memory["categories"]
                    
            except json.JSONDecodeError:
                print(f"⚠️ Error loading memory file. Creating new memory.")
                self._initialize_memory()
        else:
            self._initialize_memory()
        
        return self.memory
    
    def _initialize_memory(self) -> Dict[str, Any]:
        """Initialize a new memory structure for the analysis process.
        
        Returns:
            Dict containing the initialized memory structure
        """
        self.memory = {
            "symbol": self.symbol,
            "iterations": [],
            "current_focus": "financial_performance",
            "required_focus_areas": [
                "financial_performance",
                "competitive_analysis",
                "growth_prospects",
                "risk_assessment"
            ],
            "completed_focus_areas": [],
            "start_time": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "completion_percentage": 0,
            "questions": [],
            "links": [],
            "categories": {}
        }
        self.save_memory()
        print(f"📝 Created new memory for {self.symbol}")
        return self.memory
    
    def save_memory(self) -> bool:
        """Save the current memory state to disk.
        
        Returns:
            Boolean indicating success or failure
        """
        try:
            # Update the last_updated timestamp
            self.memory["last_updated"] = datetime.now().isoformat()
            
            # Update sub-managers data
            self.memory["questions"] = [q.to_dict() for q in self.questions]
            self.memory["links"] = [l.to_dict() for l in self.links]
            self.memory["categories"] = self.categories
            
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=2)
            return True
        except Exception as e:
            print(f"⚠️ Error saving memory: {str(e)}")
            return False
    
    def get_memory(self) -> Dict[str, Any]:
        """Get the current memory state.
        
        Returns:
            Dict containing the current memory data
        """
        return self.memory
    
    def update_memory(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update the memory with new data.
        
        Args:
            updates: Dict containing the updates to apply to the memory
            
        Returns:
            Dict containing the updated memory data
        """
        # Update the memory with the new data
        for key, value in updates.items():
            self.memory[key] = value
        
        # Save the updated memory
        self.save_memory()
        
        return self.memory
    
    def add_iteration(self, iteration_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new iteration to the memory.
        
        Args:
            iteration_data: Dict containing the iteration data
            
        Returns:
            Dict containing the updated memory data
        """
        # Ensure iterations list exists
        if "iterations" not in self.memory:
            self.memory["iterations"] = []
        
        # Add timestamp if not present
        if "timestamp" not in iteration_data:
            iteration_data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Add the iteration data
        self.memory["iterations"].append(iteration_data)
        
        # Update completion percentage
        self._update_completion_percentage()
        
        # Save the updated memory
        self.save_memory()
        
        return self.memory
    
    def update_focus_area(self, focus_area: str, completed: bool = True) -> Dict[str, Any]:
        """Update the current focus area and optionally mark it as completed.
        
        Args:
            focus_area: The focus area to set as current
            completed: Whether to mark the focus area as completed
            
        Returns:
            Dict containing the updated memory data
        """
        # Update current focus
        self.memory["current_focus"] = focus_area
        
        # Mark as completed if specified
        if completed and focus_area not in self.memory.get("completed_focus_areas", []):
            if "completed_focus_areas" not in self.memory:
                self.memory["completed_focus_areas"] = []
            self.memory["completed_focus_areas"].append(focus_area)
        
        # Update completion percentage
        self._update_completion_percentage()
        
        # Save the updated memory
        self.save_memory()
        
        return self.memory
    
    def _update_completion_percentage(self) -> float:
        """Update the analysis completion percentage based on iterations and focus areas.
        
        Returns:
            Float representing the completion percentage
        """
        required_areas = self.memory.get("required_focus_areas", [])
        completed_areas = self.memory.get("completed_focus_areas", [])
        iterations = self.memory.get("iterations", [])
        max_iterations = self.memory.get("max_iterations", 5)
        
        # Base percentage on completed focus areas and iteration count
        if not required_areas:
            area_percentage = 0
        else:
            area_percentage = (len(completed_areas) / len(required_areas)) * 100
        
        # Factor in iteration count (each iteration contributes up to 20%)
        iteration_percentage = min(len(iterations) / max_iterations * 20, 20)
        
        # Combine the two factors
        total_percentage = min(area_percentage * 0.8 + iteration_percentage, 100)
        
        # Update memory
        self.memory["completion_percentage"] = round(total_percentage, 1)
        
        return self.memory["completion_percentage"]
    
    def get_latest_iteration(self) -> Optional[Dict[str, Any]]:
        """Get the most recent iteration data.
        
        Returns:
            Dict containing the latest iteration data, or None if no iterations exist
        """
        iterations = self.memory.get("iterations", [])
        if iterations:
            return iterations[-1]
        return None
    
    def get_all_analyses(self) -> List[Dict[str, Any]]:
        """Get all analyses from all iterations.
        
        Returns:
            List of analysis results from all iterations
        """
        analyses = []
        for iteration in self.memory.get("iterations", []):
            if "analysis" in iteration:
                analyses.append(iteration["analysis"])
        return analyses
    
    def clear_memory(self) -> bool:
        """Clear the memory and start fresh.
        
        Returns:
            Boolean indicating success or failure
        """
        try:
            self._initialize_memory()
            self.questions = []
            self.links = []
            self.categories = {}
            return True
        except Exception as e:
            print(f"⚠️ Error clearing memory: {str(e)}")
            return False
    
    def export_memory(self, export_file: Optional[str] = None) -> str:
        """Export the memory to a JSON file.
        
        Args:
            export_file: Path to the export file (default: None, uses timestamp)
            
        Returns:
            Path to the exported file
        """
        if export_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_file = f"exports/{self.symbol}_memory_{timestamp}.json"
        
        # Create exports directory if it doesn't exist and the path has a directory
        directory = os.path.dirname(export_file)
        if directory:  # Only create directory if there is one in the path
            os.makedirs(directory, exist_ok=True)
        
        try:
            with open(export_file, 'w') as f:
                json.dump(self.memory, f, indent=2)
            print(f"📤 Exported memory to {export_file}")
            return export_file
        except Exception as e:
            print(f"⚠️ Error exporting memory: {str(e)}")
            return ""
    
    # QA Manager methods
    def add_question(self, text: str, is_original: bool = True) -> Question:
        """
        Add a new question to track
        
        Args:
            text: The question text
            is_original: Whether this is an original question or a follow-up
            
        Returns:
            Question: The created question object
        """
        question = Question(
            id=str(uuid4()),
            text=text,
            timestamp=datetime.now(),
            is_original=is_original
        )
        self.questions.append(question)
        self.save_memory()
        return question
    
    def add_follow_up_question(self, text: str) -> Question:
        """
        Add a follow-up question
        
        Args:
            text: The follow-up question text
            
        Returns:
            Question: The created question object
        """
        return self.add_question(text, is_original=False)
    
    def get_original_questions(self) -> List[Question]:
        """
        Get all original questions
        
        Returns:
            List[Question]: List of original questions
        """
        return [q for q in self.questions if q.is_original]
    
    def get_follow_up_questions(self) -> List[Question]:
        """
        Get all follow-up questions
        
        Returns:
            List[Question]: List of follow-up questions
        """
        return [q for q in self.questions if not q.is_original]
    
    def add_answer(self, question_id: str, text: str, source: str) -> Tuple[str, str, datetime]:
        """
        Add an answer to a question
        
        Args:
            question_id: The ID of the question being answered
            text: The answer text
            source: The source of the answer (search, browser, analysis, etc.)
            
        Returns:
            Tuple containing the answer text, source, and timestamp
        """
        for question in self.questions:
            if question.id == question_id:
                answer = question.add_answer(text, source)
                self.save_memory()
                return answer
        
        raise ValueError(f"Question with ID {question_id} not found")
    
    def get_latest_question(self) -> Optional[Question]:
        """
        Get the most recent question that hasn't been answered
        
        Returns:
            Optional[Question]: The latest pending question, or None if no pending questions
        """
        for question in reversed(self.questions):
            if question.status == "pending":
                return question
        return None
    
    def set_current_question(self, question_id: str):
        """
        Set a question as the current one being investigated
        
        Args:
            question_id: The ID of the question to set as current
        """
        # First clear any existing current question
        for question in self.questions:
            question.current_question_in_investigate = False
        
        # Set the new current question
        for question in self.questions:
            if question.id == question_id:
                question.current_question_in_investigate = True
                break
        
        self.save_memory()
    
    def get_current_question(self) -> Optional[Question]:
        """
        Get the question that is currently being investigated
        
        Returns:
            Optional[Question]: The current question being investigated, or None if no question is being investigated
        """
        for question in self.questions:
            if question.current_question_in_investigate:
                return question
        return None
    
    def clear_current_question(self):
        """
        Clear the current question being investigated
        """
        for question in self.questions:
            question.current_question_in_investigate = False
        self.save_memory()
    
    def get_question_answers(self, question_id: str) -> List[Tuple[str, str, datetime]]:
        """
        Get all answers for a specific question
        
        Args:
            question_id: The ID of the question
            
        Returns:
            List[Tuple]: List of answers as (text, source, timestamp) for the question
        """
        for question in self.questions:
            if question.id == question_id:
                return question.answers
        return []
    
    def mark_question_failed(self, question_id: str):
        """
        Mark a question as failed
        
        Args:
            question_id: The ID of the question to mark as failed
        """
        for question in self.questions:
            if question.id == question_id:
                question.status = "failed"
                self.save_memory()
                break
    
    def get_qa_summary(self) -> str:
        """
        Get a human-readable summary of the QA manager's state
        
        Returns:
            A string summary of the QA manager's state
        """
        if not self.questions:
            return "No questions have been asked."
        
        summary = [f"# Questions and Answers ({len(self.questions)} questions)"]
        
        # Add original questions and their answers
        original_questions = self.get_original_questions()
        if original_questions:
            summary.append("\n## Original Questions")
            for question in original_questions:
                status_marker = "✓" if question.status == "answered" else "❓"
                summary.append(f"\n### {status_marker} {question.text}")
                
                # Add answers for this question
                if question.answers:
                    for answer_text, source, timestamp in question.answers:
                        timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                        summary.append(f"**Answer** ({source}, {timestamp_str}):")
                        summary.append(f"{answer_text}")
                else:
                    summary.append("*No answers yet*")
        
        # Add follow-up questions and their answers
        follow_up_questions = self.get_follow_up_questions()
        if follow_up_questions:
            summary.append("\n## Follow-up Questions")
            for question in follow_up_questions:
                status_marker = "✓" if question.status == "answered" else "❓"
                summary.append(f"\n### {status_marker} {question.text}")
                
                # Add answers for this question
                if question.answers:
                    for answer_text, source, timestamp in question.answers:
                        timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                        summary.append(f"**Answer** ({source}, {timestamp_str}):")
                        summary.append(f"{answer_text}")
                else:
                    summary.append("*No answers yet*")
        
        return "\n".join(summary)
    
    # Link Manager methods
    def add_link(self, url: str, status: str, content: str) -> Link:
        """
        Add a link to track
        
        Args:
            url: The URL of the link
            status: The status of the link (pending, visited, failed, etc.)
            content: A one sentence summary of the content
            
        Returns:
            Link: The created link object
        """
        link = Link(
            id=str(uuid4()),
            url=url,
            status=status,
            content=content,
            timestamp=datetime.now()
        )
        self.links.append(link)
        self.save_memory()
        return link
    
    def get_link_by_url(self, url: str) -> Optional[Link]:
        """
        Get a link by its URL
        
        Args:
            url: The URL to search for
            
        Returns:
            Optional[Link]: The link if found, None otherwise
        """
        for link in self.links:
            if link.url == url:
                return link
        return None
    
    def update_link_status(self, url: str, status: str, content: str = None) -> Optional[Link]:
        """
        Update the status and content of a link
        
        Args:
            url: The URL of the link to update
            status: The new status
            content: Optional new content summary
            
        Returns:
            Optional[Link]: The updated link if found, None otherwise
        """
        for link in self.links:
            if link.url == url:
                link.status = status
                if content:
                    link.content = content
                self.save_memory()
                return link
        return None
    
    def get_links_by_status(self, status: str) -> List[Link]:
        """
        Get all links with a specific status
        
        Args:
            status: The status to filter by
            
        Returns:
            List[Link]: List of links with the specified status
        """
        return [link for link in self.links if link.status == status]
    
    def get_links_summary(self) -> str:
        """
        Get a human-readable summary of the links
        
        Returns:
            A string summary of the links
        """
        if not self.links:
            return "No links have been tracked."
        
        summary = [f"# Links ({len(self.links)} total)"]
        
        # Group links by status
        status_groups = {}
        for link in self.links:
            if link.status not in status_groups:
                status_groups[link.status] = []
            status_groups[link.status].append(link)
        
        # Add links by status
        for status, links in status_groups.items():
            summary.append(f"\n## {status.capitalize()} ({len(links)})")
            for link in links:
                timestamp = link.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                summary.append(f"- [{link.url}] - {link.content} (tracked: {timestamp})")
        
        return "\n".join(summary)
    
    # Category methods
    def add_to_category(self, category: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add data to a specific category
        
        Args:
            category: The category to add the data to
            data: The data to add
            
        Returns:
            The updated data with added timestamp
        """
        if category not in self.categories:
            self.categories[category] = []
        
        # Add timestamp if not present
        if "timestamp" not in data:
            data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        self.categories[category].append(data)
        self.save_memory()
        return data
    
    def get_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all data for a specific category
        
        Args:
            category: The category to get data for
            
        Returns:
            List of data items in the category
        """
        return self.categories.get(category, [])
    
    def get_all_categories(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all categories and their data
        
        Returns:
            Dict mapping category names to lists of data items
        """
        return self.categories
    
    def clear_category(self, category: str) -> bool:
        """
        Clear all data in a specific category
        
        Args:
            category: The category to clear
            
        Returns:
            Boolean indicating success
        """
        if category in self.categories:
            self.categories[category] = []
            self.save_memory()
            return True
        return False


if __name__ == "__main__":
    # Example usage
    import sys
    
    # Get symbol from command line argument or use default
    symbol = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    
    # Initialize memory manager
    memory_manager = MemoryManager(symbol)
    
    # Print current memory
    print("\nCurrent Memory:")
    print(json.dumps(memory_manager.get_memory(), indent=2))
    
    # Add a test iteration
    test_iteration = {
        "iteration": 1,
        "focus": "financial_performance",
        "analysis": {
            "analysis_type": "financial_performance",
            "symbol": symbol,
            "sentiment": "positive",
            "confidence": "high",
            "key_points": ["Strong revenue growth", "High profit margins"]
        }
    }
    
    memory_manager.add_iteration(test_iteration)
    
    # Update focus area
    memory_manager.update_focus_area("competitive_analysis")
    
    # Test QA manager
    question = memory_manager.add_question("What is the revenue growth rate?")
    memory_manager.add_answer(question.id, "The revenue growth rate is 15% year-over-year.", "analysis")
    
    # Test Link manager
    memory_manager.add_link("https://example.com/financials", "visited", "Contains quarterly financial reports")
    
    # Test categories
    memory_manager.add_to_category("financial_metrics", {
        "metric": "revenue_growth",
        "value": "15%",
        "period": "YoY"
    })
    
    # Print updated memory
    print("\nUpdated Memory:")
    print(json.dumps(memory_manager.get_memory(), indent=2))
    
    print(f"\nMemory saved to: {memory_manager.memory_file}") 