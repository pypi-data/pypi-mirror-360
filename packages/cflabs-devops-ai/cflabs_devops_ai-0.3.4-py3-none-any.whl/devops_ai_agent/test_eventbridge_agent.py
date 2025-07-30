#!/usr/bin/env python3
"""
Test script for EventBridge functionality in the DevOps AI Agent.
This script demonstrates how the agent can handle EventBridge commands.
"""

import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the path so we can import the agent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from devops_ai_agent.agent import DevOpsAIAgent


def test_eventbridge_queries():
    """Test various EventBridge queries with the agent."""
    
    # Load environment variables
    load_dotenv()
    
    # Check if OpenAI API key is available
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("❌ OPENAI_API_KEY environment variable is required")
        print("Please set your OpenAI API key in the .env file or environment")
        return
    
    # Initialize the agent
    agent = DevOpsAIAgent(openai_api_key)
    
    # Test queries for EventBridge functionality
    test_queries = [
        "create an eventbridge rule called backup-rule that runs daily at 2am targeting my lambda function",
        "list all eventbridge rules in us-east-1",
        "delete the eventbridge rule called backup-rule",
        "update my eventbridge rule called backup-rule to run every 6 hours",
        "show details for the eventbridge rule called backup-rule",
        "create a weekly eventbridge rule called report-rule that runs every monday at 9am",
        "create an eventbridge rule for cleanup that runs every 30 minutes",
        "list eventbridge rules with prefix backup",
        "delete the eventbridge rule called report-rule with force",
        "update the cleanup rule to run every 2 hours instead"
    ]
    
    print("🧪 Testing EventBridge Agent Functionality")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 50)
        
        try:
            # Parse the query
            parsed = agent.parse_query(query)
            
            # Display results
            print(f"Command: {parsed.get('command', 'unknown')}")
            print(f"Confidence: {parsed.get('confidence', 0):.2f}")
            
            if parsed.get("parameters"):
                print("Parameters:")
                for key, value in parsed["parameters"].items():
                    print(f"  {key}: {value}")
            
            if parsed.get("missing_info"):
                print(f"Missing info: {parsed['missing_info']}")
            
            # Check if it's an EventBridge command
            if parsed.get("command", "").startswith("eventbridge"):
                print("✅ EventBridge command detected!")
            else:
                print("⚠️  Not an EventBridge command")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()


def test_cron_conversion():
    """Test the cron conversion functionality."""
    print("\n🕐 Testing Cron Conversion Examples")
    print("=" * 40)
    
    # Import the cron converter
    try:
        from devops_ai_eventbridge.cron_converter import CronConverter
        
        converter = CronConverter()
        
        test_cases = [
            "daily at 9am",
            "every monday at 2pm",
            "weekly on friday at 5pm",
            "monthly on the 15th",
            "every 30 minutes",
            "every 2 hours",
            "weekdays at 8am",
            "weekends at 10am",
            "yearly on january 1st",
            "every 3 days"
        ]
        
        for description in test_cases:
            try:
                cron_expression = converter.text_to_cron(description)
                is_valid = converter.validate_cron(cron_expression)
                status = "✅" if is_valid else "❌"
                
                print(f"{status} {description:<25} → {cron_expression}")
            except Exception as e:
                print(f"❌ {description:<25} → Error: {e}")
                
    except ImportError:
        print("❌ Could not import CronConverter - EventBridge module not available")


def main():
    """Main test function."""
    print("🚀 DevOps AI Agent - EventBridge Integration Test")
    print("=" * 60)
    
    # Test cron conversion first (doesn't require OpenAI)
    test_cron_conversion()
    
    # Test agent queries (requires OpenAI API key)
    test_eventbridge_queries()
    
    print("\n✅ Test completed!")
    print("\nTo use the agent interactively:")
    print("  devops-ai-agent chat")
    print("\nTo test a specific query:")
    print("  devops-ai-agent test 'create an eventbridge rule called backup-rule that runs daily at 2am'")


if __name__ == "__main__":
    main() 