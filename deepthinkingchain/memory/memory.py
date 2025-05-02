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
from enum import Enum

from deepthinkingchain.constants import AgentType

@dataclass
class Question:
    """A question and its answers in the QA system."""
    
    id: str
    text: str
    status: str = "pending"  # pending, answered, failed
    answer: str = ""  # Answer text as a single string
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Question to a dictionary for serialization"""
        return {
            "id": self.id,
            "text": self.text,
            "status": self.status,
            "answer": self.answer
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Question':
        """Create a Question from a dictionary"""
        question = cls(
            id=data["id"],
            text=data["text"],
            status=data["status"]
        )
        
        # Handle answer field
        if "answer" in data:
            # New format - single string
            question.answer = data["answer"]
        else:
            question.answer = ""
            
        return question
    
    def add_answer(self, text: str) -> str:
        """
        Add an answer to this question
        
        Args:
            text: The answer text
            
        Returns:
            The answer text
        """
        if self.answer:
            # If there's already an answer, append with a separator
            self.answer += "/n " + text
        else:
            # First answer
            self.answer = text
        self.status = "answered"
        return text
    
    def get_latest_answer(self) -> Optional[str]:
        """
        Get the most recent answer for this question
        
        Returns:
            Optional[str]: The answer, or None if no answer
        """
        if not self.answer:
            return None
        return self.answer


@dataclass
class Link:
    """A link and its metadata in the link tracking system."""
    
    id: str
    url: str
    status: str  # pending, visited, failed, etc.
    content: str  # one sentence summary of the content
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Link to a dictionary for serialization"""
        return {
            "id": self.id,
            "url": self.url,
            "status": self.status,
            "content": self.content
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Link':
        """Create a Link from a dictionary"""
        # Extract only the fields we need, ignoring timestamp if present (for backward compatibility)
        return cls(
            id=data["id"],
            url=data["url"],
            status=data["status"],
            content=data["content"]
        )


class MemoryManager:
    """Manages memory operations for the DeepThinkingChain analysis process.
    
    This class provides methods to load, update, and save memory for each analysis cycle,
    ensuring persistence of analysis state across runs and iterations.
    """
    
    def __init__(self, memory_id: str = None, memory_dir: str = "memory/history_memo", name: str = None, max_iterations: int = 30):
        """Initialize the MemoryManager for a specific analysis ID.
        
        Args:
            memory_id: The unique identifier for this memory instance
            memory_dir: Directory where memory files are stored (default: 'memory')
            name: Optional human-readable name for this memory instance
        """
        self.memory_id = memory_id or str(uuid4())
        self.name = name or memory_id
        self.memory_dir = memory_dir
        self.memory_file = f"{memory_dir}/{self.memory_id}_memory.json"
        self.max_iterations = max_iterations
        self.memory = {}
        
        # Initialize sub-managers
        self.questions: List[Question] = []
        self.links: List[Link] = []
        self.iteration_counter = 0
        
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
                print(f"📂 Loaded existing memory for {self.name} (ID: {self.memory_id})")
                
                # Load sub-managers data if available
                if "questions" in self.memory:
                    self.questions = [Question.from_dict(q) for q in self.memory["questions"]]
                if "links" in self.memory:
                    self.links = [Link.from_dict(l) for l in self.memory["links"]]
                self.categories = self.memory.keys()
                
            except json.JSONDecodeError:
                print(f"⚠️ Error loading memory file. Creating new memory.")
                self._initialize_memory()
        else:
            self._initialize_memory()
        
        return self.memory
    
    def _initialize_memory(self) -> Dict[str, Any]:
        """Initialize a new memory structure with only essential fields.
        
        Returns:
            Dict containing the minimal initialized memory structure
        """
        self.memory = {
            "id": self.memory_id,
            "name": self.name,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
            "completion_percentage": 0.0,
            "summary": "",
            "max_iterations": self.max_iterations,
            "iteration_counter": 0,
            "iterations": [],
            # Empty container for dynamically added data
            "data": {}
        }
        self.save_memory()
        return self.memory
    
    def save_memory(self) -> bool:
        """Save the current memory state to disk.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Update any sub-manager data in memory
            self.memory["questions"] = [q.to_dict() for q in self.questions]
            self.memory["links"] = [l.to_dict() for l in self.links]
            
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=2)
            return True
        except Exception as e:
            print(f"⚠️ Error saving memory: {str(e)}")
            return False
    
    def get_memory(self) -> Dict[str, Any]:
        """Get the current memory state.
        
        Returns:
            Dict containing the current memory state
        """
        return self.memory
    
    def update_memory(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update the memory with new key-value pairs.
        
        Args:
            updates: Dictionary of updates to apply to memory
            
        Returns:
            Dict containing the updated memory
        """
        # Update memory with new data
        for key, value in updates.items():
            self.memory[key] = value
        
        # Save changes to disk
        self.save_memory()
        
        return self.memory
    
    def ensure_field(self, field_path: str, default_value: Any = None) -> Any:
        """Ensure a field exists in the memory structure, creating it if necessary.
        
        This method allows dynamically adding fields to the memory structure as needed,
        rather than having to define all fields upfront.
        
        Args:
            field_path: Dot-notation path to the field (e.g., "data.iterations.0.result")
            default_value: Default value to use if the field doesn't exist
            
        Returns:
            The current value of the field (or the default if newly created)
        """
        # Split the path into components
        components = field_path.split('.')
        
        # Start at the root of the memory
        current = self.memory
        
        # Navigate to the parent of the target field
        for i, component in enumerate(components[:-1]):
            # If we need to index into a list
            if component.isdigit() and isinstance(current, list):
                index = int(component)
                # Extend the list if necessary
                while len(current) <= index:
                    current.append({})
                current = current[index]
            else:
                # If the component doesn't exist yet, create it
                if component not in current:
                    # If the next component is a digit, create a list
                    if i+1 < len(components) and components[i+1].isdigit():
                        current[component] = []
                    else:
                        current[component] = {}
                current = current[component]
        
        # Set the final field if it doesn't exist
        last_component = components[-1]
        if last_component.isdigit() and isinstance(current, list):
            index = int(last_component)
            # Extend the list if necessary
            while len(current) <= index:
                current.append(default_value if default_value is not None else {})
            if current[index] is None:
                current[index] = default_value
            return current[index]
        else:
            if last_component not in current:
                current[last_component] = default_value
            return current[last_component]
    
    def add_iteration(self, iteration_type: AgentType, iteration_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new iteration to the memory.
        
        Args:
            iteration_type: Type of agent that generated this iteration
            iteration_data: Dict containing the iteration data
        Returns:
            Dict containing the updated memory data
        """
        # Ensure the iterations array exists
        iterations = self.ensure_field("data.iterations", [])
        
        # Create a new iteration entry
        iteration_entry = {
            "type": str(iteration_type),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "data": iteration_data
        }
        
        # Add the iteration to the list
        iterations.append(iteration_entry)
        
        # Update the last_updated timestamp
        self.memory["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Update completion percentage if present in the data
        if "completion_percentage" in iteration_data:
            self.ensure_field("data.completion_percentage", iteration_data["completion_percentage"])
        
        # Extract and store questions if present
        if "questions" in iteration_data:
            questions = self.ensure_field("data.questions", [])
            for question in iteration_data["questions"]:
                if question not in questions:
                    questions.append(question)
        
        # Extract and store summary information if present
        if "summary" in iteration_data:
            self.ensure_field("data.summary", "")
            self.memory["data"]["summary"] += f"\n{iteration_data['summary']}"
            
        # Save changes to disk
        self.save_memory()
        
        return self.memory
    
    def _update_completion_percentage(self, new_completion_percentage: float = None) -> float:
        """Update the analysis completion percentage based on iterations and focus areas.
        
        Args:
            new_completion_percentage: Optional new completion percentage to set
            
        Returns:
            Float representing the completion percentage
        """
        
        current_percentage = self.memory.get("completion_percentage", 0)
        
        # Use the new percentage if provided, otherwise keep the current one
        if new_completion_percentage is not None:
            completion_percentage = max(new_completion_percentage, current_percentage)
        else:
            completion_percentage = current_percentage
            
        max_iterations = self.memory.get("max_iterations", 5)
        iterations = self.memory.get("iterations", [])
        
        if len(iterations) > max_iterations:
            completion_percentage = 1            
        # Update memory
        self.memory["completion_percentage"] = round(completion_percentage, 2)
        
        return self.memory["completion_percentage"]
    
    def get_latest_iteration(self) -> Optional[Dict[str, Any]]:
        """Get the most recent iteration from memory.
        
        Returns:
            Dict containing the latest iteration, or None if no iterations
        """
        iterations = self.memory.get("iterations", [])
        if not iterations:
            return None
        return iterations[-1]
    
    def clear_memory(self) -> bool:
        """Clear all memory data and reset to initial state.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Preserve ID and name
            memory_id = self.memory_id
            name = self.name
            
            # Re-initialize memory
            self._initialize_memory()
            
            return True
        except Exception as e:
            print(f"⚠️ Error clearing memory: {str(e)}")
            return False
    
    def export_memory(self, export_file: Optional[str] = None) -> str:
        """Export memory to a JSON file.
        
        Args:
            export_file: File path for export, defaults to timestamped file
            
        Returns:
            str: Path to the export file
        """
        if not export_file:
            # Create timestamped export filename
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            export_file = f"{self.memory_dir}/export_{self.memory_id}_{timestamp}.json"
        
        try:
            # Export memory
            with open(export_file, 'w') as f:
                json.dump(self.memory, f, indent=2)
            
            print(f"📤 Exported memory to {export_file}")
            return export_file
        except Exception as e:
            print(f"⚠️ Error exporting memory: {str(e)}")
            return ""
    
    # Question management methods
    
    def add_question(self, text: str) -> Question:
        """Add a new question to the system.
        
        Args:
            text: The question text
            
        Returns:
            Question: The created Question object
        """
        # Create new question
        question = Question(id=str(uuid4()), text=text)
        
        # Add to questions list
        self.questions.append(question)
        
        # Update memory and save
        self.memory["questions"] = [q.to_dict() for q in self.questions]
        self.save_memory()
        
        return question
    
    def get_questions_by_status(self, status: Optional[str] = None) -> List[Question]:
        """Get questions filtered by status.
        
        Args:
            status: Status to filter by (or None for all questions)
            
        Returns:
            List of Question objects
        """
        if status:
            return [q for q in self.questions if q.status == status]
        return self.questions
    
    def add_answer(self, question_identifier: str, text: str) -> str:
        """Add an answer to a question.
        
        Args:
            question_identifier: ID or text of the question
            text: The answer text
            
        Returns:
            str: The answer text, or empty string if question not found
        """
        # Find question by ID or text
        question = None
        for q in self.questions:
            if q.id == question_identifier or q.text == question_identifier:
                question = q
                break
        
        if not question:
            print(f"⚠️ Question not found: {question_identifier}")
            return ""
        
        # Add answer
        answer = question.add_answer(text)
        
        # Update memory and save
        self.memory["questions"] = [q.to_dict() for q in self.questions]
        self.save_memory()
        
        return answer
    
    def get_question_answers(self, question_id: str) -> List[str]:
        """Get all answers for a specific question.
        
        Args:
            question_id: ID of the question
            
        Returns:
            List of answer texts
        """
        # Find question by ID
        for q in self.questions:
            if q.id == question_id:
                if not q.answer:
                    return []
                # Split by the newline separator
                return q.answer.split("/n ")
        
        return []
    
    def get_qa_summary(self, show_unsolved: bool = False) -> str:
        """Get a summary of questions and answers.
        
        Args:
            show_unsolved: Whether to include unanswered questions
            
        Returns:
            str: Formatted summary text
        """
        if not self.questions:
            return "No questions found."
        
        # Filter questions
        if not show_unsolved:
            questions = [q for q in self.questions if q.status == "answered"]
        else:
            questions = self.questions
        
        # Generate summary
        summary = []
        for i, q in enumerate(questions):
            if q.status == "answered":
                summary.append(f"Q{i+1}: {q.text}")
                summary.append(f"A: {q.answer}")
                summary.append("")
            elif show_unsolved:
                summary.append(f"Q{i+1}: {q.text}")
                summary.append("A: [Not yet answered]")
                summary.append("")
        
        return "\n".join(summary)
    
    # Link tracking methods
    
    def add_link(self, url: str, status: str = "pending", content: str = "") -> Link:
        """Add a new link to the tracking system.
        
        Args:
            url: The URL to track
            status: Initial status (default: pending)
            content: Optional content summary
            
        Returns:
            Link: The created Link object
        """
        # Create new link
        link = Link(id=str(uuid4()), url=url, status=status, content=content)
        
        # Add to links list
        self.links.append(link)
        
        # Update memory and save
        self.memory["links"] = [l.to_dict() for l in self.links]
        self.save_memory()
        
        return link
    
    def get_link_by_url(self, url: str) -> Optional[Link]:
        """Get a link by its URL.
        
        Args:
            url: The URL to find
            
        Returns:
            Link object or None if not found
        """
        for link in self.links:
            if link.url == url:
                return link
        return None
    
    def update_link_status(self, url: str, status: str, content: str = None) -> Optional[Link]:
        """Update a link's status and optionally its content.
        
        Args:
            url: The URL to update
            status: New status
            content: Optional new content summary
            
        Returns:
            Updated Link object or None if not found
        """
        link = self.get_link_by_url(url)
        if not link:
            return None
        
        # Update link
        link.status = status
        if content is not None:
            link.content = content
        
        # Update memory and save
        self.memory["links"] = [l.to_dict() for l in self.links]
        self.save_memory()
        
        return link
    
    def get_links_by_status(self, status: str) -> List[Link]:
        """Get links filtered by status.
        
        Args:
            status: Status to filter by
            
        Returns:
            List of Link objects
        """
        return [l for l in self.links if l.status == status]
    
    def get_links_summary(self) -> str:
        """Get a summary of tracked links.
        
        Returns:
            str: Formatted summary text
        """
        if not self.links:
            return "No links tracked."
        
        # Generate summary
        summary = []
        
        # Group by status
        status_groups = {}
        for link in self.links:
            if link.status not in status_groups:
                status_groups[link.status] = []
            status_groups[link.status].append(link)
        
        # Format summary
        for status, links in status_groups.items():
            summary.append(f"{status.capitalize()} Links:")
            for i, link in enumerate(links):
                summary.append(f"{i+1}. {link.url}")
                if link.content:
                    summary.append(f"   Summary: {link.content}")
            summary.append("")
        
        return "\n".join(summary)
    
    def _construct_parameters(self) -> Dict[str, Any]:
        """Output all parameters of the memory manager.
        
        Returns:
            Dictionary containing all parameters of the memory manager
        """
        output_dict = {}
        if self.memory:
            output_dict["user_intent"] = self.memory["user_intent"]
            output_dict["completion_percentage"] = self.memory["completion_percentage"]
            output_dict["summary"] = self.memory["summary"]
            output_dict["remaining_iterations"] = self.memory["max_iterations"] - self.memory["iteration_counter"]
            output_dict["iterations"] = "/n ".join(self.memory["iterations"])
            output_dict["summary"] = self.memory["summary"]
            output_dict["last_iteration"] = self.get_latest_iteration()
        if self.questions:
            output_dict["unsolved_questions"] = [q.text for q in self.get_questions_by_status(status="pending")]
            output_dict["solved_questions"] = self.get_qa_summary(show_unsolved=False)
            output_dict["all_questions_status"] = [q.text + " (" + q.status + ")" for q in self.questions]
        if self.links:
            output_dict["unvisted_link"] = [l.url for l in self.links if l.status == "pending"]
            output_dict["visited_link"] = [l.url for l in self.links if l.status == "visited"]
            output_dict["failed_link"] = [l.url for l in self.links if l.status == "failed"]
        return output_dict

    def get_completeness_percent(self) -> float:
        """Get the current completion percentage of the analysis.
        
        Returns:
            float: Completion percentage between 0 and 100
        """
        # Get the current completion percentage from memory
        completion = self.memory.get("completion_percentage", 0.0)
        
        # Ensure the value is between 0 and 100
        return max(0.0, min(100.0, float(completion)))

    def update_completion_percentage(self, new_percentage: float) -> float:
        """Update the completion percentage of the analysis.
        
        Args:
            new_percentage: New completion percentage (0-100)
            
        Returns:
            float: Updated completion percentage
        """
        # Ensure the value is between 0 and 100
        new_percentage = max(0.0, min(100.0, float(new_percentage)))
        
        # Update the memory
        self.memory["completion_percentage"] = new_percentage
        
        # Save the updated memory
        self.save_memory()
        
        return new_percentage

    def set_next_step(self, step: str) -> None:
        """Set the next step in the analysis workflow.
        
        Args:
            step: The name of the next step
        """
        self.memory["next_step"] = step
        self.save_memory()