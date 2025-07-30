"""CLI interface for devops-ai."""

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
from devops_ai_serverless import utils
from devops_ai_serverless import templates
from devops_ai_eventbridge.cli import app as eventbridge_app
from devops_ai_github_actions.cli import app as github_actions_app
from devops_ai_amplify.cli import app as amplify_app


app = typer.Typer(
    name="devops-ai-serverless",
    help="Deploy Flask apps to AWS Lambda + API Gateway and React apps to AWS Amplify with zero code changes",
    add_completion=False,
)
console = Console()


@app.command()
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
    try:
        if not image_tag:
            # generate a random image tag YYYYMMDDHHMMSS
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
        console.print(f"\nNext step: Run [yellow]devops-ai deploy[/yellow] to deploy to AWS")
        
    except Exception as e:
        utils.print_error(f"Failed to generate files: {e}")
        raise typer.Exit(1)


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
    """Deploy Flask app to AWS Lambda + API Gateway (init + build + deploy in one step)."""
    try:
        if not image_tag:
            # generate a random image tag YYYYMMDDHHMMSS
            image_tag = datetime.now().strftime("%Y%m%d%H%M%S")
            
        project_root = utils.get_project_root()
        
        # Check prerequisites
        if not utils.check_prerequisites():
            raise typer.Exit(1)
        
        # Check AWS permissions
        if not utils.check_aws_permissions():
            raise typer.Exit(1)
        
        # Check SAM configuration
        utils.check_sam_configuration()
        
        # Get or prompt for lambda name
        if lambda_name is None:
            lambda_name = Prompt.ask(
                "Enter a name for your Lambda function",
                default=f"{project_root.name}-flask-app"
            )
        
        # Use default region if not provided
        if region is None:
            region = "us-east-1"
        
        # Get AWS account ID early for SAM config
        account_id = utils.get_aws_account_id()
        
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
                "base_image": "public.ecr.aws/lambda/python:3.11",
                "working_dir": "/var/task"
            }
        }
        
        # Save config for future use
        utils.save_config(config, config_path)
        
        # Start deployment with progress tracking
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            # Calculate total steps for percentage
            total_steps = 8  # Added S3 bucket creation step
            current_step = 0
            
            # Step 1: Generate deployment files
            current_step += 1
            percentage = int((current_step / total_steps) * 100)
            task1 = progress.add_task(f"Generating deployment files... ({percentage}%)", total=None)
            
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

            # Generate lambda_entry.py wrapper for Lambda
            lambda_entry_content = templates.LAMBDA_ENTRY_TEMPLATE.render(
                app_module=config["app"]["module"],
                app_object=config["app"]["object"]
            )
            lambda_entry_path = project_root / "lambda_entry.py"
            with open(lambda_entry_path, 'w') as f:
                f.write(lambda_entry_content)
            
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
            
            # Generate requirements.txt if it doesn't exist
            requirements_path = project_root / "requirements.txt"
            if not requirements_path.exists():
                requirements_content = templates.REQUIREMENTS_TEMPLATE.render()
                with open(requirements_path, 'w') as f:
                    f.write(requirements_content)
            
            # Generate .dockerignore if it doesn't exist
            dockerignore_path = project_root / ".dockerignore"
            if not dockerignore_path.exists():
                dockerignore_content = templates.DOCKERIGNORE_TEMPLATE.render()
                with open(dockerignore_path, 'w') as f:
                    f.write(dockerignore_content)
            
            progress.update(task1, description=f"✅ Deployment files generated ({percentage}%)", completed=True)
            
            # Step 2: Create ECR repository
            current_step += 1
            percentage = int((current_step / total_steps) * 100)
            task2 = progress.add_task(f"Creating ECR repository... ({percentage}%)", total=None)
            
            if debug:
                console.print(f"[blue]Debug: Using image tag: {image_tag}[/blue]")
            
            repo_name = utils.get_ecr_repository_name(stack_name)
            repo_uri = utils.create_ecr_repository(repo_name, region)
            image_uri = f"{repo_uri}:{image_tag}"
            
            # Remove any existing SAM config to avoid conflicts
            sam_config_path = project_root / "samconfig.toml"
            if sam_config_path.exists():
                sam_config_path.unlink()
                if debug:
                    console.print("[blue]Debug: Removed existing samconfig.toml to avoid conflicts[/blue]")
            
            progress.update(task2, description=f"✅ ECR repository created ({percentage}%)", completed=True)
            
            # Step 3: Create S3 bucket for deployment artifacts
            current_step += 1
            percentage = int((current_step / total_steps) * 100)
            task3 = progress.add_task(f"Creating S3 bucket... ({percentage}%)", total=None)
            
            # Create S3 bucket name based on lambda name and region
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
                if debug:
                    console.print(f"[blue]Debug: Created S3 bucket: {s3_bucket_name}[/blue]")
            except Exception as e:
                if "BucketAlreadyExists" in str(e) or "BucketAlreadyOwnedByYou" in str(e):
                    if debug:
                        console.print(f"[blue]Debug: S3 bucket {s3_bucket_name} already exists[/blue]")
                else:
                    console.print(f"[yellow]Warning: Could not create S3 bucket: {e}[/yellow]")
                    console.print("[yellow]SAM will create one automatically with --resolve-s3[/yellow]")
                    s3_bucket_name = None
            
            progress.update(task3, description=f"✅ S3 bucket created ({percentage}%)", completed=True)
            
            # Step 4: Login to ECR
            current_step += 1
            percentage = int((current_step / total_steps) * 100)
            task4 = progress.add_task(f"Logging into ECR... ({percentage}%)", total=None)
            
            account_id = utils.get_aws_account_id()
            login_cmd = [
                "aws", "ecr", "get-login-password", "--region", region
            ]
            login_result = utils.run_command(login_cmd)
            
            docker_login_cmd = [
                "docker", "login", "--username", "AWS", "--password-stdin",
                f"{account_id}.dkr.ecr.{region}.amazonaws.com"
            ]
            utils.run_command(docker_login_cmd, input_text=login_result.stdout)
            
            progress.update(task4, description=f"✅ Logged into ECR ({percentage}%)", completed=True)
            
            # Step 5: Build Docker image
            current_step += 1
            percentage = int((current_step / total_steps) * 100)
            task5 = progress.add_task(f"Building Docker image... ({percentage}%)", total=None)
            
            build_cmd = [
                "docker", "buildx", "build", "--platform", "linux/amd64", "-t", image_uri, "."
            ]
            utils.run_command(build_cmd, cwd=project_root)
            
            progress.update(task5, description=f"✅ Docker image built ({percentage}%)", completed=True)
            
            # Step 6: Push to ECR
            current_step += 1
            percentage = int((current_step / total_steps) * 100)
            task6 = progress.add_task(f"Pushing image to ECR... ({percentage}%)", total=None)
            
            push_cmd = ["docker", "push", image_uri]
            utils.run_command(push_cmd)
            
            progress.update(task6, description=f"✅ Image pushed to ECR ({percentage}%)", completed=True)
            
            # Step 7: Validate SAM template
            current_step += 1
            percentage = int((current_step / total_steps) * 100)
            task7 = progress.add_task(f"Validating SAM template... ({percentage}%)", total=None)
            
            # Validate SAM template first
            validate_cmd = ["sam", "validate", "--template-file", "template.yml"]
            
            if debug:
                console.print(f"[blue]Debug: Validating SAM template with command: {' '.join(validate_cmd)}[/blue]")
                console.print(f"[blue]Debug: SAM template content:[/blue]")
                with open(sam_path, 'r') as f:
                    console.print(f"[dim]{f.read()}[/dim]")
            
            validate_result = utils.run_command(validate_cmd, cwd=project_root, timeout=60)
            
            if validate_result.returncode != 0:
                console.print(f"[red]SAM template validation failed:[/red]")
                if validate_result.stderr:
                    console.print(f"[red]{validate_result.stderr}[/red]")
                raise Exception("SAM template validation failed")
            
            progress.update(task7, description=f"✅ SAM template validated ({percentage}%)", completed=True)
            
            # Step 8: Deploy with SAM
            current_step += 1
            percentage = int((current_step / total_steps) * 100)
            task8 = progress.add_task(f"Deploying to AWS Lambda... ({percentage}%)", total=None)
            
            # Check if stack exists to determine if this is first deployment
            try:
                cloudformation = utils.boto3.client('cloudformation', region_name=region)
                cloudformation.describe_stacks(StackName=stack_name)
                stack_exists = True
            except:
                stack_exists = False
            
            # Build parameter overrides including environment variables
            parameter_overrides = [f"ImageUri={image_uri}"]
            
            # Add environment variables as parameters
            if env_vars:
                for key, value in env_vars.items():
                    # Escape any special characters in the value
                    escaped_value = value.replace('"', '\\"').replace("'", "\\'")
                    parameter_overrides.append(f'{key}="{escaped_value}"')
            
            # Use command line parameters to avoid user prompts
            deploy_cmd = [
                "sam", "deploy",
                "--stack-name", stack_name,
                "--region", region,
                "--capabilities", "CAPABILITY_NAMED_IAM",
                "--no-confirm-changeset",
                "--no-fail-on-empty-changeset",
                "--parameter-overrides"
            ] + parameter_overrides + [
                "--image-repositories", 
                f"FlaskFunction={image_uri}",
                "--force-upload"
            ]
            
            if debug:
                console.print(f"[blue]Debug: SAM deploy command: {' '.join(deploy_cmd)}[/blue]")
            
            # Add S3 bucket if we created one, otherwise use resolve-s3
            if s3_bucket_name:
                deploy_cmd.extend(["--s3-bucket", s3_bucket_name])
                if debug:
                    console.print(f"[blue]Debug: Using S3 bucket: {s3_bucket_name}[/blue]")
            else:
                deploy_cmd.append("--resolve-s3")
                if debug:
                    console.print("[blue]Debug: Using --resolve-s3 to auto-create S3 bucket[/blue]")
            
            try:
                # Run SAM deploy with timeout and better error handling
                console.print(f"[blue]Running: {' '.join(deploy_cmd)}[/blue]")
                console.print("[yellow]Note: SAM deployment can take 5-15 minutes for first deployment[/yellow]")
                console.print("[blue]Debug: Using --resolve-s3 to automatically create S3 bucket[/blue]")
                result = utils.run_command(deploy_cmd, cwd=project_root, timeout=1800)  # 30 minutes timeout
                
                if result.returncode != 0:
                    console.print(f"[red]SAM deployment failed with return code: {result.returncode}[/red]")
                    if result.stdout:
                        console.print(f"[blue]STDOUT:[/blue]\n{result.stdout}")
                    if result.stderr:
                        console.print(f"[red]STDERR:[/red]\n{result.stderr}")
                    
                    # Get additional debugging information
                    console.print("\n[bold blue]🔍 Gathering additional debugging information...[/bold blue]")
                    
                    # Get deployment status
                    status = utils.get_deployment_status(stack_name, region)
                    if 'error' not in status:
                        console.print(f"[blue]Stack Status: {status['stack_status']}[/blue]")
                        if status['stack_status_reason']:
                            console.print(f"[blue]Status Reason: {status['stack_status_reason']}[/blue]")
                        
                        # Show recent stack events
                        if status['recent_events']:
                            console.print("\n[bold]Recent Stack Events:[/bold]")
                            for event in status['recent_events'][:5]:  # Show last 5 events
                                timestamp = event['Timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                                status_color = "green" if "COMPLETE" in event['ResourceStatus'] else "red" if "FAILED" in event['ResourceStatus'] else "yellow"
                                console.print(f"[{status_color}]{timestamp} - {event['ResourceType']} - {event['ResourceStatus']}[/{status_color}]")
                                if event.get('ResourceStatusReason'):
                                    console.print(f"  [dim]Reason: {event['ResourceStatusReason']}[/dim]")
                    
                    # Try to get logs
                    console.print("\n[bold]Attempting to get logs...[/bold]")
                    sam_logs = utils.get_sam_logs(stack_name, region)
                    if sam_logs and "Failed to get SAM logs" not in sam_logs:
                        console.print(f"[blue]SAM Logs:[/blue]\n{sam_logs}")
                    else:
                        console.print("[yellow]Could not get SAM logs, trying CloudWatch logs...[/yellow]")
                        cw_logs = utils.get_cloudwatch_logs(stack_name, region)
                        if cw_logs and "Failed to get CloudWatch logs" not in cw_logs:
                            console.print(f"[blue]CloudWatch Logs:[/blue]\n{cw_logs}")
                        else:
                            console.print("[yellow]Could not retrieve logs. Check AWS CloudWatch console manually.[/yellow]")
                    
                    # Provide specific guidance based on error
                    if "AccessDenied" in result.stderr:
                        console.print("[red]Access denied error. Check your AWS permissions.[/red]")
                    elif "NoSuchBucket" in result.stderr:
                        console.print("[yellow]S3 bucket not found. SAM will create it automatically.[/yellow]")
                    elif "Stack already exists" in result.stderr:
                        console.print("[yellow]Stack already exists. This is normal for updates.[/yellow]")
                    elif "Invalid template" in result.stderr:
                        console.print("[red]Template validation failed. Check the SAM template.[/red]")
                    
                    raise Exception(f"SAM deployment failed with exit code {result.returncode}")
                
                progress.update(task8, description=f"✅ Deployed to AWS Lambda ({percentage}%)", completed=True)
                
            except subprocess.TimeoutExpired:
                console.print(Panel(
                    "[red]SAM deployment timed out after 30 minutes[/red]\n\n"
                    "[yellow]This might be due to:[/yellow]\n"
                    "• Large Docker image taking time to upload\n"
                    "• AWS CloudFormation taking time to create resources\n"
                    "• Network connectivity issues\n"
                    "• SAM waiting for user input (check terminal)\n\n"
                    "[bold]Troubleshooting steps:[/bold]\n"
                    "1. Check if SAM is waiting for input in another terminal\n"
                    "2. Verify your AWS credentials: [yellow]aws sts get-caller-identity[/yellow]\n"
                    "3. Check CloudFormation console for stuck resources\n"
                    "4. Try manual deployment:\n"
                    f"   [yellow]sam deploy --region {region} --stack-name {stack_name} --parameter-overrides ImageUri={image_uri} --capabilities CAPABILITY_IAM[/yellow]\n\n"
                    "5. If stuck, you can cancel with Ctrl+C and retry",
                    title="Deployment Timeout",
                    border_style="red"
                ))
                raise typer.Exit(1)
            except Exception as e:
                console.print(f"[red]SAM deployment error: {e}[/red]")
                raise
            
            # Save image URI and tag to config for future use
            config["deployment"]["image_uri"] = image_uri
            config["deployment"]["image_tag"] = image_tag
            utils.save_config(config, config_path)
        
        # Get deployment outputs
        outputs = utils.get_stack_outputs(stack_name, region)
        
        if "FlaskApi" in outputs:
            api_url = outputs["FlaskApi"]
            console.print(Panel(
                f"[green]🎉 Deployment successful![/green]\n\n"
                f"Lambda Function: [blue]{lambda_name}[/blue]\n"
                f"API Gateway URL: [blue]{api_url}[/blue]\n"
                f"Region: [blue]{region}[/blue]\n\n"
                f"Your Flask app is now running on AWS Lambda + API Gateway!\n\n"
                f"Next steps:\n"
                            f"• [yellow]devops-ai logs[/yellow] - View logs\n"
            f"• [yellow]devops-ai status[/yellow] - Check status\n"
            f"• [yellow]devops-ai delete[/yellow] - Clean up",
                title="🚀 Deployment Complete",
                border_style="green"
            ))
        else:
            utils.print_success("Deployment completed successfully!")
        
    except Exception as e:
        utils.print_error(f"Deployment failed: {e}")
        console.print(Panel(
            utils.get_aws_error_guidance(e),
            title="Error Guidance",
            border_style="red"
        ))
        raise typer.Exit(1)


@app.command()
def logs(
    config_path: Optional[str] = typer.Option(None, "--config", "-c", help="Path to config file"),
    stack_name: Optional[str] = typer.Option(None, "--stack-name", "-s", help="Name of the CloudFormation stack"),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region"),
    function_name: Optional[str] = typer.Option(None, "--function", "-f", help="Specific Lambda function name"),
    follow: bool = typer.Option(False, "--follow", help="Follow logs in real-time"),
    lines: int = typer.Option(50, "--lines", "-n", help="Number of log lines to show")
):
    """Get logs for a deployed Lambda function using multiple methods."""
    try:
        # Get stack name and region from config or parameters
        if stack_name is None or region is None:
            config = utils.load_config(config_path)
            stack_name = stack_name or config["deployment"]["stack_name"]
            region = region or config["deployment"]["region"]
        
        console.print(f"[bold blue]📋 Getting logs for stack: {stack_name}[/bold blue]")
        
        # Get deployment status first
        status = utils.get_deployment_status(stack_name, region)
        if 'error' not in status:
            console.print(f"[blue]Stack Status: {status['stack_status']}[/blue]")
            if status['stack_status_reason']:
                console.print(f"[blue]Status Reason: {status['stack_status_reason']}[/blue]")
        
        # Try multiple logging methods
        logs_found = False
        
        # Method 1: SAM logs
        console.print("\n[bold]Method 1: SAM Logs[/bold]")
        try:
            sam_logs = utils.get_sam_logs(stack_name, region, function_name)
            if sam_logs and "Failed to get SAM logs" not in sam_logs:
                console.print(f"[green]✅ SAM logs retrieved[/green]")
                console.print(sam_logs)
                logs_found = True
            else:
                console.print("[yellow]⚠️  No SAM logs available[/yellow]")
        except Exception as e:
            console.print(f"[yellow]⚠️  SAM logs failed: {e}[/yellow]")
        
        # Method 2: CloudWatch logs
        if not logs_found:
            console.print("\n[bold]Method 2: CloudWatch Logs[/bold]")
            try:
                cw_logs = utils.get_cloudwatch_logs(stack_name, region)
                if cw_logs and "Failed to get CloudWatch logs" not in cw_logs:
                    console.print(f"[green]✅ CloudWatch logs retrieved[/green]")
                    console.print(cw_logs)
                    logs_found = True
                else:
                    console.print("[yellow]⚠️  No CloudWatch logs available[/yellow]")
            except Exception as e:
                console.print(f"[yellow]⚠️  CloudWatch logs failed: {e}[/yellow]")
        
        # Method 3: AWS CLI logs
        if not logs_found:
            console.print("\n[bold]Method 3: AWS CLI Logs[/bold]")
            try:
                # Try to get Lambda function name from stack outputs
                for output in status.get('outputs', []):
                    if 'Function' in output['OutputKey']:
                        function_name = output['OutputValue'].split('/')[-1]
                        log_group = f"/aws/lambda/{function_name}"
                        
                        # Use AWS CLI to get logs
                        cmd = ["aws", "logs", "describe-log-streams", 
                               "--log-group-name", log_group, 
                               "--region", region,
                               "--order-by", "LastEventTime",
                               "--descending",
                               "--max-items", "5"]
                        
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                        if result.returncode == 0:
                            import json
                            streams = json.loads(result.stdout)['logStreams']
                            
                            for stream in streams:
                                stream_name = stream['logStreamName']
                                cmd = ["aws", "logs", "get-log-events",
                                       "--log-group-name", log_group,
                                       "--log-stream-name", stream_name,
                                       "--region", region,
                                       "--limit", str(lines)]
                                
                                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                                if result.returncode == 0:
                                    events = json.loads(result.stdout)['events']
                                    if events:
                                        console.print(f"[green]✅ AWS CLI logs from stream: {stream_name}[/green]")
                                        for event in events:
                                            timestamp = event['timestamp']
                                            message = event['message']
                                            console.print(f"{timestamp}: {message}")
                                        logs_found = True
                                        break
                        
                        break
                
                if not logs_found:
                    console.print("[yellow]⚠️  No AWS CLI logs available[/yellow]")
                    
            except Exception as e:
                console.print(f"[yellow]⚠️  AWS CLI logs failed: {e}[/yellow]")
        
        if not logs_found:
            console.print("\n[red]❌ No logs found from any method[/red]")
            console.print("[yellow]Manual troubleshooting steps:[/yellow]")
            console.print("1. Check AWS CloudWatch console: https://console.aws.amazon.com/cloudwatch/")
            console.print("2. Verify the stack exists: aws cloudformation describe-stacks --stack-name " + stack_name)
            console.print("3. Check Lambda function status: aws lambda list-functions")
            console.print("4. Verify your AWS credentials and permissions")
        
    except Exception as e:
        console.print(f"[red]❌ Failed to get logs: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def logs_direct(
    stack_name: str = typer.Option(..., "--stack-name", "-s", help="Name of the CloudFormation stack"),
    region: str = typer.Option("us-east-1", "--region", "-r", help="AWS region"),
    function_name: Optional[str] = typer.Option(None, "--function", "-f", help="Specific Lambda function name"),
    lines: int = typer.Option(50, "--lines", "-n", help="Number of log lines to show")
):
    """Get logs directly by stack name (no config file needed)."""
    try:
        console.print(f"[bold blue]📋 Getting logs for stack: {stack_name}[/bold blue]")
        
        # Get deployment status first
        status = utils.get_deployment_status(stack_name, region)
        if 'error' not in status:
            console.print(f"[blue]Stack Status: {status['stack_status']}[/blue]")
            if status['stack_status_reason']:
                console.print(f"[blue]Status Reason: {status['stack_status_reason']}[/blue]")
        
        # Try multiple logging methods
        logs_found = False
        
        # Method 1: SAM logs
        console.print("\n[bold]Method 1: SAM Logs[/bold]")
        try:
            sam_logs = utils.get_sam_logs(stack_name, region, function_name)
            if sam_logs and "Failed to get SAM logs" not in sam_logs:
                console.print(f"[green]✅ SAM logs retrieved[/green]")
                console.print(sam_logs)
                logs_found = True
            else:
                console.print("[yellow]⚠️  No SAM logs available[/yellow]")
        except Exception as e:
            console.print(f"[yellow]⚠️  SAM logs failed: {e}[/yellow]")
        
        # Method 2: CloudWatch logs
        if not logs_found:
            console.print("\n[bold]Method 2: CloudWatch Logs[/bold]")
            try:
                cw_logs = utils.get_cloudwatch_logs(stack_name, region)
                if cw_logs and "Failed to get CloudWatch logs" not in cw_logs:
                    console.print(f"[green]✅ CloudWatch logs retrieved[/green]")
                    console.print(cw_logs)
                    logs_found = True
                else:
                    console.print("[yellow]⚠️  No CloudWatch logs available[/yellow]")
            except Exception as e:
                console.print(f"[yellow]⚠️  CloudWatch logs failed: {e}[/yellow]")
        
        # Method 3: AWS CLI logs
        if not logs_found:
            console.print("\n[bold]Method 3: AWS CLI Logs[/bold]")
            try:
                # Try to get Lambda function name from stack outputs
                for output in status.get('outputs', []):
                    if 'Function' in output['OutputKey']:
                        function_name = output['OutputValue'].split('/')[-1]
                        log_group = f"/aws/lambda/{function_name}"
                        
                        # Use AWS CLI to get logs
                        cmd = ["aws", "logs", "describe-log-streams", 
                               "--log-group-name", log_group, 
                               "--region", region,
                               "--order-by", "LastEventTime",
                               "--descending",
                               "--max-items", "5"]
                        
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                        if result.returncode == 0:
                            import json
                            streams = json.loads(result.stdout)['logStreams']
                            
                            for stream in streams:
                                stream_name = stream['logStreamName']
                                cmd = ["aws", "logs", "get-log-events",
                                       "--log-group-name", log_group,
                                       "--log-stream-name", stream_name,
                                       "--region", region,
                                       "--limit", str(lines)]
                                
                                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                                if result.returncode == 0:
                                    events = json.loads(result.stdout)['events']
                                    if events:
                                        console.print(f"[green]✅ AWS CLI logs from stream: {stream_name}[/green]")
                                        for event in events:
                                            timestamp = event['timestamp']
                                            message = event['message']
                                            console.print(f"{timestamp}: {message}")
                                        logs_found = True
                                        break
                        
                        break
                
                if not logs_found:
                    console.print("[yellow]⚠️  No AWS CLI logs available[/yellow]")
                    
            except Exception as e:
                console.print(f"[yellow]⚠️  AWS CLI logs failed: {e}[/yellow]")
        
        if not logs_found:
            console.print("\n[red]❌ No logs found from any method[/red]")
            console.print("[yellow]Manual troubleshooting steps:[/yellow]")
            console.print("1. Check AWS CloudWatch console: https://console.aws.amazon.com/cloudwatch/")
            console.print("2. Verify the stack exists: aws cloudformation describe-stacks --stack-name " + stack_name)
            console.print("3. Check Lambda function status: aws lambda list-functions")
            console.print("4. Verify your AWS credentials and permissions")
        
    except Exception as e:
        console.print(f"[red]❌ Failed to get logs: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def delete(
    config_path: Optional[str] = typer.Option(None, "--config", "-c", help="Path to config file"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Delete the deployed stack and clean up ECR repository."""
    try:
        # Load configuration
        config = utils.load_config(config_path)
        stack_name = config["deployment"]["stack_name"]
        region = config["deployment"]["region"]
        
        # Check prerequisites
        if not utils.check_prerequisites():
            raise typer.Exit(1)
        
        # Confirm deletion
        if not force:
            confirmed = Confirm.ask(
                f"Are you sure you want to delete stack '{stack_name}' and clean up ECR repository?"
            )
            if not confirmed:
                console.print("[yellow]Deletion cancelled.[/yellow]")
                return
        
        # Delete SAM stack
        console.print(f"[blue]Deleting CloudFormation stack: {stack_name}[/blue]")
        delete_cmd = ["sam", "delete", "--stack-name", stack_name, "--region", region]
        utils.run_command(delete_cmd)
        
        # Clean up ECR repository
        repo_name = utils.get_ecr_repository_name(stack_name)
        console.print(f"[blue]Cleaning up ECR repository: {repo_name}[/blue]")
        utils.delete_ecr_repository(repo_name, region)
        
        # Remove image_uri from config
        if "image_uri" in config["deployment"]:
            del config["deployment"]["image_uri"]
            utils.save_config(config, config_path)
        
        utils.print_success("Stack and ECR repository deleted successfully!")
        
    except Exception as e:
        utils.print_error(f"Deletion failed: {e}")
        raise typer.Exit(1)


@app.command()
def status(
    config_path: Optional[str] = typer.Option(None, "--config", "-c", help="Path to config file"),
):
    """Show deployment status and information."""
    try:
        # Load configuration
        config = utils.load_config(config_path)
        stack_name = config["deployment"]["stack_name"]
        region = config["deployment"]["region"]
        
        # Check prerequisites
        if not utils.check_prerequisites():
            raise typer.Exit(1)
        
        # Get stack status
        try:
            cloudformation = utils.boto3.client('cloudformation', region_name=region)
            response = cloudformation.describe_stacks(StackName=stack_name)
            stack = response['Stacks'][0]
            stack_status = stack['StackStatus']
            outputs = {output['OutputKey']: output['OutputValue'] for output in stack.get('Outputs', [])}
        except Exception as e:
            stack_status = "NOT_FOUND"
            outputs = {}
        
        # Create status table
        table = Table(title=f"Deployment Status: {stack_name}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Stack Name", stack_name)
        table.add_row("Region", region)
        table.add_row("Stack Status", stack_status)
        
        if "image_uri" in config["deployment"]:
            table.add_row("Image URI", config["deployment"]["image_uri"])
        
        if "FlaskApi" in outputs:
            table.add_row("API URL", outputs["FlaskApi"])
        
        console.print(table)
        
    except Exception as e:
        utils.print_error(f"Failed to get status: {e}")
        raise typer.Exit(1)


@app.command()
def troubleshoot():
    """Show AWS troubleshooting guide and common solutions."""
    console.print(Panel(
        "[bold blue]AWS Troubleshooting Guide[/bold blue]\n\n"
        "[bold]1. AWS Credentials & Configuration[/bold]\n"
        "• Run: [yellow]aws configure[/yellow]\n"
        "• Set your AWS Access Key ID, Secret Access Key, and default region\n"
        "• Or use AWS SSO: [yellow]aws configure sso[/yellow]\n\n"
        "[bold]2. Required AWS Permissions[/bold]\n"
        "Your AWS user needs these permissions:\n"
        "• [yellow]sts:GetCallerIdentity[/yellow] - Get account info\n"
        "• [yellow]ecr:*[/yellow] - Container registry operations\n"
        "• [yellow]cloudformation:*[/yellow] - Infrastructure deployment\n"
        "• [yellow]lambda:*[/yellow] - Lambda function management\n"
        "• [yellow]apigateway:*[/yellow] - API Gateway management\n"
        "• [yellow]logs:*[/yellow] - CloudWatch logs access\n"
        "• [yellow]iam:PassRole[/yellow] - Pass IAM roles to Lambda\n\n"
        "[bold]3. Quick Permission Setup[/bold]\n"
        "For testing, attach the [yellow]AdministratorAccess[/yellow] managed policy:\n"
        "• Go to AWS IAM Console\n"
        "• Find your user\n"
        "• Attach [yellow]AdministratorAccess[/yellow] policy\n\n"
        "[bold]4. Common Error Solutions[/bold]\n"
        "• [red]AccessDenied[/red] → Check IAM permissions\n"
        "• [red]NoSuchBucket[/red] → SAM will create S3 bucket automatically\n"
        "• [red]RepositoryAlreadyExists[/red] → Normal, repository already created\n"
                    "• [red]ImageNotFound[/red] → Run [yellow]devops-ai build[/yellow] first\n\n"
        "[bold]5. Region-Specific Issues[/bold]\n"
        "• Ensure all services are available in your chosen region\n"
        "• Some regions may not support all Lambda features\n"
        "• Recommended: [yellow]us-east-1[/yellow], [yellow]us-west-2[/yellow], [yellow]eu-west-1[/yellow]\n\n"
        "[bold]6. Docker Issues[/bold]\n"
        "• Ensure Docker is running: [yellow]docker --version[/yellow]\n"
        "• Check Docker daemon: [yellow]docker ps[/yellow]\n"
        "• On macOS/Windows: Start Docker Desktop\n\n"
        "[bold]7. SAM CLI Issues[/bold]\n"
        "• Update SAM CLI: [yellow]pip install --upgrade aws-sam-cli[/yellow]\n"
        "• Check SAM version: [yellow]sam --version[/yellow]\n"
        "• Ensure SAM is in your PATH\n\n"
        "[bold]8. Network Issues[/bold]\n"
        "• Check internet connection\n"
        "• Corporate firewall? Configure proxy settings\n"
        "• VPN issues? Try disconnecting temporarily\n\n"
        "[bold]9. Still Having Issues?[/bold]\n"
                    "• Run: [yellow]devops-ai status[/yellow] to check deployment\n"
        "• Check AWS CloudFormation console for stack errors\n"
                    "• Review CloudWatch logs: [yellow]devops-ai logs[/yellow]\n"
        "• Open an issue on GitHub with error details",
        title="AWS Troubleshooting Guide",
        border_style="blue"
    ))


@app.command()
def doctor():
    """Diagnose and fix common issues."""
    console.print("[blue]🔍 Running diagnostics...[/blue]")
    
    issues = []
    fixes = []
    
    # Check AWS CLI
    try:
        result = utils.run_command(["aws", "--version"], check=False)
        if result.returncode == 0:
            console.print("[green]✓ AWS CLI is installed[/green]")
        else:
            issues.append("AWS CLI not working properly")
            fixes.append("Run: pip install awscli or download from AWS website")
    except FileNotFoundError:
        issues.append("AWS CLI not installed")
        fixes.append("Run: pip install awscli or download from AWS website")
    
    # Check SAM CLI
    try:
        result = utils.run_command(["sam", "--version"], check=False)
        if result.returncode == 0:
            console.print("[green]✓ AWS SAM CLI is installed[/green]")
        else:
            issues.append("AWS SAM CLI not working properly")
            fixes.append("Run: pip install aws-sam-cli")
    except FileNotFoundError:
        issues.append("AWS SAM CLI not installed")
        fixes.append("Run: pip install aws-sam-cli")
    
    # Check Docker
    try:
        result = utils.run_command(["docker", "--version"], check=False)
        if result.returncode == 0:
            console.print("[green]✓ Docker is installed[/green]")
            
            # Check if Docker daemon is running
            daemon_result = utils.run_command(["docker", "ps"], check=False)
            if daemon_result.returncode == 0:
                console.print("[green]✓ Docker daemon is running[/green]")
            else:
                issues.append("Docker daemon is not running")
                import platform
                system = platform.system().lower()
                if system == "darwin":
                    fixes.append("Run: open -a Docker (or start Docker Desktop from Applications)")
                elif system == "linux":
                    fixes.append("Run: sudo systemctl start docker")
                elif system == "windows":
                    fixes.append("Start Docker Desktop from Start Menu or run: start docker")
                else:
                    fixes.append("Start Docker Desktop or Docker daemon")
        else:
            issues.append("Docker not working properly")
            fixes.append("Start Docker Desktop or Docker daemon")
    except FileNotFoundError:
        issues.append("Docker not installed")
        fixes.append("Install Docker Desktop from docker.com")
    
    # Check AWS credentials
    try:
        result = utils.run_command(["aws", "sts", "get-caller-identity"], check=False)
        if result.returncode == 0:
            console.print("[green]✓ AWS credentials are configured[/green]")
        else:
            issues.append("AWS credentials not configured or invalid")
            fixes.append("Run: aws configure")
    except FileNotFoundError:
        issues.append("AWS CLI not available for credential check")
        fixes.append("Install AWS CLI first")
    
    # Check AWS permissions
    if utils.check_aws_permissions():
        console.print("[green]✓ AWS permissions are sufficient[/green]")
    else:
        issues.append("Insufficient AWS permissions")
        fixes.append("Attach AdministratorAccess policy or required permissions")
    
    # Summary
    if not issues:
        console.print(Panel(
            "[green]🎉 All checks passed! Your environment is ready for deployment.[/green]",
            title="Diagnostics Complete",
            border_style="green"
        ))
    else:
        console.print(Panel(
            f"[red]Found {len(issues)} issue(s):[/red]\n\n" +
            "\n".join([f"• {issue}" for issue in issues]) +
            "\n\n[bold]Recommended fixes:[/bold]\n" +
            "\n".join([f"• {fix}" for fix in fixes]),
            title="Diagnostics Found Issues",
            border_style="red"
        ))





# Add EventBridge commands
app.add_typer(eventbridge_app, name="eventbridge", help="Manage AWS EventBridge rules")

# Add GitHub Actions commands
app.add_typer(github_actions_app, name="github-actions", help="Manage GitHub Actions workflows")

# Add Amplify commands
app.add_typer(amplify_app, name="amplify", help="Deploy React apps to AWS Amplify")


if __name__ == "__main__":
    app() 