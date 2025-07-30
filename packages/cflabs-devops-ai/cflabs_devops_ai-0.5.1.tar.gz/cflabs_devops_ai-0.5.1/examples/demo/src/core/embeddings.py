import voyageai
from typing import Any, List, Dict
import openai
from src.utils.logger import get_logger, time_function, log_function_call
from src.config import Config

class Embeddings:
    """
        This class is responsible for generating embeddings for the documents.
    """

    def __init__(self): 
        self.openai_client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        self.voyage_client = voyageai.Client(api_key=Config.VOYAGE_API_KEY)

    @time_function
    @log_function_call
    def generate_embedding(self, document):
        """
        This function is responsible for generating embeddings for the documents using voyage api
        input: str
        output: List[float]
        """
        self.embedding = self.generate_embeddings([document])[0]
        return self.embedding

    @time_function
    @log_function_call
    def generate_embeddings(self, texts: List[str]):
        """
        This function is responsible for generating embeddings for the documents using voyage api
        input: List[str]
        output: List[List[float]]
        """
        batch_size = 128
        result = [
            self.voyage_client.embed(
                texts[i : i + batch_size],
                model="voyage-2"
            ).embeddings
            for i in range(0, len(texts), batch_size)
        ]
        embeddings = [embedding for batch in result for embedding in batch]
        return embeddings

    def situate_context(self, doc: str, chunk: str) -> tuple[str, Any]:
        """
        This function is responsible for generating a context for a chunk of text within a document.
        input: str, str
        output: str
        """

        DOCUMENT_CONTEXT_PROMPT = """
        <document>
        {doc_content}
        </document>
        """

        CHUNK_CONTEXT_PROMPT = """
        Here is the chunk we want to situate within the whole document
        <chunk>
        {chunk_content}
        </chunk>

        Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk.
        Answer only with the succinct context and nothing else.
        """
        prompt = DOCUMENT_CONTEXT_PROMPT.format(doc_content=doc) + "\n" + CHUNK_CONTEXT_PROMPT.format(chunk_content=chunk)
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.0,
                timeout=30
            )
            text = response.choices[0].message.content.strip()
            return text, None
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return "", None
