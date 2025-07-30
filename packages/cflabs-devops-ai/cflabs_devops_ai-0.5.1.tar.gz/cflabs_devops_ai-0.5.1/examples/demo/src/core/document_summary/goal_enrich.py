from typing import List
from src.utils.logger import get_logger, time_function, log_function_call
from openai import OpenAI

logger = get_logger("GoalEnricher")


class GoalEnricher:
    def __init__(self, openai_client: OpenAI):
        self.openai_client = openai_client

    @time_function
    @log_function_call
    def enrich_goal(self, goal: str) -> str:
        """
        This function is responsible for enriching the goal based on user role and project description and other relevant information.
        input: goal: str
        output: enriched_goal: str
        """
        # get the user role
        user_role = self.get_user_role()
        # get the user type
        user_type = self.get_user_type()
        # get the project description
        project_description = self.get_project_description()
        # use gpt to enrich the goal based on user role and project description and other relevant information
        enriched_goal = self.enrich_goal_with_ai(goal, user_role, user_type, project_description)
        logger.info(f"Enriched goal: {enriched_goal}")
        return enriched_goal
    
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
    def enrich_goal_with_ai(self, goal: str, user_role: str, user_type: str, project_description: str) -> str:
        """
        This function is responsible for enriching the goal with user role, user type, and project description.
        input: goal: str, user_role: str, user_type: str, project_description: str
        output: enriched_goal: str
        """
        logger.info(f"Enriching goal: '{goal[:50]}...'")
        # use gpt to enrich the goal based on user role, user type, and project description
        system_prompt = """You are a helpful assistant that enriches goals based on user role, user type, and project description.
        Identify the Key Performance Indicators (KPIs) from goal, user role, user type, and project description.
        Use the KPIs to enrich the goal.

        If there are predicted goal examples like "Need $500 sales this month."
        Then the enriched goal should be more specific and detailed.

        Examples:
        Input 1:
        Goal: "Need $500 sales this month."
        User Role: "sales manager"
        User Type: "sales manager"
        Project Description: "sales project containing sales data"
        Enrichment: "Need $500 sales this month. This is a sales project containing sales data. The sales manager is responsible for achieving this goal."

        Output:
        "Need $500 sales this month. Important KPIs to track are: lead conversion rate, average order value, customer acquisition cost, customer lifetime value, etc."

        Input 2:
        Goal: "Month on month increase in sales"
        User Role: "sales manager"
        User Type: "sales manager"
        Project Description: "sales project containing sales data"
        Enrichment: "Month on month increase in sales. Important KPIs to track are: lead conversion rate, average order value, customer acquisition cost, customer lifetime value, etc."

        Output: 
        "Month on month increase in sales. Important KPIs to track are: lead conversion rate, average order value, customer acquisition cost, customer lifetime value, etc."

        Input 3:
        Goal: "Increase in website traffic"
        User Role: "sales manager"
        User Type: "sales manager"
        Project Description: "sales project containing sales data"
        Enrichment: "Increase in website traffic. Important KPIs to track are: website traffic, website conversion rate, website bounce rate, website average time on page, etc."

        Output:
        "Increase in website traffic. Important KPIs to track are: website traffic, website conversion rate, website bounce rate, website average time on page, etc."
        """
        user_prompt = f"""Goal: {goal}
        User Role: {user_role}
        User Type: {user_type}
        Project Description: {project_description}
        """
        enriched_goal = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
        )
        return enriched_goal.choices[0].message.content.strip()