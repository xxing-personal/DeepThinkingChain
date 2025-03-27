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

# Import AgentType from constants instead of defining IterationType
from .constants import AgentType

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
    
    def __init__(self, memory_id: str = None, memory_dir: str = "memory", name: str = None, max_iterations: int = 30):
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
        """Initialize a new memory structure for the analysis process.
        
        Returns:
            Dict containing the initialized memory structure
        """
        self.memory = {
            "id": self.memory_id,
            "name": self.name,
            "iteration_counter": 0,
            "max_iterations": self.max_iterations,
            "user_intent": "",
            "iterations": [],
            "completion_percentage": 0,
            "questions": [],
            "links": [],
            "summary": "",
        }
        self.save_memory()
        print(f"📝 Created new memory for {self.name} (ID: {self.memory_id})")
        return self.memory
    
    def save_memory(self) -> bool:
        """Save the current memory state to disk.
        
        Returns:
            Boolean indicating success or failure
        """
        try:            
            # Update sub-managers data
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
    
    def add_iteration(self, iteration_type: AgentType, iteration_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new iteration to the memory.
        
        Args:
            iteration_type: Type of agent that generated this iteration
            iteration_data: Dict containing the iteration data
        Returns:
            Dict containing the updated memory data
        """
        # Add the iteration and update completion percentage
        self.iteration_counter += 1
        self._update_completion_percentage()
        
        # add iteration summary
        full_result = "/n ".join(": ".join((str(k),str(v))) for k,v in iteration_data.items())
        
        # check if there is summary in iteration_Data
        if 'thinking' in iteration_data:
            thinking_str = iteration_data['thinking']
        else:
            if iteration_type == AgentType.TOOL:
                # cutoff tool result because it is too long
                thinking_str = full_result[:100]
            else:
                thinking_str = full_result

        self.memory["iterations"].append(iteration_type.value + "_" + str(self.iteration_counter) + ": \n" + thinking_str)

        # update user intent
        if 'user_intent' in iteration_data:
            self.memory["user_intent"] += "/n user_intent_" + str(self.iteration_counter) + ": \n" + iteration_data['user_intent']

        # deal with questions:
        if 'questions' in iteration_data:
            for question in iteration_data['questions']:
                # if answer exists, add it to the question
                if 'answer' in question:
                    self.add_answer(question['text'], question['answer'])
                else:
                    self.add_question(question['text'])
        
        # deal with links:
        if 'links' in iteration_data:
            for link in iteration_data['links']:
                # if visited, update the status
                if link['status'] == 'visited':
                    self.update_link_status(link['url'], link['status'], link['content'])
                else:
                    self.add_link(link['url'], link['status'], link['content'])
        # update summary:
        if 'summary' in iteration_data:
            self.memory["summary"] += iteration_data['summary']

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
        """Get the most recent iteration data.
        
        Returns:
            Dict containing the latest iteration data, or None if no iterations exist
        """
        iterations = self.memory.get("iterations", [])
        if iterations:
            return iterations[-1]
        return None
    
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
            export_file = f"exports/{self.memory_id}_memory_{timestamp}.json"
        
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
    def add_question(self, text: str) -> Question:
        """
        Add a new question to track
        
        Args:
            text: The question text
            
        Returns:
            Question: The created question object
        """
        question = Question(
            id=str(uuid4()),
            text=text
        )
        self.questions.append(question)
        self.save_memory()
        return question
    
    def get_questions_by_status(self, status: Optional[bool] = None) -> List[Question]:
        """
        Get questions filtered by their type
        
        Args:
            is_original: If True, returns original questions. If False, returns follow-up questions.
                         If None, returns all questions.
            
        Returns:
            List[Question]: List of questions matching the specified type
        """
        if status is None:
            return self.questions
        return [q for q in self.questions if q.status == status]
    
    def add_answer(self, question_identifier: str, text: str) -> str:
        """
        Add an answer to a question
        
        Args:
            question_identifier: Either the ID or the text of the question to answer
            text: The answer text
            
        Returns:
            The answer text
        """
        # Try to find the question by ID first
        for question in self.questions:
            if question.id == question_identifier:
                answer = question.add_answer(text)
                self.save_memory()
                return answer
        
        # If not found by ID, try to find by text
        for question in self.questions:
            if question.text == question_identifier:
                answer = question.add_answer(text)
                self.save_memory()
                return answer
        
        raise ValueError(f"Question with ID or text '{question_identifier}' not found")
    
    def get_question_answers(self, question_id: str) -> List[str]:
        """
        Get all answers for a specific question
        
        Args:
            question_id: The ID of the question
            
        Returns:
            List[str]: List containing the answer string for backward compatibility
        """
        for question in self.questions:
            if question.id == question_id:
                # Return as a list with a single item for backward compatibility
                return [question.answer] if question.answer else []
        return []
    
    def get_qa_summary(self, show_unsolved: bool = False) -> str:
        """
        Get a human-readable summary of the QA manager's state
        
        Args:
            show_unsolved: Whether to include unsolved questions in the summary
            
        Returns:
            A string summary of the QA manager's state
        """
        if not self.questions:
            return "No questions have been asked."
            
        summary = [f"# Questions and Answers ({len(self.questions)} questions)"]

        for question in self.questions:
            if show_unsolved or question.status == "answered":
                status_marker = "✓" if question.status == "answered" else "❓"
                summary.append(f"\n### {status_marker} {question.text}")

                if question.answer:
                    summary.append(f"**Answer**: {question.answer}")
                else:
                    summary.append("*No answer yet*")
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
            content=content
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
                summary.append(f"- [{link.url}] - {link.content}")
        
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
        if self.questions:
            output_dict["unsolved_questions"] = [q.text for q in self.get_questions_by_status(status="pending")]
            output_dict["solved_questions"] = self.get_qa_summary(show_unsolved=False)
            output_dict["all_questions_status"] = [q.text + " (" + q.status + ")" for q in self.questions]
        if self.links:
            output_dict["unvisted_link"] = [l.url for l in self.links if l.status == "pending"]
            output_dict["visited_link"] = [l.url for l in self.links if l.status == "visited"]
            output_dict["failed_link"] = [l.url for l in self.links if l.status == "failed"]
        return output_dict
    
 



