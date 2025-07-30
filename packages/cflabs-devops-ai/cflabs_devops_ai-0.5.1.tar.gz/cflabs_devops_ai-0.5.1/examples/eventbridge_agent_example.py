#!/usr/bin/env python3
"""
Example: Using DevOps AI Agent with EventBridge functionality

This example demonstrates how to use the enhanced agent to create and manage
AWS EventBridge rules using natural language commands.
"""

import os
import sys
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from devops_ai_agent.agent import DevOpsAIAgent
from devops_ai_eventbridge.cron_converter import CronConverter


def demonstrate_eventbridge_agent():
    """Demonstrate EventBridge functionality with the agent."""
    
    # Load environment variables
    load_dotenv()
    
    # Check for OpenAI API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("❌ OPENAI_API_KEY environment variable is required")
        print("Please set your OpenAI API key in the .env file")
        return
    
    print("🚀 DevOps AI Agent - EventBridge Integration Demo")
    print("=" * 60)
    
    # Initialize the agent
    agent = DevOpsAIAgent(openai_api_key)
    
    # Example 1: Create a daily backup rule
    print("\n📝 Example 1: Create a daily backup rule")
    print("-" * 40)
    
    query1 = "create an eventbridge rule called daily-backup that runs daily at 2am targeting my lambda function arn:aws:lambda:us-east-1:123456789012:function:backup-function"
    
    print(f"Query: {query1}")
    parsed1 = agent.parse_query(query1)
    
    print(f"Command: {parsed1.get('command')}")
    print(f"Confidence: {parsed1.get('confidence', 0):.2f}")
    print("Parameters:")
    for key, value in parsed1.get("parameters", {}).items():
        print(f"  {key}: {value}")
    
    # Example 2: Create a weekly report rule
    print("\n📝 Example 2: Create a weekly report rule")
    print("-" * 40)
    
    query2 = "create an eventbridge rule called weekly-report that runs every monday at 9am targeting my lambda function arn:aws:lambda:us-east-1:123456789012:function:report-generator"
    
    print(f"Query: {query2}")
    parsed2 = agent.parse_query(query2)
    
    print(f"Command: {parsed2.get('command')}")
    print(f"Confidence: {parsed2.get('confidence', 0):.2f}")
    print("Parameters:")
    for key, value in parsed2.get("parameters", {}).items():
        print(f"  {key}: {value}")
    
    # Example 3: List rules
    print("\n📝 Example 3: List EventBridge rules")
    print("-" * 40)
    
    query3 = "list all eventbridge rules in us-east-1"
    
    print(f"Query: {query3}")
    parsed3 = agent.parse_query(query3)
    
    print(f"Command: {parsed3.get('command')}")
    print(f"Confidence: {parsed3.get('confidence', 0):.2f}")
    print("Parameters:")
    for key, value in parsed3.get("parameters", {}).items():
        print(f"  {key}: {value}")
    
    # Example 4: Update a rule
    print("\n📝 Example 4: Update a rule schedule")
    print("-" * 40)
    
    query4 = "update my eventbridge rule called daily-backup to run every 6 hours instead"
    
    print(f"Query: {query4}")
    parsed4 = agent.parse_query(query4)
    
    print(f"Command: {parsed4.get('command')}")
    print(f"Confidence: {parsed4.get('confidence', 0):.2f}")
    print("Parameters:")
    for key, value in parsed4.get("parameters", {}).items():
        print(f"  {key}: {value}")
    
    # Example 5: Delete a rule
    print("\n📝 Example 5: Delete a rule")
    print("-" * 40)
    
    query5 = "delete the eventbridge rule called weekly-report with force"
    
    print(f"Query: {query5}")
    parsed5 = agent.parse_query(query5)
    
    print(f"Command: {parsed5.get('command')}")
    print(f"Confidence: {parsed5.get('confidence', 0):.2f}")
    print("Parameters:")
    for key, value in parsed5.get("parameters", {}).items():
        print(f"  {key}: {value}")


def demonstrate_cron_conversion():
    """Demonstrate the cron conversion functionality."""
    
    print("\n🕐 Cron Conversion Examples")
    print("=" * 40)
    
    converter = CronConverter()
    
    examples = [
        ("daily at 9am", "Daily at 9 AM"),
        ("every monday at 2pm", "Every Monday at 2 PM"),
        ("weekly on friday at 5pm", "Weekly on Friday at 5 PM"),
        ("monthly on the 15th", "Monthly on the 15th"),
        ("every 30 minutes", "Every 30 minutes"),
        ("every 2 hours", "Every 2 hours"),
        ("weekdays at 8am", "Weekdays at 8 AM"),
        ("weekends at 10am", "Weekends at 10 AM"),
        ("yearly on january 1st", "Yearly on January 1st"),
        ("every 3 days", "Every 3 days"),
        ("every 6 months", "Every 6 months"),
        ("tuesday at 3pm", "Tuesday at 3 PM"),
        ("sunday at 11am", "Sunday at 11 AM"),
        ("every 15 minutes", "Every 15 minutes"),
        ("every 4 hours", "Every 4 hours"),
        ("every 7 days", "Every 7 days"),
    ]
    
    print(f"{'Description':<25} {'Cron Expression':<15} {'Valid':<5}")
    print("-" * 50)
    
    for description, display_name in examples:
        try:
            cron_expression = converter.text_to_cron(description)
            is_valid = converter.validate_cron(cron_expression)
            status = "✅" if is_valid else "❌"
            
            print(f"{display_name:<25} {cron_expression:<15} {status:<5}")
        except Exception as e:
            print(f"{display_name:<25} {'ERROR':<15} ❌")


def show_usage_examples():
    """Show usage examples for the enhanced agent."""
    
    print("\n📚 Usage Examples")
    print("=" * 40)
    
    examples = [
        {
            "category": "Creating Rules",
            "examples": [
                "create an eventbridge rule called backup-rule that runs daily at 2am",
                "create a weekly eventbridge rule called report-rule that runs every monday at 9am",
                "create an eventbridge rule for cleanup that runs every 30 minutes",
                "create an eventbridge rule called monitoring that runs weekdays at 8am",
                "create an eventbridge rule called maintenance that runs monthly on the 1st"
            ]
        },
        {
            "category": "Managing Rules",
            "examples": [
                "list all eventbridge rules",
                "list eventbridge rules with prefix backup",
                "show details for the eventbridge rule called backup-rule",
                "update my eventbridge rule to run every 6 hours",
                "update the backup rule to run daily at 3am instead"
            ]
        },
        {
            "category": "Deleting Rules",
            "examples": [
                "delete the eventbridge rule called backup-rule",
                "delete the eventbridge rule called report-rule with force",
                "remove the cleanup rule from eventbridge"
            ]
        }
    ]
    
    for category in examples:
        print(f"\n{category['category']}:")
        for example in category['examples']:
            print(f"  • {example}")


def main():
    """Main demonstration function."""
    
    print("🎯 DevOps AI Agent - EventBridge Integration")
    print("=" * 60)
    
    # Demonstrate cron conversion (no OpenAI required)
    demonstrate_cron_conversion()
    
    # Demonstrate agent functionality (requires OpenAI API key)
    demonstrate_eventbridge_agent()
    
    # Show usage examples
    show_usage_examples()
    
    print("\n✅ Demonstration completed!")
    print("\nTo use the agent interactively:")
    print("  devops-ai-agent chat")
    print("\nTo test specific commands:")
    print("  devops-ai-agent test 'create an eventbridge rule called backup-rule that runs daily at 2am'")
    print("\nTo use EventBridge CLI directly:")
    print("  devops-ai eventbridge create 'backup-rule' 'daily at 2am' 'arn:aws:lambda:...'")
    print("  devops-ai eventbridge list")
    print("  devops-ai eventbridge convert 'daily at 9am'")


if __name__ == "__main__":
    main() 