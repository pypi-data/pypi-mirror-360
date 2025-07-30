from typing import List, Dict, Any
from src.utils.logger import get_logger, time_function, log_function_call
import numpy as np
from sklearn.cluster import KMeans

logger = get_logger(__name__)

class ClusteringEngine:
    @time_function
    def __init__(self):
        pass
        
    
    @time_function
    @log_function_call
    def cluster_and_select_top_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        This function is responsible for clustering the results based on embedding vectors from Pinecone and selecting top results from each cluster.
        input: results: List[Dict[str, Any]]
        output: List[Dict[str, Any]]
        """
        if not results:
            logger.warning("No results to cluster")
            return []
        
        try:
            logger.info(f"Clustering {len(results)} results")
            # Extract embedding vectors directly from Pinecone search results
            embedding_vectors = []
            valid_results = []
            
            for result in results:
                # Check if the result has embedding vectors from Pinecone
                if 'values' in result:
                    embedding_vectors.append(result['values'])
                    valid_results.append(result)
                else:
                    logger.warning(f"Skipping result without embedding vectors: {result.get('id', 'unknown')}")
            
            if not valid_results:
                logger.warning("No valid results with embedding vectors found")
                return results[:50]  # Return top 50 results if clustering fails
            
            logger.info(f"Using {len(embedding_vectors)} embedding vectors from Pinecone for clustering")
            
            # Convert embedding vectors to numpy array for clustering
            embedding_matrix = np.array(embedding_vectors)
            
            # Voyage embeddings are already L2 normalized, so no need for StandardScaler
            # Perform clustering directly on the normalized embedding vectors
            n_clusters = min(10, len(valid_results))  # Ensure we don't have more clusters than data points
            if n_clusters < 2:
                logger.info("Not enough data points for clustering, returning all results")
                return valid_results
            
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(embedding_matrix)
            
            # Select top results from each cluster based on similarity scores
            top_results = []
            for cluster_id in range(n_clusters):
                cluster_mask = cluster_labels == cluster_id
                cluster_results = [valid_results[i] for i in range(len(valid_results)) if cluster_mask[i]]
                
                # Sort by similarity score within each cluster
                cluster_results.sort(key=lambda x: x.get('similarity', 0), reverse=True)
                
                # Take top 5 results from each cluster
                top_results.extend(cluster_results[:5])
            
            logger.info(f"clustering completed. Selected {len(top_results)} results from {n_clusters} clusters")
            return top_results
            
        except Exception as e:
            logger.error(f"Error in Pinecone embedding-based clustering: {e}")
            # Fallback: return top results by similarity
            sorted_results = sorted(results, key=lambda x: x.get('similarity', 0), reverse=True)
            return sorted_results[:50]
    