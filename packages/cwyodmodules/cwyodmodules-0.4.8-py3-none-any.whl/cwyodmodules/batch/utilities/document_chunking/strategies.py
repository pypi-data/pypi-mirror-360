from .chunking_strategy import ChunkingStrategy
from .layout import LayoutDocumentChunking
from .page import PageDocumentChunking
from .fixed_size_overlap import FixedSizeOverlapDocumentChunking
from .paragraph import ParagraphDocumentChunking

def get_document_chunker(chunking_strategy: str):
    """
    Factory function to get the appropriate document chunker based on the provided strategy.

    Parameters:
    chunking_strategy (str): The strategy to use for chunking the document. This should be one of the values defined in the ChunkingStrategy enum.

    Returns:
    object: An instance of the appropriate document chunking class based on the provided strategy.

    Raises:
    Exception: If the provided chunking strategy is not recognized.

    The available chunking strategies are:
    - LAYOUT: Uses the LayoutDocumentChunking class to chunk the document based on its layout.
    - PAGE: Uses the PageDocumentChunking class to chunk the document by pages.
    - FIXED_SIZE_OVERLAP: Uses the FixedSizeOverlapDocumentChunking class to chunk the document with fixed size and overlapping chunks.
    - PARAGRAPH: Uses the ParagraphDocumentChunking class to chunk the document by paragraphs.
    """
    if chunking_strategy == ChunkingStrategy.LAYOUT.value:
        return LayoutDocumentChunking()
    elif chunking_strategy == ChunkingStrategy.PAGE.value:
        return PageDocumentChunking()
    elif chunking_strategy == ChunkingStrategy.FIXED_SIZE_OVERLAP.value:
        return FixedSizeOverlapDocumentChunking()
    elif chunking_strategy == ChunkingStrategy.PARAGRAPH.value:
        return ParagraphDocumentChunking()
    else:
        raise Exception(f"Unknown chunking strategy: {chunking_strategy}")