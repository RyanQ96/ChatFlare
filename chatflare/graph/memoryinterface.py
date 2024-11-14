from abc import ABC, abstractmethod
from typing import Any, List, Dict, Tuple, Optional, Iterable, Union
# from some_module import EmbeddingDocument, Document  # Replace `some_module` with the actual module where these are defined

class EmbeddingDocument: 
    pass 

class Document:
    pass


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

    @abstractmethod
    def add_memory_from_commit(self, commit): 
        pass

    @abstractmethod
    def delete(self, ids: List[str]) -> bool:
        pass

    @abstractmethod 
    def get_new_memory_from_ids(self, ids: List[str]) -> "MemoryInterface":
        pass    
    
    
    @property
    @abstractmethod
    def all_document_ids(self) -> List[str]:
        pass
    
    @classmethod
    @abstractmethod
    def from_texts(
        cls,
        texts: List[str],
        embedding: Any,
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> "MemoryInterface":
        pass

    @classmethod
    @abstractmethod
    def initialize_memory(cls, embedding = None, dim:int=1536):
        pass