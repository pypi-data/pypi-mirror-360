"""vLLM-based embedding provider for Qwen3 embeddings."""

from typing import Union, List, Optional
import numpy as np
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class VLLMEmbedder:
    """vLLM-based embeddings using Qwen3-Embedding models."""
    
    def __init__(
        self, 
        model_name: str = "Qwen/Qwen3-Embedding-0.6B",
        trust_remote_code: bool = True,
        max_model_len: int = 8192,
        dtype: str = "auto",
        gpu_memory_utilization: float = 0.9
    ):
        """Initialize vLLM embedder.
        
        Args:
            model_name: HuggingFace model name or local path
            trust_remote_code: Whether to trust remote code
            max_model_len: Maximum sequence length
            dtype: Data type for model weights
            gpu_memory_utilization: GPU memory to use (0-1)
        """
        self.model_name = model_name
        self.model: Optional['LLM'] = None
        self.trust_remote_code = trust_remote_code
        self.max_model_len = max_model_len
        self.dtype = dtype
        self.gpu_memory_utilization = gpu_memory_utilization
        
        # Check if model is downloaded
        self._init_model()
    
    def _init_model(self) -> None:
        """Initialize vLLM model."""
        try:
            from vllm import LLM
            
            # Initialize vLLM with embedding task
            self.model = LLM(
                model=self.model_name,
                task="embed",
                trust_remote_code=self.trust_remote_code,
                max_model_len=self.max_model_len,
                dtype=self.dtype,
                gpu_memory_utilization=self.gpu_memory_utilization
            )
            logger.info(f"Initialized vLLM with model: {self.model_name}")
            
        except ImportError:
            logger.error("vLLM not installed. Install with: pip install vllm>=0.8.5")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize vLLM model: {e}")
            raise
    
    def get_detailed_instruct(self, task_description: str, query: str) -> str:
        """Format instruction for Qwen3 embedding models.
        
        Args:
            task_description: Description of the retrieval task
            query: The query text
            
        Returns:
            Formatted instruction string
        """
        return f'Instruct: {task_description}\nQuery: {query}'
    
    def encode(
        self, 
        text: Union[str, List[str]],
        task_description: str = "Retrieve semantically similar Python code"
    ) -> Union[np.ndarray, List[np.ndarray]]:
        """Encode text to embeddings using vLLM.
        
        Args:
            text: Single text string or list of texts
            task_description: Task description for instruction
            
        Returns:
            Single embedding array or list of embedding arrays
        """
        if self.model is None:
            raise RuntimeError("vLLM model not initialized")
            
        # Handle single vs batch input
        if isinstance(text, str):
            texts = [text]
            single = True
        else:
            texts = text
            single = False
        
        # Format with instructions for better code search
        formatted_texts = [
            self.get_detailed_instruct(task_description, t) 
            for t in texts
        ]
        
        # Get embeddings from vLLM
        outputs = self.model.embed(formatted_texts)
        
        # Extract embeddings
        embeddings = [np.array(output.outputs.embedding) for output in outputs]
        
        return embeddings[0] if single else embeddings
    
    def encode_code(
        self,
        code: Union[str, List[str]],
        context: Optional[str] = None
    ) -> Union[np.ndarray, List[np.ndarray]]:
        """Specialized method for encoding code snippets.
        
        Args:
            code: Code snippet(s) to encode
            context: Optional context (e.g., "function", "class", "method")
            
        Returns:
            Embedding vector(s)
        """
        if context:
            task = f"Retrieve semantically similar Python {context}"
        else:
            task = "Retrieve semantically similar Python code"
            
        return self.encode(code, task_description=task)