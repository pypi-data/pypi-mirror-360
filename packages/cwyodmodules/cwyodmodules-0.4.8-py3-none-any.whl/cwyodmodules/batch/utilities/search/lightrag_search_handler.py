from typing import List
from ..helpers.lightrag_helper import LightRAGHelper
from .search_handler_base import SearchHandlerBase
from ..common.source_document import SourceDocument

from ...utilities.helpers.env_helper import EnvHelper
from mgmt_config import logger
env_helper: EnvHelper = EnvHelper()
log_execution = env_helper.LOG_EXECUTION
log_args = env_helper.LOG_ARGS
log_result = env_helper.LOG_RESULT



class LightRAGSearchHandler(SearchHandlerBase):
    def __init__(self, env_helper):
        super().__init__(env_helper)
        self.lightrag_helper = LightRAGHelper()

    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=False)
    def query_search(self, question) -> List[SourceDocument]:
        logger.info(f"Performing query search for question: {question}")
        search_results = self.lightrag_helper.search(question)
        source_documents = self._convert_to_source_documents(search_results)
        logger.info(f"Found {len(source_documents)} source documents.")
        return source_documents

    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=False)
    def _convert_to_source_documents(self, search_results) -> List[SourceDocument]:
        source_documents = []
        for source in search_results:
            source_documents.append(
                SourceDocument(
                    id=source.get("id"),
                    content=source.get("content"),
                    title=source.get("title"),
                    source=source.get("source"),
                    chunk=source.get("chunk"),
                    offset=source.get("offset"),
                    page_number=source.get("page_number"),
                )
            )
        return source_documents

    @logger.trace_function(log_execution=log_execution, log_args=False, log_result=False)
    def create_vector_store(self, documents_to_upload):
        logger.info(f"Creating vector store with {len(documents_to_upload)} documents.")
        return self.lightrag_helper.create_vector_store(documents_to_upload)

    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=False)
    def perform_search(self, filename):
        logger.info(f"Performing search for filename: {filename}")
        return self.lightrag_helper.perform_search(filename)

    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=False)
    def get_files(self):
        logger.info("Fetching files from LightRAG.")
        return self.lightrag_helper.get_files()

    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=log_result)
    def delete_files(self, files):
        logger.info(f"Deleting files: {files}")
        return self.lightrag_helper.delete_files(files)

    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=False)
    def search_by_blob_url(self, blob_url):
        logger.info(f"Searching by blob URL: {blob_url}")
        return self.lightrag_helper.search_by_blob_url(blob_url)

    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=False) 
    def get_unique_files(self):
        logger.info("Fetching unique files from LightRAG.")
        return self.lightrag_helper.get_unique_files()
