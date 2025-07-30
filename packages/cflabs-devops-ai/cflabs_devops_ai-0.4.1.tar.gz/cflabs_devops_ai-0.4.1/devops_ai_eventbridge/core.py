"""
Core EventBridge management functionality.
"""

import boto3
import logging
import os
from typing import Dict, Optional, List
from botocore.exceptions import ClientError, NoCredentialsError
from .cron_converter import CronConverter

logger = logging.getLogger(__name__)


class EventBridgeManager:
    """Manages AWS EventBridge rules and targets."""
    
    def __init__(self, region_name: str = "us-east-1", profile_name: Optional[str] = None):
        """
        Initialize the EventBridge manager.
        
        Args:
            region_name: AWS region name
            profile_name: AWS profile name (optional)
        """
        self.region_name = region_name
        self.profile_name = profile_name
        
        # Automatically load OpenAI API key from environment
        openai_api_key = os.getenv("OPENAI_API_KEY")
        self.cron_converter = CronConverter(openai_api_key=openai_api_key)
        
        # Initialize AWS clients
        session_kwargs = {"region_name": region_name}
        if profile_name:
            session_kwargs["profile_name"] = profile_name
            
        self.session = boto3.Session(**session_kwargs)
        self.events_client = self.session.client('events')
        
    def create_rule_from_text(self, 
                             rule_name: str, 
                             description: str, 
                             target_arn: Optional[str] = None,
                             target_id: Optional[str] = None) -> Dict:
        """
        Create an EventBridge rule from natural language description.
        
        Args:
            rule_name: Name of the rule
            description: Natural language description of the schedule
            target_arn: ARN of the target (Lambda, SQS, etc.)
            target_id: Optional target ID
            
        Returns:
            Dict containing the created rule information
        """
        try:
            # Convert text to cron expression
            cron_expression = self.cron_converter.text_to_cron(description)
            # Create the rule
            rule_response = self.events_client.put_rule(
                Name=rule_name,
                ScheduleExpression=cron_expression,
                Description=f"Rule created from description: {description}",
                State='ENABLED'
            )
            
            # Set up target only if target_arn is provided
            if target_arn:
                target_id = target_id or f"{rule_name}-target"
                target_response = self.events_client.put_targets(
                    Rule=rule_name,
                    Targets=[
                        {
                            'Id': target_id,
                            'Arn': target_arn
                        }
                    ]
                )
            else:
                logger.info(f"Rule '{rule_name}' created without target. Target can be added later.")
                target_response = None
            
            return {
                "rule_name": rule_name,
                "rule_arn": rule_response.get("RuleArn"),
                "cron_expression": cron_expression,
                "description": description,
                "target_arn": target_arn or "None",
                "target_id": target_id or "None",
                "status": "created"
            }
            
        except ClientError as e:
            logger.error(f"Failed to create EventBridge rule: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating EventBridge rule: {e}")
            raise
    
    def list_rules(self, name_prefix: Optional[str] = None) -> List[Dict]:
        """
        List EventBridge rules.
        
        Args:
            name_prefix: Optional prefix to filter rules
            
        Returns:
            List of rule information dictionaries
        """
        try:
            rules = []
            paginator = self.events_client.get_paginator('list_rules')
            
            # Only pass NamePrefix if it's not None
            paginate_kwargs = {}
            if name_prefix is not None:
                paginate_kwargs['NamePrefix'] = name_prefix
            
            for page in paginator.paginate(**paginate_kwargs):
                for rule in page.get('Rules', []):
                    rules.append({
                        "name": rule.get("Name"),
                        "arn": rule.get("Arn"),
                        "schedule": rule.get("ScheduleExpression"),
                        "description": rule.get("Description"),
                        "state": rule.get("State")
                    })
            
            return rules
            
        except ClientError as e:
            logger.error(f"Failed to list EventBridge rules: {e}")
            raise
    
    def delete_rule(self, rule_name: str, force: bool = False) -> Dict:
        """
        Delete an EventBridge rule.
        
        Args:
            rule_name: Name of the rule to delete
            force: If True, remove targets before deleting rule
            
        Returns:
            Dict containing deletion status
        """
        try:
            if force:
                # Remove all targets first
                targets = self.events_client.list_targets_by_rule(Rule=rule_name)
                if targets.get('Targets'):
                    target_ids = [target['Id'] for target in targets['Targets']]
                    self.events_client.remove_targets(Rule=rule_name, Ids=target_ids)
            
            # Delete the rule
            self.events_client.delete_rule(Name=rule_name)
            
            return {
                "rule_name": rule_name,
                "status": "deleted"
            }
            
        except ClientError as e:
            logger.error(f"Failed to delete EventBridge rule: {e}")
            raise
    
    def get_rule_details(self, rule_name: str) -> Dict:
        """
        Get detailed information about a specific rule.
        
        Args:
            rule_name: Name of the rule
            
        Returns:
            Dict containing rule details
        """
        try:
            rule_response = self.events_client.describe_rule(Name=rule_name)
            targets_response = self.events_client.list_targets_by_rule(Rule=rule_name)
            
            return {
                "name": rule_response.get("Name"),
                "arn": rule_response.get("Arn"),
                "schedule": rule_response.get("ScheduleExpression"),
                "description": rule_response.get("Description"),
                "state": rule_response.get("State"),
                "targets": targets_response.get("Targets", [])
            }
            
        except ClientError as e:
            logger.error(f"Failed to get rule details: {e}")
            raise
    
    def update_rule_schedule(self, rule_name: str, description: str) -> Dict:
        """
        Update an existing rule's schedule from text description.
        
        Args:
            rule_name: Name of the rule to update
            description: New natural language description
            
        Returns:
            Dict containing updated rule information
        """
        try:
            # Convert text to cron expression
            cron_expression = self.cron_converter.text_to_cron(description)
            
            # Update the rule
            self.events_client.put_rule(
                Name=rule_name,
                ScheduleExpression=cron_expression,
                Description=f"Rule updated from description: {description}",
                State='ENABLED'
            )
            
            return {
                "rule_name": rule_name,
                "new_cron_expression": cron_expression,
                "new_description": description,
                "status": "updated"
            }
            
        except ClientError as e:
            logger.error(f"Failed to update EventBridge rule: {e}")
            raise 