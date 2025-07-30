# DevOps AI Unified CLI

A unified command-line interface that combines all DevOps AI modules into a single, powerful tool.

## 🚀 Features

- **Flask/Lambda Deployment**: Deploy Flask apps to AWS Lambda with zero code changes
- **React/Amplify Deployment**: Deploy React apps to AWS Amplify with branch management
- **EventBridge Rules**: Create, manage, and schedule AWS EventBridge rules
- **GitHub Actions**: Generate CI/CD workflows for automated deployment
- **AI-Powered Interface**: Natural language commands with OpenAI integration

## 📦 Installation

```bash
pip install devops-ai
```

## 🎯 Quick Start

### Deploy Flask App to AWS Lambda

```bash
# Deploy with default settings
devops-ai-unified deploy

# Deploy with custom configuration
devops-ai-unified deploy --name my-app --memory 1024 --timeout 60
```

### Deploy React App to AWS Amplify

```bash
# Create Amplify app
devops-ai-unified amplify create-app --name my-react-app --repo https://github.com/username/my-react-app

# Configure for React
devops-ai-unified amplify configure-app --framework react

# Deploy main branch
devops-ai-unified amplify deploy-branch --branch main
```

### Create EventBridge Rules

```bash
# Create a daily backup rule
devops-ai-unified eventbridge create-rule --name backup-rule --description "daily at 2am"

# Create a rule with Indian timezone
devops-ai-unified eventbridge create-rule --name backup-rule --description "daily at 9am indian time"
```

### Generate GitHub Actions Workflow

```bash
# Generate CI/CD workflow
devops-ai-unified github-actions create-workflow --name my-app
```

### AI-Powered Interface

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Start the AI agent
devops-ai-unified chat
```

Then simply type: *"deploy this flask app on aws lambda with memory as 1 GB"* or *"create an eventbridge rule called backup-rule that runs daily at 2am"*

## 📋 Available Commands

### Serverless/Lambda Commands

#### `deploy`
Deploy Flask app to AWS Lambda + API Gateway:

```bash
devops-ai-unified deploy [OPTIONS]
```

**Options:**
- `--name, -n`: Name for your Lambda function
- `--region, -r`: AWS region (default: us-east-1)
- `--port, -p`: Application port (default: 8000)
- `--memory`: Lambda memory size in MB (default: 512)
- `--timeout, -t`: Lambda timeout in seconds (default: 30)
- `--image-tag, -i`: Docker image tag to use for deployment
- `--config, -c`: Path to config file
- `--debug, -d`: Enable debug mode with verbose output

#### `generate`
Generate deployment files without deploying:

```bash
devops-ai-unified generate [OPTIONS]
```

**Options:**
- `--name, -n`: Name for your Lambda function
- `--region, -r`: AWS region (default: us-east-1)
- `--port, -p`: Application port (default: 8000)
- `--memory`: Lambda memory size in MB (default: 512)
- `--timeout, -t`: Lambda timeout in seconds (default: 30)
- `--image-tag, -i`: Docker image tag to use for deployment
- `--config, -c`: Path to config file
- `--force, -f`: Overwrite existing files

#### `logs`
Stream logs from your deployed function:

```bash
devops-ai-unified logs [OPTIONS]
```

**Options:**
- `--config, -c`: Path to config file
- `--stack-name, -s`: Name of the CloudFormation stack
- `--region, -r`: AWS region
- `--function, -f`: Specific Lambda function name
- `--follow`: Follow logs in real-time
- `--lines, -n`: Number of log lines to show (default: 50)

#### `delete`
Remove the deployed stack and clean up ECR:

```bash
devops-ai-unified delete [OPTIONS]
```

**Options:**
- `--config, -c`: Path to config file
- `--force, -f`: Skip confirmation

#### `status`
Show deployment status and information:

```bash
devops-ai-unified status [OPTIONS]
```

**Options:**
- `--config, -c`: Path to config file

### AI Agent Commands

#### `chat`
Start the AI agent in interactive chat mode:

```bash
devops-ai-unified chat [OPTIONS]
```

**Options:**
- `--api-key, -k`: OpenAI API key (optional, can use environment variable)
- `--interactive, -i`: Run in interactive mode (default: true)

#### `test`
Test the AI agent with a specific query:

```bash
devops-ai-unified test <QUERY> [OPTIONS]
```

**Options:**
- `--api-key, -k`: OpenAI API key (optional, can use environment variable)

### EventBridge Commands

#### `eventbridge create-rule`
Create a new EventBridge rule:

```bash
devops-ai-unified eventbridge create-rule [OPTIONS]
```

**Options:**
- `--name`: Name of the rule
- `--description`: Natural language description of schedule
- `--target-arn`: ARN of the target (optional)
- `--region, -r`: AWS region (default: us-east-1)
- `--target-id`: Optional target ID

#### `eventbridge list-rules`
List all EventBridge rules:

```bash
devops-ai-unified eventbridge list-rules [OPTIONS]
```

**Options:**
- `--region, -r`: AWS region (default: us-east-1)
- `--prefix`: Optional prefix to filter rules

#### `eventbridge delete-rule`
Delete an EventBridge rule:

```bash
devops-ai-unified eventbridge delete-rule [OPTIONS]
```

**Options:**
- `--name`: Name of the rule to delete
- `--region, -r`: AWS region (default: us-east-1)
- `--force`: Force deletion by removing targets first

#### `eventbridge update-rule`
Update an EventBridge rule:

```bash
devops-ai-unified eventbridge update-rule [OPTIONS]
```

**Options:**
- `--name`: Name of the rule to update
- `--description`: New natural language description of schedule
- `--region, -r`: AWS region (default: us-east-1)

#### `eventbridge show-rule`
Show details of an EventBridge rule:

```bash
devops-ai-unified eventbridge show-rule [OPTIONS]
```

**Options:**
- `--name`: Name of the rule to show
- `--region, -r`: AWS region (default: us-east-1)

### GitHub Actions Commands

#### `github-actions create-workflow`
Generate GitHub Actions workflow for CI/CD:

```bash
devops-ai-unified github-actions create-workflow [OPTIONS]
```

**Options:**
- `--name, -n`: Name for your Lambda function
- `--region, -r`: AWS region (default: us-east-1)
- `--stack-name, -s`: Name of the CloudFormation stack
- `--ecr-repo`: ECR repository name
- `--config, -c`: Path to config file
- `--force, -f`: Overwrite existing workflow file

### Amplify Commands

#### `amplify create-app`
Create new Amplify app and connect to GitHub:

```bash
devops-ai-unified amplify create-app [OPTIONS]
```

**Options:**
- `--name`: Name for the Amplify app
- `--repository`: GitHub repository URL
- `--branch`: Default branch (default: main)
- `--region, -r`: AWS region (default: us-east-1)
- `--framework`: Framework type: react, nextjs, vue, angular (default: react)

#### `amplify deploy-branch`
Deploy specific branch to Amplify:

```bash
devops-ai-unified amplify deploy-branch [OPTIONS]
```

**Options:**
- `--branch`: Branch to deploy
- `--app-id`: Amplify app ID (optional - will be loaded from config)
- `--region, -r`: AWS region (default: us-east-1)
- `--wait`: Wait for deployment to complete (default: true)

#### `amplify configure-app`
Configure app with framework-specific settings:

```bash
devops-ai-unified amplify configure-app [OPTIONS]
```

**Options:**
- `--app-id`: Amplify app ID (optional - will be loaded from config)
- `--region, -r`: AWS region (default: us-east-1)
- `--framework`: Framework: react, nextjs, vue, angular (default: react)
- `--force`: Overwrite existing files (default: false)

#### `amplify list-apps`
List all Amplify apps in a region:

```bash
devops-ai-unified amplify list-apps [OPTIONS]
```

**Options:**
- `--region, -r`: AWS region (default: us-east-1)

#### `amplify list-branches`
List all branches for an app:

```bash
devops-ai-unified amplify list-branches [OPTIONS]
```

**Options:**
- `--app-id`: Amplify app ID
- `--region, -r`: AWS region (default: us-east-1)

#### `amplify create-branch`
Create new branch for deployment:

```bash
devops-ai-unified amplify create-branch [OPTIONS]
```

**Options:**
- `--branch`: Branch name to create
- `--app-id`: Amplify app ID (optional - will be loaded from config)
- `--region, -r`: AWS region (default: us-east-1)
- `--enable-auto-build`: Enable auto build (default: true)
- `--enable-pull-request-preview`: Enable PR preview (default: true)

#### `amplify delete-app`
Delete an Amplify app:

```bash
devops-ai-unified amplify delete-app [OPTIONS]
```

**Options:**
- `--app-id`: Amplify app ID
- `--region, -r`: AWS region (default: us-east-1)
- `--force`: Skip confirmation (default: false)

#### `amplify delete-branch`
Delete a branch:

```bash
devops-ai-unified amplify delete-branch [OPTIONS]
```

**Options:**
- `--branch`: Branch name to delete
- `--app-id`: Amplify app ID (optional - will be loaded from config)
- `--region, -r`: AWS region (default: us-east-1)
- `--force`: Skip confirmation (default: false)

#### `amplify status`
Show app status and branches:

```bash
devops-ai-unified amplify status [OPTIONS]
```

**Options:**
- `--app-id`: Amplify app ID (optional - will be loaded from config)
- `--region, -r`: AWS region (default: us-east-1)

## 🧠 AI-Powered Examples

The AI agent can understand and execute these types of commands:

### Flask/Lambda Deployment
- "deploy this flask app on aws lambda with memory as 1 GB and timeout as 300 seconds"
- "create a github actions workflow for my flask app"
- "check the status of my deployment"
- "view logs from my lambda function"
- "delete my deployment"

### EventBridge Rules
- "create an eventbridge rule called backup-rule that runs daily at 2am"
- "create an eventbridge rule called backup-rule that runs daily at 9am indian time"
- "list all eventbridge rules"
- "delete the eventbridge rule called backup-rule"
- "update my eventbridge rule to run every 6 hours"

### AWS Amplify
- "deploy this react app to amplify with repository https://github.com/username/my-react-app"
- "deploy the main branch to amplify and wait for completion"
- "configure my amplify app for nextjs framework"
- "list all amplify apps"
- "create a feature branch called new-ui for my amplify app"
- "check the status of my amplify app"

## 🔧 Prerequisites

- Python 3.8+
- AWS CLI configured with appropriate permissions
- Docker installed and running
- AWS SAM CLI installed
- OpenAI API key (for AI features)

## 📄 License

MIT License - see [LICENSE](../LICENSE) file for details. 