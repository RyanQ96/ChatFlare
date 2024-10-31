from abc import ABC, abstractmethod
from typing import Any, List, Dict, Tuple, Optional, Iterable, Union
from some_module import EmbeddingDocument, Document  # Replace `some_module` with the actual module where these are defined

class MemoryInterface(ABC):
    """Interface for interacting with a memory bank."""

    @abstractmethod
    def add_working_summary(self, texts: Iterable[str], metadatas: Optional[List[dict]] = None, ids: Optional[List[str]] = None, 
                            parent: Optional[List[Document]] = None, children: Optional[List[List[Document]]] = None, 
                            **kwargs: Any) -> List[str]:
        pass

    @abstractmethod
    def add_memory(self, texts: Iterable[str], metadatas: Optional[List[dict]] = None, ids: Optional[List[str]] = None, 
                   parent: Optional[List[Document]] = None, children: Optional[List[List[Document]]] = None, 
                   **kwargs: Any) -> List[str]:
        pass

    @abstractmethod
    def associate_in_memory(self, query: str, top_k: int = 4, **kwargs: Any) -> List[Tuple[EmbeddingDocument, float]]:
        pass

    @abstractmethod
    def get_inner_memories(self) -> List[Document]:
        pass

    @abstractmethod
    def get_leaf_memories(self) -> List[Document]:
        pass

    @abstractmethod
    def output_memories_hierarchy(self, inner_memories: Optional[List[Document]] = None) -> Dict[str, Any]:
        pass