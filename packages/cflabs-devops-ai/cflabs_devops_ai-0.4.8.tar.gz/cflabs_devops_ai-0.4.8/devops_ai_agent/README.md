# DevOps AI Agent

An AI-powered command-line interface that converts natural language queries into DevOps commands using OpenAI's GPT models.

## Features

- **Natural Language Processing**: Convert human queries into structured DevOps commands
- **Interactive Chat Mode**: Chat with the AI agent in real-time
- **Multiple DevOps Operations**: Support for deployment, workflow creation, status checks, and more
- **Confidence Scoring**: AI provides confidence levels for command parsing
- **Error Handling**: Robust error handling and user feedback

## Installation

1. Install the package:
```bash
pip install -e .
```

2. Set your OpenAI API key:
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

## Usage

### Interactive Chat Mode

Start the AI agent in interactive mode:

```bash
devops-ai-agent chat
```

This will start an interactive session where you can type natural language queries like:

- "deploy this flask app on aws lambda with memory as 1 GB and timeout as 300 seconds"
- "create a github actions workflow for my flask app"
- "check the status of my deployment"
- "view logs from my lambda function"
- "delete my deployment"

### Test Mode

Test the AI agent with a specific query:

```bash
devops-ai-agent test "deploy this flask app on aws lambda with memory as 1 GB and timeout as 300 seconds"
```

### Non-Interactive Mode

Run a single query without interactive mode:

```bash
devops-ai-agent chat --no-interactive
```

## Supported Commands

The AI agent can understand and execute the following types of commands:

### 1. Deploy Flask App (`deploy_flask_app`)
Deploy a Flask application to AWS Lambda.

**Parameters:**
- `lambda_name`: Name for the Lambda function
- `region`: AWS region (default: us-east-1)
- `memory_size`: Lambda memory in MB (default: 512)
- `timeout`: Lambda timeout in seconds (default: 30)
- `port`: Application port (default: 8000)

**Example Queries:**
- "deploy this flask app on aws lambda"
- "deploy my app with 1 GB memory and 300 second timeout"
- "deploy to us-west-2 region with 2 GB memory"

### 2. Create GitHub Workflow (`create_github_workflow`)
Create a GitHub Actions workflow for CI/CD.

**Parameters:**
- `lambda_name`: Name for the Lambda function
- `region`: AWS region (default: us-east-1)
- `stack_name`: CloudFormation stack name

**Example Queries:**
- "create a github actions workflow for my flask app"
- "set up CI/CD pipeline for my lambda function"

### 3. Check Status (`check_status`)
Check the status of a deployment.

**Parameters:**
- `lambda_name`: Name for the Lambda function
- `region`: AWS region

**Example Queries:**
- "check the status of my deployment"
- "what's the status of my lambda function"

### 4. View Logs (`view_logs`)
View logs from a Lambda function.

**Parameters:**
- `lambda_name`: Name for the Lambda function
- `region`: AWS region
- `lines`: Number of log lines (default: 50)

**Example Queries:**
- "view logs from my lambda function"
- "show me the last 100 log lines"

### 5. Delete Deployment (`delete_deployment`)
Delete a deployment.

**Parameters:**
- `lambda_name`: Name for the Lambda function
- `region`: AWS region

**Example Queries:**
- "delete my deployment"
- "remove my lambda function"

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)

### API Key Setup

1. Get an OpenAI API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Set the environment variable:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
3. Or pass it as a command-line option:
   ```bash
   devops-ai-agent chat --api-key "your-api-key-here"
   ```

## Examples

### Basic Usage

```bash
# Start interactive chat
devops-ai-agent chat

# Test a specific query
devops-ai-agent test "deploy this flask app with 1 GB memory"

# Run without interactive mode
devops-ai-agent chat --no-interactive
```

### Example Session

```
🚀 Welcome
─────────────────────────────────────────────────────────────
DevOps AI Agent

I can help you with DevOps tasks using natural language!

Examples:
• 'deploy this flask app on aws lambda with memory as 1 GB and timeout as 300 seconds'
• 'create a github actions workflow for my flask app'
• 'check the status of my deployment'
• 'view logs from my lambda function'
• 'delete my deployment'

Type 'quit' or 'exit' to stop.

What would you like me to do? deploy this flask app on aws lambda with memory as 1 GB and timeout as 300 seconds

🤖 Analyzing your request...
✅ Understood: deploy_flask_app

Parameters:
┌─────────────┬───────┐
│ Parameter   │ Value │
├─────────────┼───────┤
│ memory_size │ 1024  │
│ timeout     │ 300   │
└─────────────┴───────┘

🚀 Executing command...
Executing: devops-ai deploy --memory 1024 --timeout 300
✅ Deployment successful!
```

## Error Handling

The AI agent includes robust error handling:

- **API Errors**: Handles OpenAI API connection issues
- **Parsing Errors**: Gracefully handles malformed AI responses
- **Command Errors**: Provides detailed feedback for failed commands
- **Confidence Scoring**: Warns when confidence is low

## Development

### Running Tests

```bash
python test_agent.py
```

### Building

```bash
python -m build
```

## Dependencies

- `openai>=1.0.0`: OpenAI API client
- `typer>=0.9.0`: Command-line interface
- `rich>=13.0.0`: Rich terminal output
- `devops-ai`: The underlying DevOps automation tool

## License

MIT License - see LICENSE file for details. 