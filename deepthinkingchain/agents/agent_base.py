"""
Base Agent class for DeepThinkingChain.

This module provides a base Agent class that can be extended to create
specialized agents for different tasks in the DeepThinkingChain system.
"""

import logging
import time
import os
from typing import Dict, Any, Union, List, Callable

# Import the existing PromptManager and PromptTemplate
from deepthinkingchain.prompts import PromptManager, PromptTemplate
from deepthinkingchain.memory import MemoryManager
from deepthinkingchain.constants import AgentType
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set the path to the prompts directory
PROMPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'prompts')
prompt_manager = PromptManager(PROMPTS_DIR)


class Agent:
    """
    Base Agent class for DeepThinkingChain.
    
    This class provides common functionality for all agents, including
    template processing, memory management, and execution flow control.
    """
    
    def __init__(self, prompt_template_name: str = None, prompt: str = None,
                memory_manager=None, model_name: str = 'openai/o3-mini'):
        """
        Initialize the Agent.
        
        Args:
            prompt_template_name: The name of the template to use, It should be in prompt_manager
            prompt: The actual template string if the user is not using prompt_manager
            memory_manager: Optional memory manager for saving agent results
        """
        self.model_name = model_name
        self.results = {}
        self.agent_type = AgentType.GENERIC
        self.next_step = None
        
        self.metadata = {
            "agent_name": self.__class__.__name__,
            "agent_type": self.agent_type,
        }
        logger.info(f"Initialized {self.__class__.__name__} with template '{prompt_template_name}'")
        
        ## deal with the prompt
        if prompt_template_name:
            self.template = prompt_manager.get_template(prompt_template_name)
            if self.template is None:
                logger.warning(f"Template '{prompt_template_name}' not found, using default")
                self.template = PromptTemplate("Default template")
        elif prompt:
            self.template = PromptTemplate(prompt)
        else:
            # for tools etc
            self.template = prompt_manager.get_template('user_intent')
            if self.template is None:
                logger.warning(f"Default template 'user_intent' not found, using empty template")
                self.template = PromptTemplate("Default template")
        
        ## deal with the memory manager
        if memory_manager is not None:
            if isinstance(memory_manager, str):
                # Treat as a file path to a memory JSON file
                memory_dir = os.path.dirname(memory_manager)
                memory_id = os.path.basename(memory_manager).split('_')[0]
                self.memory_manager = MemoryManager(memory_id=memory_id, memory_dir=memory_dir)
            elif isinstance(memory_manager, MemoryManager):
                # Already a MemoryManager instance
                self.memory_manager = memory_manager
            else:
                raise ValueError(f"Memory must be a MemoryManager instance, a path to a memory JSON file, or None, got {type(memory_manager)}")
        else:
            self.memory_manager = None

    def process_template(self, **kwargs) -> str:
        """
        Process the template by filling it with the provided data.
        most data should coming from the memory manager
        and there could be some additional data from the user
        
        Args:
            data: Dictionary of values to fill in the template
            
        Returns:
            str: The processed template with values filled in
        """
        placeholders = self.template.get_placeholders()

        # Create parameters dictionary
        parameters = {}
        
        # Get parameters from memory manager if available
        if self.memory_manager is not None:
            parameters.update(self.memory_manager._construct_parameters())
        
        # Add kwargs to the parameters
        parameters.update(kwargs)
        
        # Ensure all placeholders have values (use empty string as default)
        for placeholder in placeholders:
            if placeholder not in parameters:
                parameters[placeholder] = ""
        
        # Format the template
        prompt = self.template.format(**parameters)

        return prompt


    def _parse_results(self, results: Any) -> Dict[str, Any]:
        """
        Parse the raw results into a structured format.
        
        Args:
            results: The raw results to parse
            
        Returns:
            Dict[str, Any]: Parsed results as a dictionary
        """
        # format the results
        if isinstance(results, dict):
            return results
        else:
            return {
                "output": results
            }
        
    def save_to_memory(self) -> bool:
        """
        Save agent results to the memory system.
        
        Args:
            data: The data to save to memory
            key: Optional key to use for storage
            
        Returns:
            bool: True if saving was successful, False otherwise
        """

        try:
            # Add metadata
            data_with_metadata = {
                **self.results,
                "metadata": {
                    **self.metadata,
                }
            } 
            # Use memory manager to save
            success = self.memory_manager.add_iteration(self.agent_type, data_with_metadata)

            if success:
                logger.info(f"Successfully saved agent results to memory")
            else:
                logger.warning(f"Failed to save agent results to memory")
                
            return success
        except Exception as e:
            logger.error(f"Error saving to memory: {str(e)}")
            return False
    
    def run(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Run the agent with the provided arguments.
        
        This method handles common pre/post processing and calls the
        agent-specific _run method.
        
        Args:
            *args: Positional arguments to pass to _run
            **kwargs: Keyword arguments to pass to _run
            
        Returns:
            Dict[str, Any]: The results of running the agent
        """
        start_time = time.time()
        

        logger.info(f"Starting {self.__class__.__name__} agent")
        
        try:
            # Run the agent-specific implementation
            results = self._parse_results(self._run(*args, **kwargs))
            
            # Update the agent's results
            self.results.update(results)
                
            # Add execution metadata
            self.results["run_at"] = start_time
            self.results["execution_time"] = time.time() - start_time
            logger.info(f"Completed {self.__class__.__name__} agent in {self.results['execution_time']:.2f}s")
            
            return self.results
        except Exception as e:
            logger.error(f"Error running {self.__class__.__name__} agent: {str(e)}")
            return {
                "error": str(e),
                "run_at": start_time,
                "execution_time": time.time() - start_time
            }
    
    def _run(self, *args, **kwargs) -> Any:
        """
        Agent-specific implementation to be overridden by subclasses.
        
        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Any: Results of running the agent
            
        Raises:
            NotImplementedError: If the subclass does not implement this method
        """
        raise NotImplementedError("Subclasses must implement _run method")
    
    def set_next_step(self, next_step: Union[str, Callable, None]) -> None:
        """
        Set the next step in the workflow.
        
        Args:
            next_step: The next step to execute (string, function, or None)
        """
        self.next_step = next_step
    
    def get_next_step(self) -> Union[str, Callable, None]:
        """
        Get the next step in the workflow.
        
        Returns:
            Union[str, Callable, None]: The next step to execute
        """
        return self.next_step 