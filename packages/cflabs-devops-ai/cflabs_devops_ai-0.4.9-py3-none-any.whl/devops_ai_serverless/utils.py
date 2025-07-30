"""Utility functions for devops-ai."""

import os
import yaml
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import boto3
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def get_project_root() -> Path:
    """Get the current project root directory."""
    return Path.cwd()


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    if config_path is None:
        config_path = get_project_root() / "cflabs-config.yaml"
    
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)


def save_config(config: Dict[str, Any], config_path: Optional[str] = None) -> None:
    """Save configuration to YAML file."""
    if config_path is None:
        config_path = get_project_root() / "cflabs-config.yaml"
    
    config_file = Path(config_path)
    with open(config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def detect_flask_app() -> tuple[str, str]:
    """Detect Flask app module and object from current directory."""
    app_py = get_project_root() / "app.py"
    if not app_py.exists():
        raise FileNotFoundError("app.py not found in current directory")
    
    # Default to app:app
    return "app", "app"


def run_command(cmd: List[str], cwd: Optional[Path] = None, check: bool = True, input_text: Optional[str] = None, timeout: Optional[int] = None, capture_output: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command with proper error handling."""
    try:
        kwargs = {
            'cwd': cwd,
            'check': check,
            'capture_output': capture_output,
            'text': True
        }
        
        if input_text:
            kwargs['input'] = input_text
        
        if timeout:
            kwargs['timeout'] = timeout
        
        result = subprocess.run(cmd, **kwargs)
        return result
    except subprocess.TimeoutExpired as e:
        console.print(f"[red]Command timed out after {timeout} seconds: {' '.join(cmd)}[/red]")
        raise
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Command failed: {' '.join(cmd)}[/red]")
        console.print(f"[red]Error: {e.stderr}[/red]")
        raise


def get_sam_logs(stack_name: str, region: str, function_name: Optional[str] = None) -> str:
    """Get SAM logs with better error handling."""
    try:
        if function_name:
            cmd = ["sam", "logs", "--stack-name", stack_name, "--region", region, "--name", function_name]
        else:
            cmd = ["sam", "logs", "--stack-name", stack_name, "--region", region]
        
        result = run_command(cmd, timeout=60)
        return result.stdout
    except Exception as e:
        return f"Failed to get SAM logs: {e}"


def get_cloudwatch_logs(stack_name: str, region: str) -> str:
    """Get CloudWatch logs directly using AWS CLI."""
    try:
        # Get the log group name from CloudFormation stack
        cloudformation = boto3.client('cloudformation', region_name=region)
        response = cloudformation.describe_stacks(StackName=stack_name)
        
        # Look for Lambda function in stack outputs
        for output in response['Stacks'][0].get('Outputs', []):
            if 'Function' in output['OutputKey']:
                function_name = output['OutputValue'].split('/')[-1]
                log_group = f"/aws/lambda/{function_name}"
                
                # Get recent log events
                logs = boto3.client('logs', region_name=region)
                response = logs.describe_log_streams(
                    logGroupName=log_group,
                    orderBy='LastEventTime',
                    descending=True,
                    maxItems=5
                )
                
                log_events = []
                for stream in response['logStreams']:
                    events = logs.get_log_events(
                        logGroupName=log_group,
                        logStreamName=stream['logStreamName'],
                        limit=50
                    )
                    log_events.extend(events['events'])
                
                # Sort by timestamp
                log_events.sort(key=lambda x: x['timestamp'])
                
                return "\n".join([f"{event['timestamp']}: {event['message']}" for event in log_events])
        
        return "No Lambda function found in stack outputs"
        
    except Exception as e:
        return f"Failed to get CloudWatch logs: {e}"


def get_deployment_status(stack_name: str, region: str) -> dict:
    """Get detailed deployment status from CloudFormation."""
    try:
        cloudformation = boto3.client('cloudformation', region_name=region)
        response = cloudformation.describe_stacks(StackName=stack_name)
        stack = response['Stacks'][0]
        
        # Get stack events
        events_response = cloudformation.describe_stack_events(StackName=stack_name)
        recent_events = events_response['StackEvents'][:10]  # Last 10 events
        
        return {
            'stack_status': stack['StackStatus'],
            'stack_status_reason': stack.get('StackStatusReason', ''),
            'recent_events': recent_events,
            'outputs': stack.get('Outputs', [])
        }
    except Exception as e:
        return {'error': str(e)}


def check_prerequisites() -> bool:
    """Check if all prerequisites are installed."""
    missing = []
    
    # Check AWS CLI
    try:
        run_command(["aws", "--version"], check=False)
    except FileNotFoundError:
        missing.append("AWS CLI")
    
    # Check SAM CLI
    try:
        run_command(["sam", "--version"], check=False)
    except FileNotFoundError:
        missing.append("AWS SAM CLI")
    
    # Check Docker
    try:
        run_command(["docker", "--version"], check=False)
    except FileNotFoundError:
        missing.append("Docker")
    
    if missing:
        console.print(Panel(
            f"[red]Missing prerequisites: {', '.join(missing)}[/red]\n\n"
            "Please install the missing tools:\n"
            "- AWS CLI: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html\n"
            "- AWS SAM CLI: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html\n"
            "- Docker: https://docs.docker.com/get-docker/",
            title="Prerequisites Check Failed"
        ))
        return False
    
    return True


def check_sam_configuration() -> bool:
    """Check if SAM is properly configured."""
    try:
        # Check if SAM can list applications
        result = run_command(["sam", "list", "applications"], check=False, timeout=30)
        if result.returncode == 0:
            return True
        else:
            return True  # Don't fail, just warn
    except Exception as e:
        console.print(f"[yellow]SAM configuration check failed: {e}[/yellow]")
        return True  # Don't fail, just warn


def check_aws_permissions() -> bool:
    """Check if AWS user has necessary permissions."""
    try:
        # Test basic AWS access
        sts = boto3.client('sts')
        sts.get_caller_identity()
        
        # Test ECR access
        ecr = boto3.client('ecr')
        ecr.describe_repositories(maxResults=1)
        
        return True
    except Exception as e:
        console.print(Panel(
            f"[red]AWS permissions check failed: {e}[/red]\n\n"
            "Please ensure your AWS user has the following permissions:\n"
            "• sts:GetCallerIdentity\n"
            "• ecr:CreateRepository\n"
            "• ecr:DescribeRepositories\n"
            "• ecr:GetAuthorizationToken\n"
            "• ecr:BatchCheckLayerAvailability\n"
            "• ecr:GetDownloadUrlForLayer\n"
            "• ecr:BatchGetImage\n"
            "• ecr:InitiateLayerUpload\n"
            "• ecr:UploadLayerPart\n"
            "• ecr:CompleteLayerUpload\n"
            "• ecr:PutImage\n"
            "• cloudformation:*\n"
            "• lambda:*\n"
            "• apigateway:*\n"
            "• logs:*\n\n"
            "You can attach the AWS managed policy 'AdministratorAccess' for testing, "
            "or create a custom policy with the minimum required permissions.",
            title="AWS Permissions Check Failed"
        ))
        return False


def get_aws_account_id() -> str:
    """Get the current AWS account ID."""
    try:
        sts = boto3.client('sts')
        response = sts.get_caller_identity()
        return response['Account']
    except sts.exceptions.AccessDeniedException as e:
        console.print(f"[red]Access denied to STS. Please ensure your AWS user has sts:GetCallerIdentity permission.[/red]")
        raise
    except Exception as e:
        console.print(f"[red]Failed to get AWS account ID: {e}[/red]")
        raise


def get_ecr_repository_name(stack_name: str) -> str:
    """Generate ECR repository name from stack name."""
    return f"{stack_name}-repo"


def create_ecr_repository(repo_name: str, region: str) -> str:
    """Create ECR repository and return the repository URI."""
    try:
        ecr = boto3.client('ecr', region_name=region)
        
        # Check if repository already exists
        try:
            response = ecr.describe_repositories(repositoryNames=[repo_name])
            return response['repositories'][0]['repositoryUri']
        except ecr.exceptions.RepositoryNotFoundException:
            pass
        except ecr.exceptions.AccessDeniedException:
            console.print(f"[yellow]Warning: No permission to check ECR repositories. Assuming {repo_name} doesn't exist.[/yellow]")
        
        # Create repository
        try:
            response = ecr.create_repository(
                repositoryName=repo_name,
                imageScanningConfiguration={
                    'scanOnPush': True
                }
            )
            return response['repository']['repositoryUri']
        except ecr.exceptions.RepositoryAlreadyExistsException:
            # Repository was created by another process
            response = ecr.describe_repositories(repositoryNames=[repo_name])
            return response['repositories'][0]['repositoryUri']
            
    except ecr.exceptions.AccessDeniedException as e:
        console.print(f"[red]Access denied to ECR. Please ensure your AWS user has the following permissions:[/red]")
        console.print(f"[red]  - ecr:CreateRepository[/red]")
        console.print(f"[red]  - ecr:DescribeRepositories[/red]")
        console.print(f"[red]  - ecr:GetAuthorizationToken[/red]")
        console.print(f"[red]  - ecr:BatchCheckLayerAvailability[/red]")
        console.print(f"[red]  - ecr:GetDownloadUrlForLayer[/red]")
        console.print(f"[red]  - ecr:BatchGetImage[/red]")
        console.print(f"[red]  - ecr:InitiateLayerUpload[/red]")
        console.print(f"[red]  - ecr:UploadLayerPart[/red]")
        console.print(f"[red]  - ecr:CompleteLayerUpload[/red]")
        console.print(f"[red]  - ecr:PutImage[/red]")
        raise
    except Exception as e:
        console.print(f"[red]Failed to create ECR repository: {e}[/red]")
        raise


def delete_ecr_repository(repo_name: str, region: str) -> None:
    """Delete ECR repository and all images."""
    try:
        ecr = boto3.client('ecr', region_name=region)
        
        # Delete all images first
        try:
            images = ecr.list_images(repositoryName=repo_name)
            if images['imageIds']:
                ecr.batch_delete_image(
                    repositoryName=repo_name,
                    imageIds=images['imageIds']
                )
        except ecr.exceptions.RepositoryNotFoundException:
            pass
        
        # Delete repository
        ecr.delete_repository(repositoryName=repo_name)
        console.print(f"[green]Deleted ECR repository: {repo_name}[/green]")
    except Exception as e:
        console.print(f"[yellow]Warning: Failed to delete ECR repository: {e}[/yellow]")


def get_stack_outputs(stack_name: str, region: str) -> Dict[str, str]:
    """Get CloudFormation stack outputs."""
    try:
        cloudformation = boto3.client('cloudformation', region_name=region)
        response = cloudformation.describe_stacks(StackName=stack_name)
        
        outputs = {}
        for output in response['Stacks'][0]['Outputs']:
            outputs[output['OutputKey']] = output['OutputValue']
        
        return outputs
    except Exception as e:
        console.print(f"[red]Failed to get stack outputs: {e}[/red]")
        return {}


def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable string."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m {seconds % 60}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[green]✓ {message}[/green]")


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[red]✗ {message}[/red]")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[yellow]⚠ {message}[/yellow]")


def print_info(message: str) -> None:
    """Print an info message."""
    console.print(f"[blue]ℹ {message}[/blue]")


def load_env_variables(env_file: str = ".env") -> Dict[str, str]:
    """Load environment variables from .env file."""
    env_vars = {}
    env_path = get_project_root() / env_file
    
    if not env_path.exists():
        console.print(f"[yellow]⚠️  {env_file} file not found. No environment variables will be loaded.[/yellow]")
        return env_vars
    
    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse key=value format
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    
                    env_vars[key] = value
        
        if env_vars:
            console.print(f"[green]✅ Loaded {len(env_vars)} environment variables from {env_file}[/green]")
            if len(env_vars) <= 5:  # Show all if 5 or fewer
                for key, value in env_vars.items():
                    # Mask sensitive values
                    masked_value = value if not any(sensitive in key.lower() for sensitive in ['password', 'secret', 'key', 'token']) else '***'
                    console.print(f"[dim]  {key}={masked_value}[/dim]")
            else:
                console.print(f"[dim]  Showing first 5 variables...[/dim]")
                for i, (key, value) in enumerate(env_vars.items()):
                    if i >= 5:
                        break
                    masked_value = value if not any(sensitive in key.lower() for sensitive in ['password', 'secret', 'key', 'token']) else '***'
                    console.print(f"[dim]  {key}={masked_value}[/dim]")
                console.print(f"[dim]  ... and {len(env_vars) - 5} more[/dim]")
        else:
            console.print(f"[yellow]⚠️  No environment variables found in {env_file}[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Error reading {env_file}: {e}[/red]")
    
    return env_vars


def get_aws_error_guidance(error: Exception) -> str:
    """Get specific guidance for AWS errors."""
    error_str = str(error).lower()
    
    # Check for Docker daemon issues first
    if "cannot connect to the docker daemon" in error_str or "docker daemon" in error_str:
        import platform
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            return (
                "[red]Docker is not running[/red]\n\n"
                "Docker Desktop is not running on macOS. To fix this:\n\n"
                "1. [yellow]Start Docker Desktop[/yellow]:\n"
                "   • Open Docker Desktop from Applications\n"
                "   • Or run: [yellow]open -a Docker[/yellow]\n"
                "   • Wait for Docker to fully start (check the whale icon in menu bar)\n\n"
                "2. [yellow]Verify Docker is running[/yellow]:\n"
                "   • Run: [yellow]docker ps[/yellow]\n"
                "   • Should show empty list, not an error\n\n"
                "3. [yellow]If Docker Desktop is not installed[/yellow]:\n"
                "   • Download from: https://www.docker.com/products/docker-desktop\n"
                "   • Install and start Docker Desktop\n\n"
                "After starting Docker, try the command again."
            )
        elif system == "linux":
            return (
                "[red]Docker daemon is not running[/red]\n\n"
                "Docker daemon is not running on Linux. To fix this:\n\n"
                "1. [yellow]Start Docker daemon[/yellow]:\n"
                "   • Run: [yellow]sudo systemctl start docker[/yellow]\n"
                "   • Or run: [yellow]sudo service docker start[/yellow]\n\n"
                "2. [yellow]Enable Docker to start on boot[/yellow]:\n"
                "   • Run: [yellow]sudo systemctl enable docker[/yellow]\n\n"
                "3. [yellow]Add user to docker group[/yellow] (optional):\n"
                "   • Run: [yellow]sudo usermod -aG docker $USER[/yellow]\n"
                "   • Log out and back in for changes to take effect\n\n"
                "4. [yellow]Verify Docker is running[/yellow]:\n"
                "   • Run: [yellow]docker ps[/yellow]\n"
                "   • Should show empty list, not an error\n\n"
                "After starting Docker, try the command again."
            )
        elif system == "windows":
            return (
                "[red]Docker is not running[/red]\n\n"
                "Docker Desktop is not running on Windows. To fix this:\n\n"
                "1. [yellow]Start Docker Desktop[/yellow]:\n"
                "   • Open Docker Desktop from Start Menu\n"
                "   • Or run: [yellow]start docker[/yellow]\n"
                "   • Wait for Docker to fully start (check the whale icon in system tray)\n\n"
                "2. [yellow]Verify Docker is running[/yellow]:\n"
                "   • Run: [yellow]docker ps[/yellow]\n"
                "   • Should show empty list, not an error\n\n"
                "3. [yellow]If Docker Desktop is not installed[/yellow]:\n"
                "   • Download from: https://www.docker.com/products/docker-desktop\n"
                "   • Install and start Docker Desktop\n\n"
                "4. [yellow]WSL2 issues[/yellow] (if using WSL2):\n"
                "   • Ensure WSL2 is enabled: [yellow]wsl --set-default-version 2[/yellow]\n"
                "   • Restart Docker Desktop\n\n"
                "After starting Docker, try the command again."
            )
        else:
            return (
                "[red]Docker is not running[/red]\n\n"
                "Docker daemon is not running. To fix this:\n\n"
                "1. [yellow]Start Docker[/yellow]:\n"
                "   • Start Docker Desktop (macOS/Windows)\n"
                "   • Or start Docker daemon (Linux): [yellow]sudo systemctl start docker[/yellow]\n\n"
                "2. [yellow]Verify Docker is running[/yellow]:\n"
                "   • Run: [yellow]docker ps[/yellow]\n"
                "   • Should show empty list, not an error\n\n"
                "After starting Docker, try the command again."
            )
    
    if "accessdenied" in error_str or "unauthorized" in error_str:
        return (
            "[red]Access Denied Error[/red]\n\n"
            "This usually means insufficient AWS permissions. Try:\n"
                    "1. [yellow]devops-ai doctor[/yellow] - Check your setup\n"
        "2. [yellow]devops-ai troubleshoot[/yellow] - View troubleshooting guide\n"
            "3. Attach [yellow]AdministratorAccess[/yellow] policy to your AWS user\n"
            "4. Or create a custom policy with required permissions\n\n"
            "Required permissions: sts:GetCallerIdentity, ecr:*, cloudformation:*, lambda:*, apigateway:*, logs:*, iam:PassRole"
        )
    
    elif "nosuchbucket" in error_str:
        return (
            "[red]S3 Bucket Not Found[/red]\n\n"
            "This is usually handled automatically by SAM. Try:\n"
            "1. Ensure you have [yellow]s3:CreateBucket[/yellow] permission\n"
            "2. Check if the bucket name is already taken\n"
            "3. Try a different region: [yellow]--region us-east-1[/yellow]"
        )
    
    elif "repositoryalreadyexists" in error_str:
        return (
            "[yellow]Repository Already Exists[/yellow]\n\n"
            "This is normal - the ECR repository was already created.\n"
            "The deployment will continue normally."
        )
    
    elif "imagenotfound" in error_str:
        return (
            "[red]Docker Image Not Found[/red]\n\n"
            "The container image hasn't been built yet. Try:\n"
            "1. [yellow]devops-ai build[/yellow] - Build the container first\n"
            "2. Check if Docker is running: [yellow]docker ps[/yellow]"
        )
    
    elif "credentials" in error_str or "authentication" in error_str:
        return (
            "[red]AWS Credentials Error[/red]\n\n"
            "Your AWS credentials are not configured or invalid. Try:\n"
            "1. [yellow]aws configure[/yellow] - Set up credentials\n"
            "2. [yellow]aws sts get-caller-identity[/yellow] - Test credentials\n"
            "3. Check your AWS Access Key and Secret Key\n"
            "4. Ensure your credentials haven't expired"
        )
    
    elif "network" in error_str or "timeout" in error_str:
        return (
            "[red]Network/Timeout Error[/red]\n\n"
            "Network connectivity issues. Try:\n"
            "1. Check your internet connection\n"
            "2. Disable VPN if using one\n"
            "3. Check corporate firewall settings\n"
            "4. Try again in a few minutes"
        )
    
    elif "unexpected keyword argument" in error_str:
        return (
            "[red]Internal Error[/red]\n\n"
            "This appears to be an internal library error. Try:\n"
            "1. Update the library: [yellow]pip install --upgrade devops-ai[/yellow]\n"
            "2. Check if you're using the latest version\n"
            "3. Open an issue on GitHub with the error details"
        )
    
    else:
        return (
            "[red]Unexpected Error[/red]\n\n"
            "An unexpected error occurred. Try:\n"
                    "1. [yellow]devops-ai doctor[/yellow] - Run diagnostics\n"
        "2. [yellow]devops-ai troubleshoot[/yellow] - View troubleshooting guide\n"
            "3. Check the full error message above\n"
            "4. Open an issue on GitHub with error details"
        ) 

def get_env_vars(env_vars):
    """
    Input: comma separated key=value pairs
    Output: list of ParameterKey=ParameterValue pairs
    """
    parameter_overrides = []
    # Parse command line environment variables if provided
    if env_vars:
        console.print("[blue]📝 Adding command line environment variables...[/blue]")
        for pair in env_vars.split(','):
            pair = pair.strip()
            if '=' in pair:
                # Key=value format
                key, value = pair.split('=', 1)
                key = key.strip()
                value = value.strip()
                # Escape any special characters in the value
                escaped_value = value.replace('"', '\\"').replace("'", "\\'")
                parameter_overrides.append(f'ParameterKey={key},ParameterValue={escaped_value}')
                console.print(f"  • {key}={escaped_value[:20]}{'...' if len(escaped_value) > 20 else ''}")
            else:
                # Only key provided - try to get value from environment variables
                key = pair
                value = os.environ.get(key)
                if value:
                    escaped_value = value.replace('"', '\\"').replace("'", "\\'")
                    parameter_overrides.append(f'ParameterKey={key},ParameterValue={escaped_value}')
                    console.print(f"  • {key}=*** (from environment)")
                else:
                    console.print(f"  ⚠️  Warning: Key '{key}' not found in environment variables")
    return parameter_overrides