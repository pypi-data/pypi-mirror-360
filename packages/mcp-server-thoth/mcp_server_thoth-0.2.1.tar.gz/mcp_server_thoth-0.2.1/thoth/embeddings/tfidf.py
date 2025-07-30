"""TF-IDF based embedder as lightweight fallback."""

from typing import Union, List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import logging

logger = logging.getLogger(__name__)


class TfidfEmbedder:
    """Lightweight TF-IDF based embedder as fallback."""
    
    def __init__(self, max_features: int = 512):
        self.max_features = max_features
        self.vectorizer = TfidfVectorizer(max_features=max_features)
        self.fitted = False
        self.documents: List[str] = []
    
    def encode(
        self, 
        text: Union[str, List[str]]
    ) -> Union[np.ndarray, List[np.ndarray]]:
        """Encode text using TF-IDF.
        
        Args:
            text: Single text string or list of texts
            
        Returns:
            Single embedding array or list of embedding arrays
        """
        if isinstance(text, str):
            texts = [text]
            single = True
        else:
            texts = text
            single = False
            
        if not self.fitted:
            # Return zeros for unfitted vectorizer
            embeddings = [np.zeros(self.max_features) for _ in texts]
        else:
            # Transform using fitted vectorizer
            vec = self.vectorizer.transform(texts)
            embeddings = [vec[i].toarray()[0] for i in range(vec.shape[0])]
        
        return embeddings[0] if single else embeddings
    
    def fit(self, documents: List[str]) -> None:
        """Fit TF-IDF on documents.
        
        Args:
            documents: List of text documents to fit on
        """
        self.documents = documents
        if documents:
            self.vectorizer.fit(documents)
            self.fitted = True
            logger.info(f"TF-IDF fitted on {len(documents)} documents")