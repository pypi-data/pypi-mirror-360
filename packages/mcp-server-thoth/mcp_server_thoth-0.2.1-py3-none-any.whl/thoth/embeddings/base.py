"""Base embedding provider protocol."""

from typing import Protocol, Union, List
import numpy as np


class EmbeddingProvider(Protocol):
    """Protocol for embedding providers."""
    
    def encode(
        self, 
        text: Union[str, List[str]]
    ) -> Union[np.ndarray, List[np.ndarray]]:
        """Encode text to embedding vector(s).
        
        Args:
            text: Single text string or list of texts
            
        Returns:
            Single embedding array or list of embedding arrays
        """
        ...