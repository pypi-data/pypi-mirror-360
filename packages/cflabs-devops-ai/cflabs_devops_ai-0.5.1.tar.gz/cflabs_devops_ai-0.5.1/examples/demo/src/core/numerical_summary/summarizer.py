from typing import List, Dict, Any
from src.utils.logger import get_logger, time_function, log_function_call
import openai
import os   

from src.core.numerical_summary.analyze_table_data import AnalyzeTableData  
from src.core.numerical_summary.goal_enrich import GoalEnricher

logger = get_logger(__name__)

class NumericalSummaryEngine:
    """
    This class is responsible for getting KPIs from the tables from a given database.
    1. Extract KPIs from the goal
    2. Analyze the tables and get the KPIs
    3. Generate a comprehensive list of KPIs
    """
    @time_function
    def __init__(self, database_name: str):
        logger.info(f"Initializing SummaryEngine with database: {database_name}")
        self.database_name = database_name
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.table_analyzer = AnalyzeTableData(self.openai_client, self.database_name)
        self.goal_enrich = GoalEnricher(self.openai_client)   
        logger.info("SummaryEngine initialized successfully")

    @time_function
    @log_function_call
    def numerical_summarization(self, goal: str) -> List[Dict[str, Any]]:
        """
        Get all tables from project database and summarize them with KPI analysis.
        input: goal: str
        output: List[Dict[str, Any]]
        """
        logger.info(f"Starting numerical summarization for goal: '{goal[:50]}...' and database: {self.database_name}")
        
        # Extract KPIs from the goal
        kpis = self.goal_enrich.extract_kpis_from_goal(goal)
        
        # Get all tables from the database
        tables = self.table_analyzer.get_table_data()

        # Analyze the tables and get the KPIs
        logger.info(f"Analyzing {len(tables)} tables for KPIs")
        table_summaries = []
        for table in tables:
            logger.info(f"Analyzing table: {table.ingested_table_name}")
            table_analysis = self.table_analyzer.analyze_table_data(table, kpis)
            if table_analysis is None:
                logger.warning(f"No table summary found for table: {table.ingested_table_name}")
                continue
            table_summaries.append(table_analysis)
            
        # Extract KPIs from table summaries
        total_kpis = []
        for table_summary in table_summaries:
            if table_summary.get('ai_analysis') and table_summary['ai_analysis'].get('kpis'):
                if isinstance(table_summary['ai_analysis']['kpis'], list):
                    total_kpis.extend(table_summary['ai_analysis']['kpis'])
                elif table_summary['ai_analysis']['kpis'] != "not_present":
                    total_kpis.append(table_summary['ai_analysis']['kpis'])
        
        # Generate a comprehensive summary of the data
        comprehensive_summary = self._generate_comprehensive_summary(total_kpis)
        logger.info(f"Comprehensive summary: {comprehensive_summary}")
        return {
            "goal": goal,
            "enriched_goal": kpis,
            "summary": comprehensive_summary,
            "table_summaries": table_summaries,
            "extracted_kpis": total_kpis,
        }
    

    @time_function
    @log_function_call
    def _generate_comprehensive_summary(self, total_kpis: List[Dict[str, Any]]) -> str:
        """
        Generate a comprehensive summary of the data using the table summaries with AI.
        """
        system_prompt = """You are a data analyst that summarizes database tables.

## Your task  
You receive:    
1. **Total KPIs** - the KPIs that are present in all tables

## Instructions
1. Generate a concise and insightful summary using the KPI names alone.
2. Mention and highlight the KPIs that are included.
3. Do not fabricate any numerical values or data points.
4. Provide a crisp explanation of what each KPI represents, and why it matters.
5. Use bullet points or sections for clarity.
6. Limit the summary to less than 500 words.
7. The output should be suitable for product managers, analysts, or business leaders to understand the focus areas.


## Example Output:
# Summary of Key Performance Indicators (KPIs)

### KPIs Identified:
- Total Sales
- Conversion Rate
- Customer Retention Rate
- Monthly Active Users
- Average Order Value
"""
        
        user_prompt = f"Total KPIs: {total_kpis}"
        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=200,
            temperature=0.1,
            timeout=30
        )
        return response.choices[0].message.content.strip()
 
    