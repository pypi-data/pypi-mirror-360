#!/usr/bin/env python3
"""
Test script to demonstrate optional target functionality in EventBridge rule creation.
"""

import os
import sys
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from devops_ai_agent.agent import DevOpsAIAgent


def test_optional_target_queries():
    """Test queries with and without target ARN."""
    
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
    
    # Test queries for optional target functionality
    test_queries = [
        "create an eventbridge rule called backup-rule that runs daily at 2am",
        "create an eventbridge rule called backup-rule that runs daily at 2am targeting my lambda function",
        "create an eventbridge rule called weekly-report that runs every monday at 9am",
        "create an eventbridge rule called weekly-report that runs every monday at 9am targeting arn:aws:lambda:us-east-1:123456789012:function:report-generator",
        "create an eventbridge rule for cleanup that runs every 30 minutes",
        "create an eventbridge rule for cleanup that runs every 30 minutes targeting arn:aws:lambda:us-east-1:123456789012:function:cleanup",
    ]
    
    print("🧪 Testing Optional Target Functionality")
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
                
                # Check if target_arn is present
                if "target_arn" in parsed.get("parameters", {}):
                    target_arn = parsed["parameters"]["target_arn"]
                    if target_arn and target_arn != "":
                        print("✅ Target ARN provided")
                    else:
                        print("⚠️  Target ARN is empty or None")
                else:
                    print("⚠️  No target ARN in parameters")
            else:
                print("⚠️  Not an EventBridge command")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()


def demonstrate_usage():
    """Show usage examples for optional targets."""
    
    print("\n📚 Usage Examples for Optional Targets")
    print("=" * 50)
    
    examples = [
        {
            "category": "Creating Rules Without Target",
            "examples": [
                "create an eventbridge rule called backup-rule that runs daily at 2am",
                "create an eventbridge rule called weekly-report that runs every monday at 9am",
                "create an eventbridge rule for cleanup that runs every 30 minutes",
                "create an eventbridge rule called monitoring that runs weekdays at 8am",
                "create an eventbridge rule called maintenance that runs monthly on the 1st"
            ]
        },
        {
            "category": "Creating Rules With Target",
            "examples": [
                "create an eventbridge rule called backup-rule that runs daily at 2am targeting my lambda function",
                "create an eventbridge rule called weekly-report that runs every monday at 9am targeting arn:aws:lambda:us-east-1:123456789012:function:report-generator",
                "create an eventbridge rule for cleanup that runs every 30 minutes targeting arn:aws:lambda:us-east-1:123456789012:function:cleanup",
                "create an eventbridge rule called monitoring that runs weekdays at 8am targeting arn:aws:lambda:us-east-1:123456789012:function:health-check"
            ]
        }
    ]
    
    for category in examples:
        print(f"\n{category['category']}:")
        for example in category['examples']:
            print(f"  • {example}")


def main():
    """Main test function."""
    
    print("🎯 EventBridge Optional Target Test")
    print("=" * 60)
    
    # Test agent queries (requires OpenAI API key)
    test_optional_target_queries()
    
    # Show usage examples
    demonstrate_usage()
    
    print("\n✅ Test completed!")
    print("\nKey Points:")
    print("• Target ARN is now optional when creating EventBridge rules")
    print("• Rules can be created without targets and configured later")
    print("• The agent will prompt for target ARN only if needed")
    print("• CLI supports both with and without target ARN")


if __name__ == "__main__":
    main() 