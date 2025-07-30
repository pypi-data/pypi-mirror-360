# EventBridge Integration with DevOps AI Agent

This document explains how the EventBridge module integrates with the DevOps AI Agent to provide natural language interface for AWS EventBridge management.

## Overview

The EventBridge integration allows you to create, manage, and monitor AWS EventBridge rules using natural language commands through the AI agent. The agent uses OpenAI's GPT models to parse natural language queries and convert them into structured EventBridge operations.

## Features

### Natural Language Processing
- Convert human-readable descriptions to cron expressions
- Support for various time patterns and schedules
- Intelligent parsing of complex scheduling requirements

### EventBridge Operations
- **Create Rules**: Create EventBridge rules with natural language schedules
- **List Rules**: List and filter EventBridge rules
- **Update Rules**: Modify existing rule schedules
- **Delete Rules**: Remove EventBridge rules with optional force deletion
- **Show Details**: Get detailed information about specific rules

### AI Agent Integration
- Seamless integration with the existing DevOps AI Agent
- Interactive chat interface for EventBridge management
- Automatic parameter extraction and validation
- User-friendly prompts for missing information

## Usage Examples

### Interactive Agent Mode

Start the agent in interactive mode:
```bash
devops-ai-agent chat
```

Then use natural language commands:
```
> create an eventbridge rule called backup-rule that runs daily at 2am
> list all eventbridge rules
> update my backup rule to run every 6 hours
> delete the backup rule with force
```

### Direct CLI Usage

Use the EventBridge CLI directly:
```bash
# Create a rule
devops-ai eventbridge create "backup-rule" "daily at 2am" "arn:aws:lambda:us-east-1:123456789012:function:backup"

# List rules
devops-ai eventbridge list

# Convert text to cron
devops-ai eventbridge convert "every monday at 9am"

# Show examples
devops-ai eventbridge examples
```

### Programmatic Usage

```python
from devops_ai_agent.agent import DevOpsAIAgent
from devops_ai_eventbridge.cron_converter import CronConverter

# Initialize agent
agent = DevOpsAIAgent(openai_api_key="your-api-key")

# Parse natural language query
parsed = agent.parse_query("create an eventbridge rule called backup that runs daily at 2am")

# Execute the command
success = agent.execute_command(parsed["command"], parsed["parameters"])

# Use cron converter directly
converter = CronConverter()
cron_expression = converter.text_to_cron("daily at 9am")
print(f"Cron: {cron_expression}")  # Output: 0 9 * * *
```

## Supported Natural Language Patterns

### Rate Expressions (Recommended for Simple Intervals)
- `every 2 minutes` → `rate(2 minutes)`
- `every 1 minute` → `rate(1 minute)`
- `every 3 hours` → `rate(3 hours)`
- `every 1 hour` → `rate(1 hour)`
- `every 5 days` → `rate(5 days)`
- `every 1 day` → `rate(1 day)`
- `every 2 weeks` → `rate(14 days)`

### Cron Expressions (For Complex Schedules)
- `daily at 9am` → `cron(0 9 * * ? *)`
- `every monday at 2pm` → `cron(0 14 ? * 1 *)`
- `weekly on friday at 5pm` → `cron(0 17 ? * 5 *)`
- `monthly on the 15th` → `cron(0 0 15 * ? *)`
- `yearly on january 1st` → `cron(0 0 1 1 ? *)`

### Business Patterns
- `weekdays at 8am` → `cron(0 8 ? * 1-5 *)`
- `weekends at 10am` → `cron(0 10 ? * 0,6 *)`

### Specific Days
- `monday at 9am` → `cron(0 9 ? * 1 *)`
- `friday at 5pm` → `cron(0 17 ? * 5 *)`

## Agent Commands

The enhanced agent supports the following EventBridge commands:

### 1. create_eventbridge_rule
Creates a new EventBridge rule with natural language schedule description.

**Parameters:**
- `rule_name`: Name of the EventBridge rule
- `description`: Natural language description of schedule
- `target_arn`: ARN of the target (Lambda, SQS, etc.)
- `region`: AWS region (default: us-east-1)
- `target_id`: Optional target ID

**Example:**
```
"create an eventbridge rule called backup-rule that runs daily at 2am targeting my lambda function"
```

### 2. list_eventbridge_rules
Lists EventBridge rules with optional filtering.

**Parameters:**
- `region`: AWS region (default: us-east-1)
- `prefix`: Optional prefix to filter rules

**Example:**
```
"list all eventbridge rules in us-east-1"
"list eventbridge rules with prefix backup"
```

### 3. delete_eventbridge_rule
Deletes an EventBridge rule.

**Parameters:**
- `rule_name`: Name of the rule to delete
- `region`: AWS region (default: us-east-1)
- `force`: Force deletion by removing targets first

**Example:**
```
"delete the eventbridge rule called backup-rule"
"delete the eventbridge rule called report-rule with force"
```

### 4. update_eventbridge_rule
Updates an existing EventBridge rule's schedule.

**Parameters:**
- `rule_name`: Name of the rule to update
- `description`: New natural language description of schedule
- `region`: AWS region (default: us-east-1)

**Example:**
```
"update my eventbridge rule called backup-rule to run every 6 hours"
"update the backup rule to run daily at 3am instead"
```

### 5. show_eventbridge_rule
Shows detailed information about a specific EventBridge rule.

**Parameters:**
- `rule_name`: Name of the rule to show
- `region`: AWS region (default: us-east-1)

**Example:**
```
"show details for the eventbridge rule called backup-rule"
```

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Required for AI agent functionality
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_DEFAULT_REGION`: Default AWS region
- `AWS_PROFILE`: AWS profile name

### AWS Credentials
The module supports standard AWS credential providers:
1. Environment variables
2. AWS profiles
3. IAM roles (when running on EC2/ECS)
4. AWS CLI configuration

## Error Handling

The integration provides comprehensive error handling:

- **Invalid Descriptions**: Graceful fallback to default schedules
- **AWS Errors**: Detailed error messages for AWS API failures
- **Validation**: Cron expression validation
- **Credentials**: Clear error messages for missing AWS credentials
- **Agent Errors**: User-friendly error messages for parsing failures

## Testing

### Test the Agent
```bash
# Test specific query
devops-ai-agent test "create an eventbridge rule called backup-rule that runs daily at 2am"

# Run interactive mode
devops-ai-agent chat
```

### Test Cron Conversion
```bash
# Test cron conversion
devops-ai eventbridge convert "daily at 9am"

# Show examples
devops-ai eventbridge examples
```

### Run Test Scripts
```bash
# Test EventBridge agent functionality
python devops_ai_agent/test_eventbridge_agent.py

# Run comprehensive example
python examples/eventbridge_agent_example.py
```

## Examples

### Common Use Cases

**Daily Backup:**
```
"create an eventbridge rule called daily-backup that runs daily at 2am targeting my lambda function"
```

**Weekly Report:**
```
"create an eventbridge rule called weekly-report that runs every monday at 9am targeting my lambda function"
```

**Cleanup Job:**
```
"create an eventbridge rule called cleanup that runs every 6 hours targeting my lambda function"
```

**Business Hours Monitoring:**
```
"create an eventbridge rule called monitoring that runs weekdays at 8am targeting my lambda function"
```

### Complex Schedules

**Multiple Times Per Day:**
```
"create an eventbridge rule called morning-check that runs daily at 8am"
"create an eventbridge rule called afternoon-check that runs daily at 2pm"
"create an eventbridge rule called evening-check that runs daily at 6pm"
```

## Troubleshooting

### Common Issues

1. **OpenAI API Key Missing**
   - Set `OPENAI_API_KEY` environment variable
   - Or pass it to the agent constructor

2. **AWS Credentials Missing**
   - Configure AWS credentials using AWS CLI
   - Or set environment variables

3. **Invalid Cron Expression**
   - Check the natural language description
   - Use `devops-ai eventbridge convert` to test

4. **EventBridge Rule Creation Fails**
   - Verify target ARN exists and is accessible
   - Check AWS permissions for EventBridge

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
devops-ai-agent chat
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This integration is part of the DevOps AI project and is licensed under the MIT License. 