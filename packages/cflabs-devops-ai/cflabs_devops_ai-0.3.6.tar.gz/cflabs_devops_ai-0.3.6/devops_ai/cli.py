"""Unified CLI interface for devops-ai - combining all modules."""

import os
import typer
import subprocess
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from datetime import datetime

# Import all module CLIs
from devops_ai_serverless import utils
from devops_ai_serverless import templates
from devops_ai_eventbridge.cli import app as eventbridge_app
from devops_ai_github_actions.cli import app as github_actions_app
from devops_ai_amplify.cli import app as amplify_app
from devops_ai_agent.agent import DevOpsAIAgent

app = typer.Typer(
    name="devops-ai",
    help="Unified DevOps AI - Deploy Flask apps to AWS Lambda, React apps to Amplify, manage EventBridge rules, and GitHub Actions with AI-powered interface",
    add_completion=False,
)
console = Console()


# ============================================================================
# SERVERLESS MODULE COMMANDS
# ============================================================================

@app.command()
def deploy(
    lambda_name: str = typer.Option(None, "--name", "-n", help="Name for your Lambda function"),
    region: str = typer.Option(None, "--region", "-r", help="AWS region"),
    port: int = typer.Option(8000, "--port", "-p", help="Application port"),
    memory_size: int = typer.Option(512, "--memory", help="Lambda memory size (MB)"),
    timeout: int = typer.Option(30, "--timeout", "-t", help="Lambda timeout (seconds)"),
    image_tag: str = typer.Option(None, "--image-tag", "-i", help="Docker image tag to use for deployment"),
    config_path: Optional[str] = typer.Option(None, "--config", "-c", help="Path to config file"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug mode with verbose output"),
):
    """Deploy Flask app to AWS Lambda + API Gateway (alias for serverless deploy)."""
    return serverless_deploy(
        lambda_name=lambda_name,
        region=region,
        port=port,
        memory_size=memory_size,
        timeout=timeout,
        image_tag=image_tag,
        config_path=config_path,
        debug=debug
    )

@app.command()
def serverless_deploy(
    lambda_name: str = typer.Option(None, "--name", "-n", help="Name for your Lambda function"),
    region: str = typer.Option(None, "--region", "-r", help="AWS region"),
    port: int = typer.Option(8000, "--port", "-p", help="Application port"),
    memory_size: int = typer.Option(512, "--memory", help="Lambda memory size (MB)"),
    timeout: int = typer.Option(30, "--timeout", "-t", help="Lambda timeout (seconds)"),
    image_tag: str = typer.Option(None, "--image-tag", "-i", help="Docker image tag to use for deployment"),
    config_path: Optional[str] = typer.Option(None, "--config", "-c", help="Path to config file"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug mode with verbose output"),
):
    """Deploy Flask app to AWS Lambda + API Gateway."""
    try:
        if not image_tag:
            image_tag = datetime.now().strftime("%Y%m%d%H%M%S")
        
        project_root = utils.get_project_root()
        
        # Check prerequisites
        if not utils.check_prerequisites():
            raise typer.Exit(1)
        
        # Get or prompt for lambda name
        if lambda_name is None:
            lambda_name = Prompt.ask(
                "Enter a name for your Lambda function",
                default=f"{project_root.name}-flask-app"
            )
        
        # Use default region if not provided
        if region is None:
            region = "ap-south-1"
        
        # Detect Flask app
        try:
            app_module, app_object = utils.detect_flask_app()
        except FileNotFoundError:
            utils.print_error("app.py not found in current directory")
            raise typer.Exit(1)
        
        # Generate stack name from lambda name
        stack_name = f"{lambda_name}-stack"
        
        # Create configuration
        config = {
            "app": {
                "module": app_module,
                "object": app_object,
                "port": port
            },
            "deployment": {
                "stack_name": stack_name,
                "lambda_name": lambda_name,
                "region": region,
                "memory_size": memory_size,
                "timeout": timeout
            },
            "container": {
                "base_image": "public.ecr.aws/lambda/python:3.12",
                "working_dir": "/var/task"
            }
        }
        
        # Save config for future use
        utils.save_config(config, config_path)
        
        console.print("[blue]🚀 Deploying Flask app to AWS Lambda...[/blue]")
        
        # Generate deployment files
        console.print("[blue]📝 Generating deployment files...[/blue]")
        
        # Generate Dockerfile
        dockerfile_content = templates.DOCKERFILE_TEMPLATE.render(
            base_image=config["container"]["base_image"],
            working_dir=config["container"]["working_dir"],
            port=config["app"]["port"],
            app_module=config["app"]["module"],
            app_object=config["app"]["object"]
        )
        
        dockerfile_path = project_root / "Dockerfile"
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
        console.print(f"[green]✅ Generated: {dockerfile_path}[/green]")

        # Generate lambda_entry.py wrapper for Lambda
        lambda_entry_content = templates.LAMBDA_ENTRY_TEMPLATE.render(
            app_module=config["app"]["module"],
            app_object=config["app"]["object"]
        )
        lambda_entry_path = project_root / "lambda_entry.py"
        with open(lambda_entry_path, 'w') as f:
            f.write(lambda_entry_content)
        console.print(f"[green]✅ Generated: {lambda_entry_path}[/green]")
        
        # Load environment variables from .env file
        env_vars = utils.load_env_variables()
        # Generate SAM template
        sam_content = templates.SAM_TEMPLATE.render(
            timeout=config["deployment"]["timeout"],
            memory_size=config["deployment"]["memory_size"],
            port=config["app"]["port"],
            env_vars=env_vars
        )
        
        sam_path = project_root / "template.yml"
        with open(sam_path, 'w') as f:
            f.write(sam_content)
        console.print(f"[green]✅ Generated: {sam_path}[/green]")
        
        # Generate requirements.txt if it doesn't exist
        requirements_path = project_root / "requirements.txt"
        if not requirements_path.exists():
            requirements_content = templates.REQUIREMENTS_TEMPLATE.render()
            with open(requirements_path, 'w') as f:
                f.write(requirements_content)
            console.print(f"[green]✅ Generated: {requirements_path}[/green]")
        
        # Generate .dockerignore if it doesn't exist
        dockerignore_path = project_root / ".dockerignore"
        if not dockerignore_path.exists():
            dockerignore_content = templates.DOCKERIGNORE_TEMPLATE.render()
            with open(dockerignore_path, 'w') as f:
                f.write(dockerignore_content)
            console.print(f"[green]✅ Generated: {dockerignore_path}[/green]")
        
        # Build and deploy
        console.print("[blue]🔨 Building Docker image...[/blue]")
        
        # Create ECR repository
        ecr_repo_name = f"{lambda_name}-repo"
        create_repo_cmd = [
            "aws", "ecr", "create-repository",
            "--repository-name", ecr_repo_name,
            "--region", region
        ]
        
        result = utils.run_command(create_repo_cmd, check=False)
        if result.returncode != 0 and "RepositoryAlreadyExistsException" not in result.stderr:
            utils.print_error(f"Failed to create ECR repository: {result.stderr}")
            raise typer.Exit(1)
        
        # Get ECR login token
        login_cmd = ["aws", "ecr", "get-login-password", "--region", region]
        result = utils.run_command(login_cmd, capture_output=True)
        if result.returncode != 0:
            utils.print_error(f"Failed to get ECR login token: {result.stderr}")
            raise typer.Exit(1)
        
        # Login to ECR
        docker_login_cmd = [
            "docker", "login", "--username", "AWS", "--password-stdin",
            f"{utils.get_aws_account_id()}.dkr.ecr.{region}.amazonaws.com"
        ]
        
        result = utils.run_command(docker_login_cmd, input_text=result.stdout, check=False)
        if result.returncode != 0:
            utils.print_error(f"Failed to login to ECR: {result.stderr}")
            raise typer.Exit(1)
        
        # Build Docker image
        image_uri = f"{utils.get_aws_account_id()}.dkr.ecr.{region}.amazonaws.com/{ecr_repo_name}:{image_tag}"
        build_cmd = [
                "docker", "buildx", "build", "--platform", "linux/amd64", "-t", image_uri, "."
            ]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Building Docker image...", total=None)
            result = utils.run_command(build_cmd, check=False)
            progress.update(task, completed=True)
        
        if result.returncode != 0:
            utils.print_error(f"Failed to build Docker image: {result.stderr}")
            raise typer.Exit(1)
        
        console.print("[green]✅ Docker image built successfully[/green]")
        
        # Push to ECR
        console.print("[blue]📤 Pushing to ECR...[/blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Pushing to ECR...", total=None)
            result = utils.run_command(["docker", "push", image_uri], check=False)
            progress.update(task, completed=True)
        
        if result.returncode != 0:
            utils.print_error(f"Failed to push to ECR: {result.stderr}")
            raise typer.Exit(1)
        
        console.print("[green]✅ Image pushed to ECR successfully[/green]")
        
        # Create S3 bucket for deployment artifacts
        console.print("[blue]📦 Creating S3 bucket for deployment artifacts...[/blue]")
        
        # Create S3 bucket name based on lambda name and region
        account_id = utils.get_aws_account_id()
        s3_bucket_name = f"{lambda_name}-deployment-{region}-{account_id}".lower().replace('_', '-')
        # Ensure bucket name is valid (3-63 characters, lowercase, no underscores)
        s3_bucket_name = ''.join(c for c in s3_bucket_name if c.isalnum() or c == '-')
        if len(s3_bucket_name) > 63:
            s3_bucket_name = s3_bucket_name[:63]
        if s3_bucket_name.endswith('-'):
            s3_bucket_name = s3_bucket_name[:-1]
        
        try:
            s3_client = utils.boto3.client('s3', region_name=region)
            s3_client.create_bucket(
                Bucket=s3_bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region} if region != 'us-east-1' else {}
            )
            console.print(f"[green]✅ Created S3 bucket: {s3_bucket_name}[/green]")
        except Exception as e:
            if "BucketAlreadyExists" in str(e) or "BucketAlreadyOwnedByYou" in str(e):
                console.print(f"[blue]ℹ️  S3 bucket {s3_bucket_name} already exists[/blue]")
            else:
                console.print(f"[yellow]⚠️  Could not create S3 bucket: {e}[/yellow]")
                console.print("[yellow]SAM will create one automatically with --resolve-s3[/yellow]")
                s3_bucket_name = None
        
        # Deploy with SAM
        console.print("[blue]🚀 Deploying to AWS Lambda...[/blue]")
        
        # Build parameter overrides including environment variables
        parameter_overrides = [f"ImageUri={image_uri}"]
        
        # Add environment variables as parameters
        env_vars = utils.load_env_variables()
        if env_vars:
            for key, value in env_vars.items():
                # Escape any special characters in the value
                escaped_value = value.replace('"', '\\"').replace("'", "\\'")
                parameter_overrides.append(f'{key}="{escaped_value}"')
        
        deploy_cmd = [
            "sam", "deploy",
            "--template-file", "template.yml",
            "--stack-name", stack_name,
            "--capabilities", "CAPABILITY_NAMED_IAM",
            "--region", region,
            "--no-confirm-changeset",
            "--no-fail-on-empty-changeset",
            "--parameter-overrides"
        ] + parameter_overrides + [
            "--image-repositories", 
            f"FlaskFunction={image_uri}",
            "--force-upload"
        ]
        
        # Add S3 bucket if we created one, otherwise use resolve-s3
        if s3_bucket_name:
            deploy_cmd.extend(["--s3-bucket", s3_bucket_name])
        else:
            deploy_cmd.append("--resolve-s3")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Deploying to AWS Lambda...", total=None)
            result = utils.run_command(deploy_cmd, check=False)
            progress.update(task, completed=True)
        
        if result.returncode != 0:
            utils.print_error(f"Failed to deploy to AWS Lambda: {result.stderr}")
            raise typer.Exit(1)
        
        # Get API Gateway URL
        describe_cmd = [
            "aws", "cloudformation", "describe-stacks",
            "--stack-name", stack_name,
            "--region", region,
            "--query", "Stacks[0].Outputs[?OutputKey=='FlaskApi'].OutputValue",
            "--output", "text"
        ]
        
        result = utils.run_command(describe_cmd, capture_output=True)
        if result.returncode == 0:
            api_url = result.stdout.strip()
            console.print(f"\n[bold green]🎉 Deployment successful![/bold green]")
            console.print(f"API Gateway URL: [blue]{api_url}[/blue]")
            console.print(f"Stack Name: [blue]{stack_name}[/blue]")
            console.print(f"Lambda Function: [blue]{lambda_name}[/blue]")
            console.print(f"Region: [blue]{region}[/blue]")
        else:
            console.print("[yellow]⚠️  Deployment completed but couldn't retrieve API URL[/yellow]")
        
    except Exception as e:
        utils.print_error(f"Deployment failed: {e}")
        raise typer.Exit(1)


@app.command()
def generate_files(
    lambda_name: str = typer.Option(None, "--name", "-n", help="Name for your Lambda function"),
    region: str = typer.Option("us-east-1", "--region", "-r", help="AWS region"),
    port: int = typer.Option(8000, "--port", "-p", help="Application port"),
    memory_size: int = typer.Option(512, "--memory", help="Lambda memory size (MB)"),
    timeout: int = typer.Option(30, "--timeout", "-t", help="Lambda timeout (seconds)"),
    image_tag: str = typer.Option(None, "--image-tag", "-i", help="Docker image tag to use for deployment"),
    config_path: Optional[str] = typer.Option(None, "--config", "-c", help="Path to config file"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files"),
):
    """Generate deployment files (Dockerfile, template.yml, etc.) without deploying."""
    try:
        if not image_tag:
            image_tag = datetime.now().strftime("%Y%m%d%H%M%S")
        
        project_root = utils.get_project_root()
        
        # Check prerequisites
        if not utils.check_prerequisites():
            raise typer.Exit(1)
        
        # Get or prompt for lambda name
        if lambda_name is None:
            lambda_name = Prompt.ask(
                "Enter a name for your Lambda function",
                default=f"{project_root.name}-flask-app"
            )
        
        # Use default region if not provided
        if region is None:
            region = "ap-south-1"
        
        # Detect Flask app
        try:
            app_module, app_object = utils.detect_flask_app()
        except FileNotFoundError:
            utils.print_error("app.py not found in current directory")
            raise typer.Exit(1)
        
        # Generate stack name from lambda name
        stack_name = f"{lambda_name}-stack"
        
        # Create configuration
        config = {
            "app": {
                "module": app_module,
                "object": app_object,
                "port": port
            },
            "deployment": {
                "stack_name": stack_name,
                "lambda_name": lambda_name,
                "region": region,
                "memory_size": memory_size,
                "timeout": timeout
            },
            "container": {
                "base_image": "public.ecr.aws/lambda/python:3.12",
                "working_dir": "/var/task"
            }
        }
        
        # Save config for future use
        utils.save_config(config, config_path)
        
        console.print("[blue]Generating deployment files...[/blue]")
        
        # Generate Dockerfile
        dockerfile_content = templates.DOCKERFILE_TEMPLATE.render(
            base_image=config["container"]["base_image"],
            working_dir=config["container"]["working_dir"],
            port=config["app"]["port"],
            app_module=config["app"]["module"],
            app_object=config["app"]["object"]
        )
        
        dockerfile_path = project_root / "Dockerfile"
        if dockerfile_path.exists() and not force:
            if not Confirm.ask("Dockerfile already exists. Overwrite?"):
                console.print("[yellow]Skipping Dockerfile generation.[/yellow]")
            else:
                with open(dockerfile_path, 'w') as f:
                    f.write(dockerfile_content)
                console.print(f"[green]✅ Generated: {dockerfile_path}[/green]")
        else:
            with open(dockerfile_path, 'w') as f:
                f.write(dockerfile_content)
            console.print(f"[green]✅ Generated: {dockerfile_path}[/green]")

        # Generate lambda_entry.py wrapper for Lambda
        lambda_entry_content = templates.LAMBDA_ENTRY_TEMPLATE.render(
            app_module=config["app"]["module"],
            app_object=config["app"]["object"]
        )
        lambda_entry_path = project_root / "lambda_entry.py"
        if lambda_entry_path.exists() and not force:
            if not Confirm.ask("lambda_entry.py already exists. Overwrite?"):
                console.print("[yellow]Skipping lambda_entry.py generation.[/yellow]")
            else:
                with open(lambda_entry_path, 'w') as f:
                    f.write(lambda_entry_content)
                console.print(f"[green]✅ Generated: {lambda_entry_path}[/green]")
        else:
            with open(lambda_entry_path, 'w') as f:
                f.write(lambda_entry_content)
            console.print(f"[green]✅ Generated: {lambda_entry_path}[/green]")
        
        # Load environment variables from .env file
        env_vars = utils.load_env_variables()
        # Generate SAM template
        sam_content = templates.SAM_TEMPLATE.render(
            timeout=config["deployment"]["timeout"],
            memory_size=config["deployment"]["memory_size"],
            port=config["app"]["port"],
            env_vars=env_vars
        )
        
        sam_path = project_root / "template.yml"
        if sam_path.exists() and not force:
            if not Confirm.ask("template.yml already exists. Overwrite?"):
                console.print("[yellow]Skipping template.yml generation.[/yellow]")
            else:
                with open(sam_path, 'w') as f:
                    f.write(sam_content)
                console.print(f"[green]✅ Generated: {sam_path}[/green]")
        else:
            with open(sam_path, 'w') as f:
                f.write(sam_content)
            console.print(f"[green]✅ Generated: {sam_path}[/green]")
        
        # Generate requirements.txt if it doesn't exist
        requirements_path = project_root / "requirements.txt"
        if not requirements_path.exists():
            requirements_content = templates.REQUIREMENTS_TEMPLATE.render()
            with open(requirements_path, 'w') as f:
                f.write(requirements_content)
            console.print(f"[green]✅ Generated: {requirements_path}[/green]")
        else:
            console.print(f"[blue]ℹ️  Using existing: {requirements_path}[/blue]")
        
        # Generate .dockerignore if it doesn't exist
        dockerignore_path = project_root / ".dockerignore"
        if not dockerignore_path.exists():
            dockerignore_content = templates.DOCKERIGNORE_TEMPLATE.render()
            with open(dockerignore_path, 'w') as f:
                f.write(dockerignore_content)
            console.print(f"[green]✅ Generated: {dockerignore_path}[/green]")
        else:
            console.print(f"[blue]ℹ️  Using existing: {dockerignore_path}[/blue]")
        
        console.print(f"\n[bold green]✅ All deployment files generated successfully![/bold green]")
        console.print(f"Files created:")
        console.print(f"  • Dockerfile")
        console.print(f"  • template.yml")
        console.print(f"  • lambda_entry.py")
        console.print(f"  • requirements.txt (if needed)")
        console.print(f"  • .dockerignore (if needed)")
        console.print(f"\nNext step: Run [yellow]devops-ai-unified deploy[/yellow] to deploy to AWS")
        
    except Exception as e:
        utils.print_error(f"Failed to generate files: {e}")
        raise typer.Exit(1)


@app.command()
def stream_logs(
    config_path: Optional[str] = typer.Option(None, "--config", "-c", help="Path to config file"),
    stack_name: Optional[str] = typer.Option(None, "--stack-name", "-s", help="Name of the CloudFormation stack"),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region"),
    function_name: Optional[str] = typer.Option(None, "--function", "-f", help="Specific Lambda function name"),
    follow: bool = typer.Option(False, "--follow", help="Follow logs in real-time"),
    lines: int = typer.Option(50, "--lines", "-n", help="Number of log lines to show")
):
    """Stream logs from your deployed function."""
    try:
        # Load config
        config = utils.load_config(config_path)
        if not config:
            raise typer.Exit(1)
        
        # Use config values or provided arguments
        stack_name = stack_name or config["deployment"]["stack_name"]
        region = region or config["deployment"]["region"]
        function_name = function_name or config["deployment"]["lambda_name"]
        
        console.print(f"[blue]📋 Streaming logs for {function_name}...[/blue]")
        
        # Get CloudWatch log group name
        log_group_name = f"/aws/lambda/{function_name}"
        
        # Stream logs
        log_cmd = [
            "aws", "logs", "tail", log_group_name,
            "--region", region,
            "--lines", str(lines)
        ]
        
        if follow:
            log_cmd.append("--follow")
        
        result = utils.run_command(log_cmd, check=False)
        if result.returncode != 0:
            utils.print_error(f"Failed to stream logs: {result.stderr}")
            raise typer.Exit(1)
        
        print(result.stdout)
        
    except Exception as e:
        utils.print_error(f"Failed to stream logs: {e}")
        raise typer.Exit(1)


@app.command()
def delete_deployment(
    config_path: Optional[str] = typer.Option(None, "--config", "-c", help="Path to config file"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Remove the deployed stack and clean up ECR."""
    try:
        # Load config
        config = utils.load_config(config_path)
        if not config:
            raise typer.Exit(1)
        
        stack_name = config["deployment"]["stack_name"]
        region = config["deployment"]["region"]
        lambda_name = config["deployment"]["lambda_name"]
        
        if not force:
            if not Confirm.ask(f"Are you sure you want to delete stack '{stack_name}'?"):
                console.print("[yellow]Deletion cancelled.[/yellow]")
                return
        
        console.print(f"[blue]🗑️  Deleting stack '{stack_name}'...[/blue]")
        
        # Delete CloudFormation stack
        delete_cmd = [
            "aws", "cloudformation", "delete-stack",
            "--stack-name", stack_name,
            "--region", region
        ]
        
        result = utils.run_command(delete_cmd, check=False)
        if result.returncode != 0:
            utils.print_error(f"Failed to delete stack: {result.stderr}")
            raise typer.Exit(1)
        
        console.print(f"[green]✅ Stack '{stack_name}' deleted successfully[/green]")
        
        # Clean up ECR repository
        ecr_repo_name = f"{lambda_name}-repo"
        console.print(f"[blue]🧹 Cleaning up ECR repository '{ecr_repo_name}'...[/blue]")
        
        # Delete all images in the repository
        list_images_cmd = [
            "aws", "ecr", "list-images",
            "--repository-name", ecr_repo_name,
            "--region", region,
            "--query", "imageIds[*]",
            "--output", "json"
        ]
        
        result = utils.run_command(list_images_cmd, capture_output=True)
        if result.returncode == 0:
            import json
            images = json.loads(result.stdout)
            if images:
                # Delete all images
                for image in images:
                    delete_image_cmd = [
                        "aws", "ecr", "batch-delete-image",
                        "--repository-name", ecr_repo_name,
                        "--region", region,
                        "--image-ids", json.dumps([image])
                    ]
                    utils.run_command(delete_image_cmd, check=False)
        
        # Delete the repository
        delete_repo_cmd = [
            "aws", "ecr", "delete-repository",
            "--repository-name", ecr_repo_name,
            "--region", region,
            "--force"
        ]
        
        result = utils.run_command(delete_repo_cmd, check=False)
        if result.returncode == 0:
            console.print(f"[green]✅ ECR repository '{ecr_repo_name}' deleted successfully[/green]")
        else:
            console.print(f"[yellow]⚠️  Could not delete ECR repository: {result.stderr}[/yellow]")
        
        console.print("[green]✅ Cleanup completed successfully![/green]")
        
    except Exception as e:
        utils.print_error(f"Failed to delete deployment: {e}")
        raise typer.Exit(1)


@app.command()
def show_status(
    config_path: Optional[str] = typer.Option(None, "--config", "-c", help="Path to config file"),
):
    """Show deployment status and information."""
    try:
        # Load config
        config = utils.load_config(config_path)
        if not config:
            raise typer.Exit(1)
        
        stack_name = config["deployment"]["stack_name"]
        region = config["deployment"]["region"]
        lambda_name = config["deployment"]["lambda_name"]
        
        console.print(f"[blue]📊 Checking status for stack '{stack_name}'...[/blue]")
        
        # Get stack status
        describe_cmd = [
            "aws", "cloudformation", "describe-stacks",
            "--stack-name", stack_name,
            "--region", region,
            "--query", "Stacks[0]",
            "--output", "json"
        ]
        
        result = utils.run_command(describe_cmd, capture_output=True)
        if result.returncode != 0:
            utils.print_error(f"Failed to get stack status: {result.stderr}")
            raise typer.Exit(1)
        
        import json
        stack_info = json.loads(result.stdout)
        
        # Display status
        table = Table(title=f"Stack Status: {stack_name}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Stack Name", stack_name)
        table.add_row("Status", stack_info["StackStatus"])
        table.add_row("Region", region)
        table.add_row("Lambda Function", lambda_name)
        
        # Get API Gateway URL if available
        for output in stack_info.get("Outputs", []):
            if output["OutputKey"] == "ApiUrl":
                table.add_row("API Gateway URL", output["OutputValue"])
                break
        
        console.print(table)
        
        # Get Lambda function info
        lambda_cmd = [
            "aws", "lambda", "get-function",
            "--function-name", lambda_name,
            "--region", region,
            "--query", "Configuration.{Runtime:Runtime,MemorySize:MemorySize,Timeout:Timeout,LastModified:LastModified}",
            "--output", "table"
        ]
        
        result = utils.run_command(lambda_cmd, capture_output=True)
        if result.returncode == 0:
            console.print("\n[blue]Lambda Function Details:[/blue]")
            print(result.stdout)
        
    except Exception as e:
        utils.print_error(f"Failed to get status: {e}")
        raise typer.Exit(1)


# ============================================================================
# AI AGENT COMMANDS
# ============================================================================

@app.command()
def chat(
    openai_api_key: Optional[str] = typer.Option(None, "--api-key", "-k", help="OpenAI API key"),
    interactive: bool = typer.Option(True, "--interactive", "-i", help="Run in interactive mode"),
):
    """Start the AI agent in chat mode for natural language DevOps commands."""
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


# ============================================================================
# ADD SUBCOMMANDS FROM OTHER MODULES
# ============================================================================

# Create serverless subcommand group
serverless_app = typer.Typer(name="serverless", help="Serverless deployment commands")

@serverless_app.command()
def deploy(
    lambda_name: str = typer.Option(None, "--name", "-n", help="Name for your Lambda function"),
    region: str = typer.Option(None, "--region", "-r", help="AWS region"),
    port: int = typer.Option(8000, "--port", "-p", help="Application port"),
    memory_size: int = typer.Option(512, "--memory", help="Lambda memory size (MB)"),
    timeout: int = typer.Option(30, "--timeout", "-t", help="Lambda timeout (seconds)"),
    image_tag: str = typer.Option(None, "--image-tag", "-i", help="Docker image tag to use for deployment"),
    config_path: Optional[str] = typer.Option(None, "--config", "-c", help="Path to config file"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug mode with verbose output"),
):
    """Deploy Flask app to AWS Lambda + API Gateway."""
    return serverless_deploy(
        lambda_name=lambda_name,
        region=region,
        port=port,
        memory_size=memory_size,
        timeout=timeout,
        image_tag=image_tag,
        config_path=config_path,
        debug=debug
    )

@serverless_app.command()
def generate(
    lambda_name: str = typer.Option(None, "--name", "-n", help="Name for your Lambda function"),
    region: str = typer.Option("us-east-1", "--region", "-r", help="AWS region"),
    port: int = typer.Option(8000, "--port", "-p", help="Application port"),
    memory_size: int = typer.Option(512, "--memory", help="Lambda memory size (MB)"),
    timeout: int = typer.Option(30, "--timeout", "-t", help="Lambda timeout (seconds)"),
    image_tag: str = typer.Option(None, "--image-tag", "-i", help="Docker image tag to use for deployment"),
    config_path: Optional[str] = typer.Option(None, "--config", "-c", help="Path to config file"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files"),
):
    """Generate deployment files (Dockerfile, template.yml, etc.) without deploying."""
    return generate_files(
        lambda_name=lambda_name,
        region=region,
        port=port,
        memory_size=memory_size,
        timeout=timeout,
        image_tag=image_tag,
        config_path=config_path,
        force=force
    )

@serverless_app.command()
def logs(
    config_path: Optional[str] = typer.Option(None, "--config", "-c", help="Path to config file"),
    stack_name: Optional[str] = typer.Option(None, "--stack-name", "-s", help="Name of the CloudFormation stack"),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region"),
    function_name: Optional[str] = typer.Option(None, "--function", "-f", help="Specific Lambda function name"),
    follow: bool = typer.Option(False, "--follow", help="Follow logs in real-time"),
    lines: int = typer.Option(50, "--lines", "-n", help="Number of log lines to show")
):
    """Stream logs from your deployed function."""
    return stream_logs(
        config_path=config_path,
        stack_name=stack_name,
        region=region,
        function_name=function_name,
        follow=follow,
        lines=lines
    )

@serverless_app.command()
def delete(
    config_path: Optional[str] = typer.Option(None, "--config", "-c", help="Path to config file"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Remove the deployed stack and clean up ECR."""
    return delete_deployment(
        config_path=config_path,
        force=force
    )

@serverless_app.command()
def status(
    config_path: Optional[str] = typer.Option(None, "--config", "-c", help="Path to config file"),
):
    """Show deployment status and information."""
    return show_status(
        config_path=config_path
    )

# Add serverless commands
app.add_typer(serverless_app, name="serverless", help="Serverless deployment commands")

# Add EventBridge commands
app.add_typer(eventbridge_app, name="eventbridge", help="Manage AWS EventBridge rules")

# Add GitHub Actions commands
app.add_typer(github_actions_app, name="github-actions", help="Manage GitHub Actions workflows")

# Add Amplify commands
app.add_typer(amplify_app, name="amplify", help="Deploy React apps to AWS Amplify")


if __name__ == "__main__":
    app() 