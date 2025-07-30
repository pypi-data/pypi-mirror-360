from typing import List, Dict, Any
from src.core.embeddings import Embeddings
from src.core.vector_db import VectorDB
from src.utils.logger import get_logger, time_function, log_function_call
import openai   
import os
from src.core.document_summary.goal_enrich import GoalEnricher
from src.core.document_summary.clustering import ClusteringEngine

logger = get_logger(__name__)

class DocumentSummaryEngine:
    """
    This class is responsible for summarizing the data into the vector database.
    1. Enrich the goal based on user role and project description and other relevant information
    2. Use the same vector_db instance that was used for ingestion
    3. Cluster the results
    4. Format the results into a summary
    """
    @time_function
    def __init__(self, project_name: str):
        logger.info(f"Initializing SummaryEngine with project: {project_name}")
        self.project_name = project_name    
        self.vector_db = VectorDB(backend="pinecone", index_name=self.project_name, dimension=1024)
        self.embeddings = Embeddings()
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.goal_enrich = GoalEnricher(self.openai_client)
        self.clustering_engine = ClusteringEngine()
        logger.info("SummaryEngine initialized successfully")

    @time_function
    @log_function_call
    def document_summarization(self, goal: str):
        """
        This function is responsible for summarizing the data into the vector database.
        input: goal: str
        output: summary: str
        """
        logger.info(f"Summarizing goal: '{goal[:50]}...'")
        # enrich the goal based on user role and project description and other relevant information
        enriched_goal = self.goal_enrich.enrich_goal(goal)
        # Use the same vector_db instance that was used for ingestion
        query_embedding = self.embeddings.generate_embedding(enriched_goal)
        results = self.vector_db.search(query_embedding, k=200)
        # cluster the results
        results = self.clustering_engine.cluster_and_select_top_results(results)
        # format the results into a summary
        summary = self.format_summary(enriched_goal, results)
        logger.info(f"Summarization completed, found {len(summary)} results")
        return {
            "goal": goal,
            "enriched_goal": enriched_goal,
            "summary": summary
        }
    
    @time_function
    @log_function_call
    def format_summary(self, enriched_goal: str, results: List[Dict[str, Any]]) -> str:
        """
        This function is responsible for formatting the results into a summary.
        input: goal: str, results: List[Dict[str, Any]]
        output: str
        """
        logger.info(f"Formatting {len(results)} search results for goal: '{enriched_goal[:50]}...'")
        
        if not results:
            logger.warning("No results to format")
            return "I couldn't find any relevant information to summarize your goal."
        
        # Prepare the context from search results
        context_parts = []
        for i, result in enumerate(results):
            metadata = result.get('metadata', {})
            original_content = metadata.get('original_content', '')
            contextualized_content = metadata.get('contextualized_content', '')
            similarity = result.get('similarity', 0)
            
            # Combine original content with contextualized content
            combined_content = f"{original_content}\n\nContext: {contextualized_content}"
            context_parts.append(f"Source {i+1} (Relevance: {similarity:.3f}):\n{combined_content}")
        
        context = "\n\n---\n\n".join(context_parts)
        
        # System prompt for formatting
        system_prompt = """You are a helpful assistant that summarises documents.

## Your task  
You receive:
1. **Goal** - a natural-language objective.  
2. **Context** - a list of one or more documents.

Produce a concise, well-structured summary **in Markdown**.

#Instructions
1. Detect KPIs from the goal.
2. If these KPIs are present in the context, use them to generate the summary.
3. Put these KPIs in  one of these Key Insights, Action Items, Recommendations, or Conclusion.
---

## Required output format  

```
# Summary  

## Key Insights  
1. …  
2. …  

## Action Items  
1. …  
2. …  

## Recommendations  
1. …  
2. …  

## Conclusion  
…
```

---

## Guardrails  
- Maximum length: **≤ 1000 words**  
- **No hallucinations** - include only facts present in the documents  
- Exclude content not relevant to the stated goal  
- Every statement must be supported by the provided context  

---

## Reference Example  

**Input (excerpt)**  
> Marketing Campaign Q1 set out to boost brand awareness and generate high quality leads across digital channels. Over the quarter, we achieved significant uplifts in engagement and optimised our spend for maximum ROI.  

**Expected Output**  
```
# Summary

## Key Insights
1. Increase in Q1 website traffic by 42%
2. Top channels: Email & Social
3. Recommended budget reallocation to paid search
4. Customer engagement up 18% vs. Q4

## Action Items
1. Increase email marketing spend by 20%
2. Optimize social media campaigns for maximum ROI
3. Allocate 30% of budget to paid search
4. Increase email marketing spend by 20%

## Recommendations
1. Continue monitoring engagement metrics
2. Adjust budget allocations based on performance
3. Optimise email campaigns for better ROI
4. Increase social media spend for brand awareness

## Conclusion
The Q1 marketing campaign successfully met its objectives while maximising ROI.

        """
    
        # User prompt with query and context
        user_prompt = f"""Goal: {enriched_goal}

Context from search results:
{context}

Please provide a concise and well-structured answer based on the above context. If the context doesn't contain sufficient information to answer the question, please state that clearly."""

        try:
            logger.info("Sending request to OpenAI for result formatting")
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.3,
                timeout=60
            )
            
            formatted_answer = response.choices[0].message.content.strip()
            logger.info(f"Successfully formatted results, response length: {len(formatted_answer)}")
            
            return formatted_answer
            
        except Exception as e:
            logger.error(f"Error formatting results with OpenAI: {e}")
            # Fallback: return a simple formatted response
            fallback_response = f"Based on the search results, here's what I found:\n\n"
            for i, result in enumerate(results[:3]):  # Limit to top 3 results
                metadata = result.get('metadata', {})
                content = metadata.get('original_content', '')[:200] + "..."
                fallback_response += f"{i+1}. {content}\n\n"
            return fallback_response
