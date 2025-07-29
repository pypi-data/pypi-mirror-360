from typing import List
from .document_chunking_base import DocumentChunkingBase
from .chunking_strategy import ChunkingSettings
from ..common.source_document import SourceDocument
from ...utilities.helpers.env_helper import EnvHelper

from mgmt_config import logger
env_helper: EnvHelper = EnvHelper()
log_execution = env_helper.LOG_EXECUTION
log_args = env_helper.LOG_ARGS
log_result = env_helper.LOG_RESULT


class SimpleTextSplitter:
    """Simple text splitter to replace LangChain's MarkdownTextSplitter."""
    
    def __init__(self, chunk_size: int, chunk_overlap: int):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    @logger.trace_function(log_execution=log_execution, log_args=False, log_result=False)
    def split_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap."""
        if not text:
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Calculate end position
            end = start + self.chunk_size
            
            # If this is not the last chunk, try to find a good break point
            if end < len(text):
                # Look for sentence endings, then paragraph breaks, then word boundaries
                for break_char in ['. ', '.\n', '\n\n', '\n', ' ']:
                    break_pos = text.rfind(break_char, start, end)
                    if break_pos > start:
                        end = break_pos + len(break_char)
                        break
            
            # Extract chunk
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position (with overlap)
            start = max(start + 1, end - self.chunk_overlap)
            
            # Prevent infinite loop
            if start >= len(text):
                break
        
        return chunks


class LayoutDocumentChunking(DocumentChunkingBase):
    def __init__(self) -> None:
        pass

    @logger.trace_function(log_execution=log_execution, log_args=False, log_result=False)
    def chunk(
        self, documents: List[SourceDocument], chunking: ChunkingSettings
    ) -> List[SourceDocument]:
        full_document_content = "".join(
            list(map(lambda document: document.content, documents))
        )
        try:
            document_url = documents[0].source
        except IndexError as e:
            # If no documents are provided, set document_url to None
            logger.error("No documents provided for chunking.")
            logger.debug(e)
            document_url = None
        
        splitter = SimpleTextSplitter(
            chunk_size=chunking.chunk_size, 
            chunk_overlap=chunking.chunk_overlap
        )
        chunked_content_list = splitter.split_text(full_document_content)
        
        # Create document for each chunk
        documents = []
        chunk_offset = 0
        for idx, chunked_content in enumerate(chunked_content_list):
            documents.append(
                SourceDocument.from_metadata(
                    content=chunked_content,
                    document_url=document_url,
                    metadata={"offset": chunk_offset},
                    idx=idx,
                )
            )

            chunk_offset += len(chunked_content)
        return documents
