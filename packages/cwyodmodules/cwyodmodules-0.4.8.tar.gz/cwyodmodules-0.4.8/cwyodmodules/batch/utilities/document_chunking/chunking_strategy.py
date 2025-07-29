from enum import Enum

class ChunkingStrategy(Enum):
    """
    Enum representing different chunking strategies for document processing.
    
    Attributes:
        LAYOUT (str): Chunking based on document layout.
        PAGE (str): Chunking based on individual pages.
        FIXED_SIZE_OVERLAP (str): Chunking with fixed size and overlap.
        PARAGRAPH (str): Chunking based on paragraphs.
    """
    LAYOUT = "layout"
    PAGE = "page"
    FIXED_SIZE_OVERLAP = "fixed_size_overlap"
    PARAGRAPH = "paragraph"

class ChunkingSettings:
    """
    Class representing the settings for document chunking.
    
    Attributes:
        chunking_strategy (ChunkingStrategy): The strategy used for chunking.
        chunk_size (int): The size of each chunk.
        chunk_overlap (int): The overlap between consecutive chunks.
    """
    def __init__(self, chunking: dict):
        """
        Initializes the ChunkingSettings with the provided chunking configuration.
        
        Args:
            chunking (dict): A dictionary containing the chunking configuration.
                Expected keys are "strategy", "size", and "overlap".
        """
        self.chunking_strategy = ChunkingStrategy(chunking["strategy"])
        self.chunk_size = chunking["size"]
        self.chunk_overlap = chunking["overlap"]

    def __eq__(self, other: object) -> bool:
        """
        Checks if this ChunkingSettings instance is equal to another instance.
        
        Args:
            other (object): The other instance to compare against.
        
        Returns:
            bool: True if both instances have the same chunking strategy, size, and overlap, False otherwise.
        """
        if isinstance(self, other.__class__):
            return (
                self.chunking_strategy == other.chunking_strategy
                and self.chunk_size == other.chunk_size
                and self.chunk_overlap == other.chunk_overlap
            )
        else:
            return False