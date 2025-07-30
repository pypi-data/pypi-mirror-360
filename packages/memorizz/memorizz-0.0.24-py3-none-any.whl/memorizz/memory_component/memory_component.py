from .conversational_memory_component import ConversationMemoryComponent
from ..memory_provider import MemoryProvider
from ..memory_provider.memory_type import MemoryType
from .application_mode import ApplicationMode, ApplicationModeConfig
from ..embeddings.openai import get_embedding
from typing import TYPE_CHECKING, Dict, Any, List, Optional
import time
import numpy as np
import pprint

# Use lazy initialization for OpenAI
def get_openai_llm():
    from ..llms.openai import OpenAI
    return OpenAI()

class MemoryComponent:
    def __init__(self, application_mode: str, memory_provider: MemoryProvider = None):
        # Validate and set the application mode
        if isinstance(application_mode, str):
            self.application_mode = ApplicationModeConfig.validate_mode(application_mode)
        else:
            self.application_mode = application_mode
            
        self.memory_provider = memory_provider
        self.query_embedding = None
        
        # Get the memory types for this application mode
        self.active_memory_types = ApplicationModeConfig.get_memory_types(self.application_mode)

    def generate_memory_component(self, content: dict):
        """
        Generate the memory component based on the application mode.
        The memory component type is determined by the content and active memory types.
        """

        # Generate the embedding of the memory component
        content["embedding"] = get_embedding(content["content"])

        # Determine the appropriate memory component type based on content and active memory types
        if MemoryType.CONVERSATION_MEMORY in self.active_memory_types and "role" in content:
            return self._generate_conversational_memory_component(content)
        elif MemoryType.WORKFLOW_MEMORY in self.active_memory_types:
            return self._generate_workflow_memory_component(content)
        elif MemoryType.LONG_TERM_MEMORY in self.active_memory_types:
            return self._generate_knowledge_base_component(content)
        else:
            # Default to conversational if available, otherwise use the first active memory type
            if MemoryType.CONVERSATION_MEMORY in self.active_memory_types:
                return self._generate_conversational_memory_component(content)
            else:
                raise ValueError(f"No suitable memory component type for application mode: {self.application_mode.value}")

    def _generate_conversational_memory_component(self, content: dict) -> ConversationMemoryComponent:
        """
        Generate the conversational memory component.
        
        Parameters:
            content (dict): The content of the memory component.

        Returns:
            ConversationMemoryComponent: The conversational memory component.
        """
        memory_component = ConversationMemoryComponent(
            role=content["role"],
            content=content["content"],
            timestamp=content["timestamp"],
            conversation_id=content["conversation_id"],
            memory_id=content["memory_id"],
            embedding=content["embedding"]
        )

        # Save the memory component to the memory provider
        self._save_memory_component(memory_component, MemoryType.CONVERSATION_MEMORY)

        return memory_component

    def _generate_workflow_memory_component(self, content: dict):
        """
        Generate a workflow memory component.
        
        Parameters:
            content (dict): The content of the memory component.
            
        Returns:
            dict: The workflow memory component.
        """
        workflow_component = {
            "content": content["content"],
            "timestamp": content.get("timestamp", time.time()),
            "memory_id": content["memory_id"],
            "embedding": content["embedding"],
            "component_type": "workflow",
            "workflow_step": content.get("workflow_step", "unknown"),
            "task_id": content.get("task_id"),
        }
        
        # Save the memory component to the memory provider
        self._save_memory_component(workflow_component, MemoryType.WORKFLOW_MEMORY)
        
        return workflow_component

    def _generate_knowledge_base_component(self, content: dict):
        """
        Generate a knowledge base (long-term memory) component.
        
        Parameters:
            content (dict): The content of the memory component.
            
        Returns:
            dict: The knowledge base memory component.
        """
        knowledge_component = {
            "content": content["content"],
            "timestamp": content.get("timestamp", time.time()),
            "memory_id": content["memory_id"],
            "embedding": content["embedding"],
            "component_type": "knowledge",
            "category": content.get("category", "general"),
            "importance": content.get("importance", 0.5),
        }
        
        # Save the memory component to the memory provider
        self._save_memory_component(knowledge_component, MemoryType.LONG_TERM_MEMORY)
        
        return knowledge_component
    
    def _save_memory_component(self, memory_component: any, memory_type: MemoryType = None):
        """
        Save the memory component to the memory provider.
        
        Parameters:
            memory_component: The memory component to save
            memory_type: Specific memory type to save to (optional)
        """

        # Remove the score(vector similarity score calculated by the vector search of the memory provider) from the memory component if it exists
        if isinstance(memory_component, dict) and "score" in memory_component:
            memory_component.pop("score", None)

        # Convert Pydantic model to dictionary if needed
        if hasattr(memory_component, 'model_dump'):
            memory_component_dict = memory_component.model_dump()
        elif hasattr(memory_component, 'dict'):
            memory_component_dict = memory_component.dict()
        else:
            # If it's already a dictionary, use it as is
            memory_component_dict = memory_component

        # If memory_type is not specified, determine from the component or use conversation as default
        if memory_type is None:
            if MemoryType.CONVERSATION_MEMORY in self.active_memory_types:
                memory_type = MemoryType.CONVERSATION_MEMORY
            else:
                # Use the first available memory type from active types
                memory_type = self.active_memory_types[0] if self.active_memory_types else MemoryType.CONVERSATION_MEMORY

        # Validate that the memory type is active for this application mode
        if memory_type not in self.active_memory_types:
            print(f"Warning: Memory type {memory_type.value} not active for application mode {self.application_mode.value}")

        print(f"Storing memory component of type {memory_type.value} in memory provider")
        print(f"Memory component data: {memory_component_dict}")
        stored_id = self.memory_provider.store(memory_component_dict, memory_type)
        print(f"Stored memory component with ID: {stored_id}")
        return stored_id

    def retrieve_memory_components_by_memory_id(self, memory_id: str, memory_type: MemoryType):
        """
        Retrieve the memory components by memory id.

        Parameters:
            memory_id (str): The id of the memory to retrieve the memory components for.
            memory_type (MemoryType): The type of the memory to retrieve the memory components for.

        Returns:
            List[MemoryComponent]: The memory components.
        """
        if memory_type == MemoryType.CONVERSATION_MEMORY:
            return self.memory_provider.retrieve_conversation_history_ordered_by_timestamp(memory_id)
        elif memory_type == MemoryType.TASK_MEMORY:
            return self.memory_provider.retrieve_task_history_ordered_by_timestamp(memory_id)
        elif memory_type == MemoryType.WORKFLOW_MEMORY:
            return self.memory_provider.retrieve_workflow_history_ordered_by_timestamp(memory_id)
        else:
            raise ValueError(f"Invalid memory type: {memory_type}")

    def retrieve_memory_components_by_conversation_id(self, conversation_id: str):
        pass

    def retrieve_memory_components_by_query(self, query: str, memory_id: str, memory_type: MemoryType, limit: int = 5):
        """
        Retrieve the memory components by query.

        Parameters:
            query (str): The query to use for retrieval.
            memory_id (str): The id of the memory to retrieve the memory components for.
            memory_type (MemoryType): The type of the memory to retrieve the memory components for.
            limit (int): The limit of the memory components to return.

        Returns:
            List[MemoryComponent]: The memory components.
        """

        # Create the query embedding here so that it is not created for each memory component
        self.query_embedding = get_embedding(query)

        # Get the memory components by query
        memory_components = self.memory_provider.retrieve_memory_components_by_query(query, self.query_embedding, memory_id, memory_type, limit)

        # Get the surronding conversation ids from each of the memory components
        # Handle cases where conversation_id might be missing or _id is used instead
        surrounding_conversation_ids = []
        for memory_component in memory_components:
            surrounding_conversation_ids.append(memory_component["_id"])

        # Before returning the memory components, we need to update the memory signals within the memory components
        for memory_component in memory_components:
            self.update_memory_signals_within_memory_component(memory_component, memory_type, surrounding_conversation_ids)

        # Calculate the memory signal for each of the memory components
        for memory_component in memory_components:
            memory_component["memory_signal"] = self.calculate_memory_signal(memory_component, query)

        # Sort the memory components by the memory signal
        memory_components.sort(key=lambda x: x["memory_signal"], reverse=True)

        # Return the memory components
        return memory_components
    

    def update_memory_signals_within_memory_component(self, memory_component: any, memory_type: MemoryType, surrounding_conversation_ids: list[str]):
        """
        Update the memory signal within the memory component.

        Parameters:
            memory_component (dict): The memory component to update the memory signal within.
            memory_type (MemoryType): The type of the memory to update the memory signal within.
            surrounding_conversation_ids (list[str]): The list of surrounding conversation ids.
        """

        # Update the recall_recency field (how recently the memory component was recalled), this is the current timestamp
        memory_component["recall_recency"] = time.time()

        if memory_type == MemoryType.CONVERSATION_MEMORY:
            # Update the importance field with a list of calling ID and surronding conversation ID's
            memory_component["associated_conversation_ids"] = surrounding_conversation_ids

        # Save the memory component to the memory provider
        self._save_memory_component(memory_component)

    def calculate_memory_signal(self, memory_component: any, query: str):
        """
        Calculate the memory signal within the memory component.

        Parameters:
            memory_component (any): The memory component to calculate the memory signal within.
            query (str): The query to use for calculation.

        Returns:
            float: The memory signal between 0 and 1.
        """
        # Detect the gap between the current timestamp and the recall_recency field
        recency = time.time() - memory_component["recall_recency"]

        # Get the number of associated memory ids (this is used to calcualte the importance of the memory component)
        number_of_associated_conversation_ids = len(memory_component["associated_conversation_ids"])

        # If the score exists, use it as the relevance score (this is the vector similarity score calculated by the vector search of the memory provider)
        if "score" in memory_component:
            relevance = memory_component["score"]
        else:
            # Calculate the relevance of the memory component which is a vector score between the memory component and the query
            relevance = self.calculate_relevance(query, memory_component)

        # Calulate importance of the memory component
        importance = self.calculate_importance(memory_component["content"], query)

        # Calculate the normalized memory signal
        memory_signal = recency * number_of_associated_conversation_ids * relevance * importance

        # Normalize the memory signal between 0 and 1
        memory_signal = memory_signal / 100

        # Return the memory signal
        return memory_signal

    def calculate_relevance(self, query: str, memory_component: any) -> float:
        """
        Calculate the relevance of the query with the memory component.

        Parameters:
            query (str): The query to use for calculation.
            memory_component (any): The memory component to calculate the relevance within.

        Returns:
            float: The relevance between 0 and 1.
        """
        # Get embedding of the query
        if self.query_embedding is None:
            self.query_embedding = get_embedding(query)

        # Get embedding of the memory component if it is not already embedded
        if memory_component["embedding"] is None:
            memory_component_embedding = get_embedding(memory_component["content"])
        else:
            memory_component_embedding = memory_component["embedding"]

        # Calculate the cosine similarity between the query embedding and the memory component embedding
        relevance = self.cosine_similarity(self.query_embedding, memory_component_embedding)

        # Return the relevance
        return relevance
        

    # We might not need this as the memory compoennt should have a score from retrieval
    def cosine_similarity(self, query_embedding: list[float], memory_component_embedding: list[float]) -> float:
        """
        Calculate the cosine similarity between two embeddings.

        Parameters:
            query_embedding (list[float]): The query embedding.
            memory_component_embedding (list[float]): The memory component embedding.

        Returns:
            float: The cosine similarity between the two embeddings.
        """
        # Calculate the dot product of the two embeddings
        dot_product = np.dot(query_embedding, memory_component_embedding)

        # Calculate the magnitude of the two embeddings
        magnitude_query_embedding = np.linalg.norm(query_embedding)
        magnitude_memory_component_embedding = np.linalg.norm(memory_component_embedding)

        # Calculate the cosine similarity
        cosine_similarity = dot_product / (magnitude_query_embedding * magnitude_memory_component_embedding)

        # Return the cosine similarity
        return cosine_similarity


    def calculate_importance(self, memory_component_content: str, query: str) -> float:
        """
        Calculate the importance of the memory component.
        Using an LLM to calculate the importance of the memory component.

        Parameters:
            memory_component_content (str): The content of the memory component to calculate the importance within.
            query (str): The query to use for calculation.

        Returns:
            float: The importance between 0 and 1.
        """
   

        importance_prompt = f"""
        Calculate the importance of the following memory component:
        {memory_component_content}
        in relation to the following query and rate the likely poignancy of the memory component:
        {query}
        Return the importance of the memory component as a number between 0 and 1.
        """

        # Get the importance of the memory component
        importance = get_openai_llm().generate_text(importance_prompt, instructions="Return the importance of the memory component as a number between 0 and 1. No other text or comments, just the number. For example: 0.5")

        # Return the importance
        return float(importance)

