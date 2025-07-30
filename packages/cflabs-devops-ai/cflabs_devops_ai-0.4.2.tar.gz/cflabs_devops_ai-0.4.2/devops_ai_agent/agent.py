"""DevOps AI Agent - Natural language interface for DevOps operations."""

import os
import json
import subprocess
import typer
from typing import Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
import openai
from dotenv import load_dotenv

console = Console()

class DevOpsAIAgent:
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the DevOps AI Agent."""
        # Load environment variables from .env file
        load_dotenv()
        
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it to the constructor.")
        
        openai.api_key = self.openai_api_key
        self.client = openai.OpenAI(api_key=self.openai_api_key)
    
    def parse_query(self, user_query: str) -> Dict[str, Any]:
        """Parse natural language query into structured command parameters."""
        
        system_prompt = """You are a DevOps AI assistant that converts natural language queries into structured command parameters.

Available commands and their parameters:
1. deploy_flask_app:
   - lambda_name: str (name for the Lambda function)
   - region: str (AWS region, default: ap-south-1)
   - memory_size: int (Lambda memory in MB, default: 512)
   - timeout: int (Lambda timeout in seconds, default: 30)
   - port: int (application port, default: 8000)

2. create_github_workflow:
   - lambda_name: str (name for the Lambda function)
   - region: str (AWS region, default: us-east-1)
   - stack_name: str (CloudFormation stack name, optional - will be auto-generated)
   - ecr_repository: str (ECR repository name, optional - will be auto-generated)
   - config_path: str (path to config file, optional)

3. check_status:
   - lambda_name: str (name for the Lambda function)
   - region: str (AWS region)

4. view_logs:
   - lambda_name: str (name for the Lambda function)
   - region: str (AWS region)
   - lines: int (number of log lines, default: 50)

5. delete_deployment:
   - lambda_name: str (name for the Lambda function)
   - region: str (AWS region)

6. create_eventbridge_rule:
   - rule_name: str (name for the EventBridge rule)
   - description: str (natural language description of schedule, e.g., "daily at 9am", "every monday at 2pm", "daily at 9am indian time")
   - target_arn: str (ARN of the target Lambda, SQS, etc.) - optional
   - region: str (AWS region, default: ap-south-1)
   - target_id: str (optional target ID)
   
   Note: For Indian timezone, include "indian time", "ist", "india time", or "indian" in the description.
   The system will automatically convert IST to UTC (subtract 5:30 hours).

7. list_eventbridge_rules:
   - region: str (AWS region, default: us-east-1)
   - prefix: str (optional prefix to filter rules)

8. delete_eventbridge_rule:
   - rule_name: str (name of the rule to delete)
   - region: str (AWS region, default: us-east-1)
   - force: bool (force deletion by removing targets first)

9. update_eventbridge_rule:
   - rule_name: str (name of the rule to update)
   - description: str (new natural language description of schedule)
   - region: str (AWS region, default: us-east-1)

10. show_eventbridge_rule:
    - rule_name: str (name of the rule to show)
    - region: str (AWS region, default: us-east-1)

11. create_amplify_app:
    - app_name: str (name for the Amplify app)
    - repository: str (GitHub repository URL)
    - branch: str (default branch, default: main)
    - region: str (AWS region, default: us-east-1)
    - framework: str (framework type: react, nextjs, vue, angular, default: react)

12. deploy_amplify_branch:
    - branch: str (branch to deploy)
    - app_id: str (Amplify app ID, optional - will be loaded from config)
    - region: str (AWS region, default: us-east-1)
    - wait: bool (wait for deployment to complete, default: true)

13. configure_amplify_app:
    - app_id: str (Amplify app ID, optional - will be loaded from config)
    - region: str (AWS region, default: us-east-1)
    - framework: str (framework: react, nextjs, vue, angular, default: react)
    - force: bool (overwrite existing files, default: false)

14. list_amplify_apps:
    - region: str (AWS region, default: us-east-1)

15. list_amplify_branches:
    - app_id: str (Amplify app ID)
    - region: str (AWS region, default: us-east-1)

16. create_amplify_branch:
    - branch: str (branch name to create)
    - app_id: str (Amplify app ID, optional - will be loaded from config)
    - region: str (AWS region, default: us-east-1)
    - enable_auto_build: bool (enable auto build, default: true)
    - enable_pull_request_preview: bool (enable PR preview, default: true)

17. delete_amplify_app:
    - app_id: str (Amplify app ID)
    - region: str (AWS region, default: us-east-1)
    - force: bool (skip confirmation, default: false)

18. delete_amplify_branch:
    - branch: str (branch name to delete)
    - app_id: str (Amplify app ID, optional - will be loaded from config)
    - region: str (AWS region, default: us-east-1)
    - force: bool (skip confirmation, default: false)

19. amplify_status:
    - app_id: str (Amplify app ID, optional - will be loaded from config)
    - region: str (AWS region, default: us-east-1)

Extract the command and parameters from the user query. Return a JSON object with:
- command: the command to execute
- parameters: dict of parameters for the command
- confidence: float between 0 and 1 indicating confidence in the parsing
- missing_info: list of missing parameters that need user input

Example input: "create an eventbridge rule called backup-rule that runs daily at 2am indian time"
Example output: {
  "command": "create_eventbridge_rule",
  "parameters": {
    "rule_name": "backup-rule",
    "description": "daily at 2am indian time"
  },
  "confidence": 0.95,
  "missing_info": ["region"]
}

Example input: "create an eventbridge rule called backup-rule that runs daily at 2am targeting my lambda function"
Example output: {
  "command": "create_eventbridge_rule",
  "parameters": {
    "rule_name": "backup-rule",
    "description": "daily at 2am",
    "target_arn": "arn:aws:lambda:us-east-1:123456789012:function:my-function"
  },
  "confidence": 0.95,
  "missing_info": ["region"]
}

Example input: "deploy this flask app on aws lambda with memory as 1 GB and timeout as 300 seconds"
Example output: {
  "command": "deploy_flask_app",
  "parameters": {
    "lambda_name": "my-flask-app",
    "region": "ap-south-1",
    "memory_size": 1024,
    "timeout": 300,
    "port": 8000
  },
  "confidence": 0.95,
  "missing_info": []
}

Example input: "create a github actions workflow for my flask app called my-app in us-west-2"
Example output: {
  "command": "create_github_workflow",
  "parameters": {
    "lambda_name": "my-app",
    "region": "us-west-2"
  },
  "confidence": 0.95,
  "missing_info": []
}

Example input: "deploy this react app to amplify with repository https://github.com/username/my-react-app"
Example output: {
  "command": "create_amplify_app",
  "parameters": {
    "app_name": "my-react-app",
    "repository": "https://github.com/username/my-react-app",
    "branch": "main",
    "region": "us-east-1",
    "framework": "react"
  },
  "confidence": 0.95,
  "missing_info": []
}

Example input: "deploy the main branch to amplify and wait for completion"
Example output: {
  "command": "deploy_amplify_branch",
  "parameters": {
    "branch": "main",
    "region": "us-east-1",
    "wait": true
  },
  "confidence": 0.95,
  "missing_info": []
}

Example input: "configure my amplify app for nextjs framework"
Example output: {
  "command": "configure_amplify_app",
  "parameters": {
    "framework": "nextjs",
    "region": "us-east-1",
    "force": false
  },
  "confidence": 0.95,
  "missing_info": []
}
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            result = response.choices[0].message.content.strip()
            
            # Try to parse as JSON
            try:
                parsed = json.loads(result)
                
                # If there's missing information, prompt the user for it
                if parsed.get("missing_info"):
                    parsed = self._get_missing_info_from_user(parsed)
                
                return parsed
            except json.JSONDecodeError:
                # If not valid JSON, try to extract from the response
                console.print(f"[yellow]Warning: Could not parse AI response as JSON: {result}[/yellow]")
                return {
                    "command": "unknown",
                    "parameters": {},
                    "confidence": 0.0,
                    "raw_response": result
                }
                
        except Exception as e:
            console.print(f"[red]Error calling OpenAI API: {e}[/red]")
            return {
                "command": "error",
                "parameters": {},
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _get_missing_info_from_user(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Prompt user for missing information and update parameters."""
        
        missing_info = parsed.get("missing_info", [])
        parameters = parsed.get("parameters", {})
        
        if not missing_info:
            return parsed
        
        console.print(f"\n[bold yellow]🔍 Additional Information Needed[/bold yellow]")
        console.print("=" * 50)
        
        # Define parameter descriptions and defaults
        param_descriptions = {
            "lambda_name": {
                "description": "Lambda function name",
                "default": "my-flask-app",
                "type": "str"
            },
            "region": {
                "description": "AWS region",
                "default": "ap-south-1",
                "type": "str"
            },
            "memory_size": {
                "description": "Memory size (MB)",
                "default": 512,
                "type": "int"
            },
            "timeout": {
                "description": "Timeout (seconds)",
                "default": 30,
                "type": "int"
            },
            "port": {
                "description": "Application port",
                "default": 8000,
                "type": "int"
            },
            "lines": {
                "description": "Number of log lines",
                "default": 50,
                "type": "int"
            },
            "stack_name": {
                "description": "CloudFormation stack name",
                "default": "my-stack",
                "type": "str"
            },
            "rule_name": {
                "description": "EventBridge rule name",
                "default": "my-eventbridge-rule",
                "type": "str"
            },
            "description": {
                "description": "Schedule description (e.g., 'daily at 9am', 'every monday at 2pm')",
                "default": "daily at 9am",
                "type": "str"
            },
            "target_arn": {
                "description": "Target ARN (Lambda, SQS, etc.) - optional",
                "default": "",
                "type": "str"
            },
            "target_id": {
                "description": "Target ID (optional)",
                "default": "",
                "type": "str"
            },
            "prefix": {
                "description": "Rule name prefix filter",
                "default": "",
                "type": "str"
            },
            "force": {
                "description": "Force deletion (true/false)",
                "default": False,
                "type": "bool"
            }
        }
        
        # Show what we have so far
        if parameters:
            table = Table(title="Current Parameters")
            table.add_column("Parameter", style="cyan")
            table.add_column("Value", style="green")
            
            for key, value in parameters.items():
                table.add_row(key, str(value))
            
            console.print(table)
        
        # Ask for missing information
        console.print(f"\n[blue]Please provide the following information:[/blue]")
        
        for param in missing_info:
            if param in param_descriptions:
                desc = param_descriptions[param]
                default_value = desc["default"]
                
                # Get user input
                user_input = Prompt.ask(
                    f"[cyan]{desc['description']}[/cyan]",
                    default=str(default_value)
                )
                
                # Convert to appropriate type
                if desc["type"] == "int":
                    try:
                        user_input = int(user_input)
                    except ValueError:
                        console.print(f"[red]Invalid number, using default: {default_value}[/red]")
                        user_input = default_value
                elif desc["type"] == "bool":
                    if user_input.lower() in ['true', 'yes', 'y', '1']:
                        user_input = True
                    elif user_input.lower() in ['false', 'no', 'n', '0']:
                        user_input = False
                    else:
                        console.print(f"[red]Invalid boolean, using default: {default_value}[/red]")
                        user_input = default_value
                
                parameters[param] = user_input
        
        # Update the parsed result
        parsed["parameters"] = parameters
        parsed["missing_info"] = []  # Clear missing info since we got it
        
        console.print(f"\n[green]✅ All required information collected![/green]")
        
        return parsed
    
    def execute_command(self, command: str, parameters: Dict[str, Any]) -> bool:
        """Execute the parsed command with the given parameters."""
        
        try:
            if command == "deploy_flask_app":
                return self._deploy_flask_app(parameters)
            elif command == "create_github_workflow":
                return self._create_github_workflow(parameters)
            elif command == "check_status":
                return self._check_status(parameters)
            elif command == "view_logs":
                return self._view_logs(parameters)
            elif command == "delete_deployment":
                return self._delete_deployment(parameters)
            elif command == "create_eventbridge_rule":
                return self._create_eventbridge_rule(parameters)
            elif command == "list_eventbridge_rules":
                return self._list_eventbridge_rules(parameters)
            elif command == "delete_eventbridge_rule":
                return self._delete_eventbridge_rule(parameters)
            elif command == "update_eventbridge_rule":
                return self._update_eventbridge_rule(parameters)
            elif command == "show_eventbridge_rule":
                return self._show_eventbridge_rule(parameters)
            elif command == "create_amplify_app":
                return self._create_amplify_app(parameters)
            elif command == "deploy_amplify_branch":
                return self._deploy_amplify_branch(parameters)
            elif command == "configure_amplify_app":
                return self._configure_amplify_app(parameters)
            elif command == "list_amplify_apps":
                return self._list_amplify_apps(parameters)
            elif command == "list_amplify_branches":
                return self._list_amplify_branches(parameters)
            elif command == "create_amplify_branch":
                return self._create_amplify_branch(parameters)
            elif command == "delete_amplify_app":
                return self._delete_amplify_app(parameters)
            elif command == "delete_amplify_branch":
                return self._delete_amplify_branch(parameters)
            elif command == "amplify_status":
                return self._amplify_status(parameters)
            else:
                console.print(f"[red]Unknown command: {command}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]Error executing command: {e}[/red]")
            return False
    
    def _deploy_flask_app(self, parameters: Dict[str, Any]) -> bool:
        """Deploy Flask app to AWS Lambda."""
        try:
            # Build the devops-ai deploy command
            cmd = ["devops-ai", "deploy"]
            
            if "lambda_name" in parameters:
                cmd.extend(["--name", str(parameters["lambda_name"])])
            
            if "region" in parameters:
                cmd.extend(["--region", str(parameters["region"])])
            
            if "memory_size" in parameters:
                cmd.extend(["--memory", str(parameters["memory_size"])])
            
            if "timeout" in parameters:
                cmd.extend(["--timeout", str(parameters["timeout"])])
            
            if "port" in parameters:
                cmd.extend(["--port", str(parameters["port"])])
            
            console.print(f"[blue]Executing: {' '.join(cmd)}[/blue]")
            
            # Execute the command directly in the terminal (no subprocess capture)
            # This allows Rich progress bars and console output to work properly
            result = subprocess.run(cmd, check=False)
            
            if result.returncode == 0:
                console.print(f"[green]✅ Deployment successful![/green]")
                return True
            else:
                console.print(f"[red]❌ Deployment failed with return code: {result.returncode}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]Error in deployment: {e}[/red]")
            return False
    
    def _create_github_workflow(self, parameters: Dict[str, Any]) -> bool:
        """Create GitHub Actions workflow."""
        try:
            cmd = ["devops-ai", "github-actions", "create-workflow"]
            
            if "lambda_name" in parameters:
                cmd.extend(["--name", str(parameters["lambda_name"])])
            
            if "region" in parameters:
                cmd.extend(["--region", str(parameters["region"])])
            
            if "stack_name" in parameters:
                cmd.extend(["--stack-name", str(parameters["stack_name"])])
            
            console.print(f"[blue]Executing: {' '.join(cmd)}[/blue]")
            
            # Execute the command directly in the terminal
            result = subprocess.run(cmd, check=False)
            
            if result.returncode == 0:
                console.print(f"[green]✅ GitHub Actions workflow created![/green]")
                return True
            else:
                console.print(f"[red]❌ Workflow creation failed with return code: {result.returncode}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]Error creating workflow: {e}[/red]")
            return False
    
    def _check_status(self, parameters: Dict[str, Any]) -> bool:
        """Check deployment status."""
        try:
            cmd = ["devops-ai", "status"]
            
            if "lambda_name" in parameters:
                cmd.extend(["--name", str(parameters["lambda_name"])])
            
            if "region" in parameters:
                cmd.extend(["--region", str(parameters["region"])])
            
            console.print(f"[blue]Executing: {' '.join(cmd)}[/blue]")
            
            # Execute the command directly in the terminal
            result = subprocess.run(cmd, check=False)
            
            if result.returncode == 0:
                console.print(f"[green]✅ Status retrieved![/green]")
                return True
            else:
                console.print(f"[red]❌ Status check failed with return code: {result.returncode}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]Error checking status: {e}[/red]")
            return False
    
    def _view_logs(self, parameters: Dict[str, Any]) -> bool:
        """View deployment logs."""
        try:
            cmd = ["devops-ai", "logs"]
            
            if "lambda_name" in parameters:
                cmd.extend(["--name", str(parameters["lambda_name"])])
            
            if "region" in parameters:
                cmd.extend(["--region", str(parameters["region"])])
            
            if "lines" in parameters:
                cmd.extend(["--lines", str(parameters["lines"])])
            
            console.print(f"[blue]Executing: {' '.join(cmd)}[/blue]")
            
            # Execute the command directly in the terminal
            result = subprocess.run(cmd, check=False)
            
            if result.returncode == 0:
                console.print(f"[green]✅ Logs retrieved![/green]")
                return True
            else:
                console.print(f"[red]❌ Log retrieval failed with return code: {result.returncode}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]Error viewing logs: {e}[/red]")
            return False
    
    def _delete_deployment(self, parameters: Dict[str, Any]) -> bool:
        """Delete deployment."""
        try:
            cmd = ["devops-ai", "delete", "--force"]
            
            if "lambda_name" in parameters:
                cmd.extend(["--name", str(parameters["lambda_name"])])
            
            if "region" in parameters:
                cmd.extend(["--region", str(parameters["region"])])
            
            console.print(f"[blue]Executing: {' '.join(cmd)}[/blue]")
            
            # Execute the command directly in the terminal
            result = subprocess.run(cmd, check=False)
            
            if result.returncode == 0:
                console.print(f"[green]✅ Deployment deleted![/green]")
                return True
            else:
                console.print(f"[red]❌ Deletion failed with return code: {result.returncode}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]Error deleting deployment: {e}[/red]")
            return False
    
    def _create_eventbridge_rule(self, parameters: Dict[str, Any]) -> bool:
        """Create an EventBridge rule."""
        try:
            cmd = ["devops-ai", "eventbridge", "create"]
            
            if "rule_name" in parameters:
                cmd.append(str(parameters["rule_name"]))
            else:
                console.print("[red]Error: rule_name is required[/red]")
                return False
            
            if "description" in parameters:
                cmd.append(str(parameters["description"]))
            else:
                console.print("[red]Error: description is required[/red]")
                return False
            
            # For EventBridge rules, we need to handle optional target_arn differently
            # The CLI expects target_arn as a positional argument, but it can be None
            if "target_arn" in parameters and parameters["target_arn"]:
                cmd.append(str(parameters["target_arn"]))
            else:
                # Create rule without target - this is allowed
                console.print("[yellow]Warning: No target ARN provided. Rule will be created without a target.[/yellow]")
                # Add None as a string to indicate no target
                cmd.append("None")
            
            if "region" in parameters:
                cmd.extend(["--region", str(parameters["region"])])
            
            if "target_id" in parameters and parameters["target_id"]:
                cmd.extend(["--target-id", str(parameters["target_id"])])
            
            console.print(f"[blue]Executing: {' '.join(cmd)}[/blue]")
            
            # Execute the command directly in the terminal
            result = subprocess.run(cmd, check=False)
            
            if result.returncode == 0:
                console.print(f"[green]✅ EventBridge rule created successfully![/green]")
                return True
            else:
                console.print(f"[red]❌ EventBridge rule creation failed with return code: {result.returncode}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]Error creating EventBridge rule: {e}[/red]")
            return False
    
    def _list_eventbridge_rules(self, parameters: Dict[str, Any]) -> bool:
        """List EventBridge rules."""
        try:
            cmd = ["devops-ai", "eventbridge", "list"]
            
            if "region" in parameters:
                cmd.extend(["--region", str(parameters["region"])])
            
            if "prefix" in parameters and parameters["prefix"]:
                cmd.extend(["--prefix", str(parameters["prefix"])])
            
            console.print(f"[blue]Executing: {' '.join(cmd)}[/blue]")
            
            # Execute the command directly in the terminal
            result = subprocess.run(cmd, check=False)
            
            if result.returncode == 0:
                console.print(f"[green]✅ EventBridge rules listed successfully![/green]")
                return True
            else:
                console.print(f"[red]❌ EventBridge rules listing failed with return code: {result.returncode}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]Error listing EventBridge rules: {e}[/red]")
            return False
    
    def _delete_eventbridge_rule(self, parameters: Dict[str, Any]) -> bool:
        """Delete an EventBridge rule."""
        try:
            cmd = ["devops-ai", "eventbridge", "delete"]
            
            if "rule_name" in parameters:
                cmd.append(str(parameters["rule_name"]))
            else:
                console.print("[red]Error: rule_name is required[/red]")
                return False
            
            if "region" in parameters:
                cmd.extend(["--region", str(parameters["region"])])
            
            if parameters.get("force", False):
                cmd.append("--force")
            
            console.print(f"[blue]Executing: {' '.join(cmd)}[/blue]")
            
            # Execute the command directly in the terminal
            result = subprocess.run(cmd, check=False)
            
            if result.returncode == 0:
                console.print(f"[green]✅ EventBridge rule deleted successfully![/green]")
                return True
            else:
                console.print(f"[red]❌ EventBridge rule deletion failed with return code: {result.returncode}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]Error deleting EventBridge rule: {e}[/red]")
            return False
    
    def _update_eventbridge_rule(self, parameters: Dict[str, Any]) -> bool:
        """Update an EventBridge rule."""
        try:
            cmd = ["devops-ai", "eventbridge", "update"]
            
            if "rule_name" in parameters:
                cmd.append(str(parameters["rule_name"]))
            else:
                console.print("[red]Error: rule_name is required[/red]")
                return False
            
            if "description" in parameters:
                cmd.append(str(parameters["description"]))
            else:
                console.print("[red]Error: description is required[/red]")
                return False
            
            if "region" in parameters:
                cmd.extend(["--region", str(parameters["region"])])
            
            console.print(f"[blue]Executing: {' '.join(cmd)}[/blue]")
            
            # Execute the command directly in the terminal
            result = subprocess.run(cmd, check=False)
            
            if result.returncode == 0:
                console.print(f"[green]✅ EventBridge rule updated successfully![/green]")
                return True
            else:
                console.print(f"[red]❌ EventBridge rule update failed with return code: {result.returncode}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]Error updating EventBridge rule: {e}[/red]")
            return False
    
    def _show_eventbridge_rule(self, parameters: Dict[str, Any]) -> bool:
        """Show EventBridge rule details."""
        try:
            cmd = ["devops-ai", "eventbridge", "show"]
            
            if "rule_name" in parameters:
                cmd.append(str(parameters["rule_name"]))
            else:
                console.print("[red]Error: rule_name is required[/red]")
                return False
            
            if "region" in parameters:
                cmd.extend(["--region", str(parameters["region"])])
            
            console.print(f"[blue]Executing: {' '.join(cmd)}[/blue]")
            
            # Execute the command directly in the terminal
            result = subprocess.run(cmd, check=False)
            
            if result.returncode == 0:
                console.print(f"[green]✅ EventBridge rule details retrieved successfully![/green]")
                return True
            else:
                console.print(f"[red]❌ EventBridge rule details retrieval failed with return code: {result.returncode}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]Error showing EventBridge rule details: {e}[/red]")
            return False

    def _create_amplify_app(self, parameters: Dict[str, Any]) -> bool:
        """Create Amplify app."""
        try:
            cmd = ["devops-ai", "amplify", "create-app"]
            
            if "app_name" in parameters:
                cmd.extend(["--name", str(parameters["app_name"])])
            
            if "repository" in parameters:
                cmd.extend(["--repo", str(parameters["repository"])])
            
            if "branch" in parameters:
                cmd.extend(["--branch", str(parameters["branch"])])
            
            if "region" in parameters:
                cmd.extend(["--region", str(parameters["region"])])
            
            console.print(f"[blue]Executing: {' '.join(cmd)}[/blue]")
            
            # Execute the command directly in the terminal
            result = subprocess.run(cmd, check=False)
            
            if result.returncode == 0:
                console.print(f"[green]✅ Amplify app created successfully![/green]")
                return True
            else:
                console.print(f"[red]❌ Amplify app creation failed with return code: {result.returncode}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]Error creating Amplify app: {e}[/red]")
            return False

    def _deploy_amplify_branch(self, parameters: Dict[str, Any]) -> bool:
        """Deploy Amplify branch."""
        try:
            cmd = ["devops-ai", "amplify", "deploy-branch"]
            
            if "branch" in parameters:
                cmd.extend(["--branch", str(parameters["branch"])])
            
            if "app_id" in parameters:
                cmd.extend(["--app-id", str(parameters["app_id"])])
            
            if "region" in parameters:
                cmd.extend(["--region", str(parameters["region"])])
            
            if "wait" in parameters:
                if parameters["wait"]:
                    cmd.append("--wait")
            
            console.print(f"[blue]Executing: {' '.join(cmd)}[/blue]")
            
            # Execute the command directly in the terminal
            result = subprocess.run(cmd, check=False)
            
            if result.returncode == 0:
                console.print(f"[green]✅ Amplify branch deployed successfully![/green]")
                return True
            else:
                console.print(f"[red]❌ Amplify branch deployment failed with return code: {result.returncode}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]Error deploying Amplify branch: {e}[/red]")
            return False

    def _configure_amplify_app(self, parameters: Dict[str, Any]) -> bool:
        """Configure Amplify app."""
        try:
            cmd = ["devops-ai", "amplify", "configure-app"]
            
            if "app_id" in parameters:
                cmd.extend(["--app-id", str(parameters["app_id"])])
            
            if "region" in parameters:
                cmd.extend(["--region", str(parameters["region"])])
            
            if "framework" in parameters:
                cmd.extend(["--framework", str(parameters["framework"])])
            
            if "force" in parameters and parameters["force"]:
                cmd.append("--force")
            
            console.print(f"[blue]Executing: {' '.join(cmd)}[/blue]")
            
            # Execute the command directly in the terminal
            result = subprocess.run(cmd, check=False)
            
            if result.returncode == 0:
                console.print(f"[green]✅ Amplify app configured successfully![/green]")
                return True
            else:
                console.print(f"[red]❌ Amplify app configuration failed with return code: {result.returncode}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]Error configuring Amplify app: {e}[/red]")
            return False

    def _list_amplify_apps(self, parameters: Dict[str, Any]) -> bool:
        """List Amplify apps."""
        try:
            cmd = ["devops-ai", "amplify", "list-apps"]
            
            if "region" in parameters:
                cmd.extend(["--region", str(parameters["region"])])
            
            console.print(f"[blue]Executing: {' '.join(cmd)}[/blue]")
            
            # Execute the command directly in the terminal
            result = subprocess.run(cmd, check=False)
            
            if result.returncode == 0:
                console.print(f"[green]✅ Amplify apps listed successfully![/green]")
                return True
            else:
                console.print(f"[red]❌ Listing Amplify apps failed with return code: {result.returncode}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]Error listing Amplify apps: {e}[/red]")
            return False

    def _list_amplify_branches(self, parameters: Dict[str, Any]) -> bool:
        """List Amplify branches."""
        try:
            cmd = ["devops-ai", "amplify", "list-branches"]
            
            if "app_id" in parameters:
                cmd.extend(["--app-id", str(parameters["app_id"])])
            
            if "region" in parameters:
                cmd.extend(["--region", str(parameters["region"])])
            
            console.print(f"[blue]Executing: {' '.join(cmd)}[/blue]")
            
            # Execute the command directly in the terminal
            result = subprocess.run(cmd, check=False)
            
            if result.returncode == 0:
                console.print(f"[green]✅ Amplify branches listed successfully![/green]")
                return True
            else:
                console.print(f"[red]❌ Listing Amplify branches failed with return code: {result.returncode}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]Error listing Amplify branches: {e}[/red]")
            return False

    def _create_amplify_branch(self, parameters: Dict[str, Any]) -> bool:
        """Create Amplify branch."""
        try:
            cmd = ["devops-ai", "amplify", "create-branch"]
            
            if "branch" in parameters:
                cmd.extend(["--branch", str(parameters["branch"])])
            
            if "app_id" in parameters:
                cmd.extend(["--app-id", str(parameters["app_id"])])
            
            if "region" in parameters:
                cmd.extend(["--region", str(parameters["region"])])
            
            if "enable_auto_build" in parameters:
                if parameters["enable_auto_build"]:
                    cmd.append("--auto-build")
            
            if "enable_pull_request_preview" in parameters:
                if parameters["enable_pull_request_preview"]:
                    cmd.append("--pr-preview")
            
            console.print(f"[blue]Executing: {' '.join(cmd)}[/blue]")
            
            # Execute the command directly in the terminal
            result = subprocess.run(cmd, check=False)
            
            if result.returncode == 0:
                console.print(f"[green]✅ Amplify branch created successfully![/green]")
                return True
            else:
                console.print(f"[red]❌ Amplify branch creation failed with return code: {result.returncode}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]Error creating Amplify branch: {e}[/red]")
            return False

    def _delete_amplify_app(self, parameters: Dict[str, Any]) -> bool:
        """Delete Amplify app."""
        try:
            cmd = ["devops-ai", "amplify", "delete-app"]
            
            if "app_id" in parameters:
                cmd.extend(["--app-id", str(parameters["app_id"])])
            
            if "region" in parameters:
                cmd.extend(["--region", str(parameters["region"])])
            
            if "force" in parameters and parameters["force"]:
                cmd.append("--force")
            
            console.print(f"[blue]Executing: {' '.join(cmd)}[/blue]")
            
            # Execute the command directly in the terminal
            result = subprocess.run(cmd, check=False)
            
            if result.returncode == 0:
                console.print(f"[green]✅ Amplify app deleted successfully![/green]")
                return True
            else:
                console.print(f"[red]❌ Amplify app deletion failed with return code: {result.returncode}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]Error deleting Amplify app: {e}[/red]")
            return False

    def _delete_amplify_branch(self, parameters: Dict[str, Any]) -> bool:
        """Delete Amplify branch."""
        try:
            cmd = ["devops-ai", "amplify", "delete-branch"]
            
            if "branch" in parameters:
                cmd.extend(["--branch", str(parameters["branch"])])
            
            if "app_id" in parameters:
                cmd.extend(["--app-id", str(parameters["app_id"])])
            
            if "region" in parameters:
                cmd.extend(["--region", str(parameters["region"])])
            
            if "force" in parameters and parameters["force"]:
                cmd.append("--force")
            
            console.print(f"[blue]Executing: {' '.join(cmd)}[/blue]")
            
            # Execute the command directly in the terminal
            result = subprocess.run(cmd, check=False)
            
            if result.returncode == 0:
                console.print(f"[green]✅ Amplify branch deleted successfully![/green]")
                return True
            else:
                console.print(f"[red]❌ Amplify branch deletion failed with return code: {result.returncode}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]Error deleting Amplify branch: {e}[/red]")
            return False

    def _amplify_status(self, parameters: Dict[str, Any]) -> bool:
        """Show Amplify app status."""
        try:
            cmd = ["devops-ai", "amplify", "status"]
            
            if "app_id" in parameters:
                cmd.extend(["--app-id", str(parameters["app_id"])])
            
            if "region" in parameters:
                cmd.extend(["--region", str(parameters["region"])])
            
            console.print(f"[blue]Executing: {' '.join(cmd)}[/blue]")
            
            # Execute the command directly in the terminal
            result = subprocess.run(cmd, check=False)
            
            if result.returncode == 0:
                console.print(f"[green]✅ Amplify status retrieved successfully![/green]")
                return True
            else:
                console.print(f"[red]❌ Amplify status retrieval failed with return code: {result.returncode}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]Error getting Amplify status: {e}[/red]")
            return False

def create_agent_app():
    """Create the Typer app for the AI agent."""
    app = typer.Typer(
        name="devops-ai-agent",
        help="AI-powered DevOps assistant - Convert natural language to DevOps commands",
        add_completion=False,
    )
    
    @app.command()
    def chat(
        openai_api_key: Optional[str] = typer.Option(None, "--api-key", "-k", help="OpenAI API key"),
        interactive: bool = typer.Option(True, "--interactive", "-i", help="Run in interactive mode"),
    ):
        """Start the AI agent in chat mode."""
        try:
            # Load .env file if it exists
            if os.path.exists(".env"):
                console.print("[green]✅ Loaded configuration from .env file[/green]")
            else:
                console.print("[yellow]⚠️  No .env file found. Using environment variables.[/yellow]")
            
            agent = DevOpsAIAgent(openai_api_key)
            
            if interactive:
                console.print(Panel(
                    "[bold blue]DevOps AI Agent[/bold blue]\n\n"
                    "I can help you with DevOps tasks using natural language!\n\n"
                    "Examples:\n"
                    "• 'deploy this flask app on aws lambda with memory as 1 GB and timeout as 300 seconds'\n"
                    "• 'create a github actions workflow for my flask app'\n"
                    "• 'check the status of my deployment'\n"
                    "• 'view logs from my lambda function'\n"
                    "• 'delete my deployment'\n"
                    "• 'create an eventbridge rule called backup-rule that runs daily at 2am'\n"
                    "• 'create an eventbridge rule called backup-rule that runs daily at 9am indian time'\n"
                    "• 'list all eventbridge rules'\n"
                    "• 'delete the eventbridge rule called backup-rule'\n"
                    "• 'update my eventbridge rule to run every 6 hours'\n"
                    "• 'deploy this react app to amplify with repository https://github.com/username/my-react-app'\n"
                    "• 'deploy the main branch to amplify and wait for completion'\n"
                    "• 'configure my amplify app for nextjs framework'\n"
                    "• 'list all amplify apps'\n"
                    "• 'create a feature branch called new-ui for my amplify app'\n"
                    "• 'check the status of my amplify app'\n\n"
                    "Note: Complex natural language descriptions will use OpenAI for enhanced cron expression generation.\n"
                    "Type 'quit' or 'exit' to stop.",
                    title="🚀 Welcome",
                    border_style="blue"
                ))
                
                while True:
                    query = Prompt.ask("\n[bold cyan]What would you like me to do?[/bold cyan]")
                    
                    if query.lower() in ['quit', 'exit', 'q']:
                        console.print("[yellow]Goodbye! 👋[/yellow]")
                        break
                    
                    if not query.strip():
                        continue
                    
                    # Parse the query
                    console.print("[blue]🤖 Analyzing your request...[/blue]")
                    parsed = agent.parse_query(query)
                    
                    # Display what we understood
                    if parsed.get("confidence", 0) > 0.5:
                        console.print(f"[green]✅ Understood: {parsed['command']}[/green]")
                        
                        # Show parameters
                        if parsed.get("parameters"):
                            table = Table(title="Parameters")
                            table.add_column("Parameter", style="cyan")
                            table.add_column("Value", style="green")
                            
                            for key, value in parsed["parameters"].items():
                                table.add_row(key, str(value))
                            
                            console.print(table)
                        
                        # Execute the command
                        console.print("[blue]🚀 Executing command...[/blue]")
                        success = agent.execute_command(parsed["command"], parsed["parameters"])
                        
                        if success:
                            console.print("[green]✅ Task completed successfully![/green]")
                        else:
                            console.print("[red]❌ Task failed. Check the output above for details.[/red]")
                    else:
                        console.print(f"[yellow]⚠️  Low confidence in understanding. Raw response: {parsed.get('raw_response', 'No response')}[/yellow]")
                        
            else:
                # Non-interactive mode - take query from command line
                query = typer.get_text("Enter your DevOps query")
                if query:
                    agent = DevOpsAIAgent(openai_api_key)
                    parsed = agent.parse_query(query)
                    success = agent.execute_command(parsed["command"], parsed["parameters"])
                    raise typer.Exit(0 if success else 1)
                    
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)
    
    @app.command()
    def test(
        query: str = typer.Argument(..., help="Test query to parse"),
        openai_api_key: Optional[str] = typer.Option(None, "--api-key", "-k", help="OpenAI API key"),
    ):
        """Test the AI agent with a specific query."""
        try:
            # Load .env file if it exists
            if os.path.exists(".env"):
                console.print("[green]✅ Loaded configuration from .env file[/green]")
            else:
                console.print("[yellow]⚠️  No .env file found. Using environment variables.[/yellow]")
            
            agent = DevOpsAIAgent(openai_api_key)
            
            console.print(f"[blue]Testing query: {query}[/blue]")
            
            parsed = agent.parse_query(query)
            
            # Display results
            table = Table(title="Parsed Results")
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Command", parsed.get("command", "unknown"))
            table.add_row("Confidence", str(parsed.get("confidence", 0)))
            
            if parsed.get("parameters"):
                for key, value in parsed["parameters"].items():
                    table.add_row(f"Parameter: {key}", str(value))
            
            console.print(table)
            
            if parsed.get("confidence", 0) > 0.5:
                console.print("[green]✅ Query parsed successfully![/green]")
            else:
                console.print("[yellow]⚠️  Low confidence in parsing.[/yellow]")
                
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)
    
    return app

# Create the app instance
app = create_agent_app()

if __name__ == "__main__":
    print("Starting DevOps AI Agent...")
    app() 