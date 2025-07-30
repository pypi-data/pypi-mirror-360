from typing import List
from src.utils.logger import get_logger, time_function, log_function_call   
from openai import OpenAI
import os   

logger = get_logger("GoalEnricher")

class GoalEnricher:
    def __init__(self, openai_client: OpenAI):
        self.openai_client = openai_client

    def enrich_goal(self, goal: str) -> str:
        return goal
    
    def get_user_role(self) -> str:
        """
        This function is responsible for getting the user role.
        input: None
        output: user_role: str
        """
        # get the user role
        return "sales"
    
    def get_user_type(self) -> str:
        """
        This function is responsible for getting the user type.
        input: None
        output: user_type: str
        """
        # get the user type
        return "sales manager"
    
    def get_project_description(self) -> str:
        """
        This function is responsible for getting the project description.
        input: None
        output: project_description: str
        """
        # get the project description
        return "sales project containing sales data"
    
    @time_function
    @log_function_call
    def extract_kpis_from_goal(self, goal: str) -> List[str]:
        """
        Extract KPIs from the enriched goal using AI.
        """
        logger.info(f"Extracting KPIs from goal: '{goal[:50]}...'")
        try:
            system_prompt = """You are a KPI extraction specialist. Extract specific, measurable KPIs from the given goal.

## Examples:
Goal: "Need $200K sales this month"
KPIs: ["total_sales", "monthly_revenue", "lead_generation", "conversion_rate", "average_order_value", "total_orders"]

Goal: "Increase website traffic by 50%"
KPIs: ["website_traffic", "page_views", "unique_visitors", "traffic_growth_rate", "bounce_rate"]

Goal: "Improve customer retention"
KPIs: ["customer_retention_rate", "churn_rate", "customer_lifetime_value", "repeat_purchase_rate", "customer_satisfaction"]

## Instructions:
1. Extract 5-10 specific, measurable KPIs
2. Use standard business terminology
3. Include both primary and supporting KPIs
4. Focus on metrics that can be tracked in databases
5. Return only the KPI names as a list, no explanations

## Output Format:
["kpi1", "kpi2", "kpi3", ...]"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Goal: {goal}"}
                ],
                max_tokens=200,
                temperature=0.1,
                timeout=30
            )
            
            kpis_text = response.choices[0].message.content.strip()
            # Parse the list format and extract KPIs
            kpis = [kpi.strip().strip('"').strip("'") for kpi in kpis_text.strip('[]').split(',')]
            return [kpi for kpi in kpis if kpi]
            
        except Exception as e:
            logger.error(f"Error extracting KPIs: {e}")
            # Fallback to common KPIs
            return ["total_sales", "revenue", "orders", "customers", "conversion_rate"]