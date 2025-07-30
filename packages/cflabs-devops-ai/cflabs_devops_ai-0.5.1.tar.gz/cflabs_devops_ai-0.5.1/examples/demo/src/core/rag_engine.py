from typing import List, Dict, Any
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.core.embeddings import Embeddings   
from src.core.vector_db import VectorDB     
from src.utils.logger import get_logger, time_function, log_function_call
import openai
from src.config import Config

logger = get_logger(__name__)

class RAGEngine:
    @time_function
    def __init__(self, project_name: str):
        logger.info(f"Initializing RAGEngine with project: {project_name}")
        self.project_name = project_name
        self.vector_db = VectorDB(backend="pinecone", index_name=self.project_name, dimension=1024)
        self.embeddings = Embeddings()
        self.openai_client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        logger.info("RAGEngine initialized successfully")

    @time_function
    @log_function_call
    def ingest(self, dataset: List[Dict[str, Any]], parallel_threads: int = 1):
        """
        This function is responsible for ingesting the data into the vector database.
        input: List[Dict[str, Any]], parallel_threads: int = 1
        output: None
        """
        try:
            logger.info(f"Starting ingestion of {len(dataset)} documents with {parallel_threads} threads")
            
            texts_to_embed = []
            metadata = []
            total_chunks = sum(len(doc['chunks']) for doc in dataset)
            
            logger.info(f"Total chunks to process: {total_chunks}")

            def process_chunk(doc, chunk):
                #for each chunk, produce the context
                contextualized_text, usage = self.embeddings.situate_context(doc['content'], chunk['content'])
                
                return {
                    #append the context to the original text chunk
                    'text_to_embed': f"{chunk['content']}\n\n{contextualized_text}",
                    'metadata': {
                        'doc_id': doc['doc_id'],
                        'original_uuid': doc['original_uuid'],
                        'chunk_id': chunk['chunk_id'],
                        'original_index': chunk['original_index'],
                        'original_content': chunk['content'],
                        'contextualized_content': contextualized_text,
                        'file_id': doc['file_id'],
                    }
                }

            logger.info(f"Processing {total_chunks} chunks with {parallel_threads} threads")
            with ThreadPoolExecutor(max_workers=parallel_threads) as executor:
                futures = []
                for doc in dataset:
                    for chunk in doc['chunks']:
                        futures.append(executor.submit(process_chunk, doc, chunk))
                
                for future in tqdm(as_completed(futures), total=total_chunks, desc="Processing chunks"):
                    result = future.result()
                    texts_to_embed.append(result['text_to_embed'])
                    metadata.append(result['metadata'])

            logger.info(f"Generated {len(texts_to_embed)} texts to embed")

            # generate embeddings for the texts
            logger.info("Generating embeddings for texts")
            embeddings = self.embeddings.generate_embeddings(texts_to_embed)
            
            # save the embeddings and vector database
            logger.info("Adding embeddings to vector database")
            self.vector_db.add_embeddings(embeddings, metadata)
            
            logger.info("Ingestion completed successfully")
            return True
        except Exception as e:
            logger.error(f"Error ingesting documents: {str(e)}")
            return False
