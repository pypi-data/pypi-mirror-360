import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm
from devops_ai_serverless import utils
from devops_ai_github_actions import templates

app = typer.Typer(
    name="devops-ai-github-actions",
    help="GitHub Actions utilities for devops-ai",
    add_completion=False,
)
console = Console()

@app.command()
def create_workflow(
    lambda_name: str = typer.Option(None, "--name", "-n", help="Name for your Lambda function"),
    region: str = typer.Option("us-east-1", "--region", "-r", help="AWS region"),
    stack_name: Optional[str] = typer.Option(None, "--stack-name", "-s", help="Name of the CloudFormation stack"),
    ecr_repository: Optional[str] = typer.Option(None, "--ecr-repo", help="ECR repository name"),
    config_path: Optional[str] = typer.Option(None, "--config", "-c", help="Path to config file"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing workflow file"),
):
    """Create GitHub Actions workflow for CI/CD deployment."""
    try:
        project_root = utils.get_project_root()
        # Load config if provided
        config = None
        if config_path and Path(config_path).exists():
            config = utils.load_config(config_path)
        # Get or prompt for lambda name
        if lambda_name is None:
            if config and "deployment" in config:
                lambda_name = config["deployment"]["lambda_name"]
            else:
                lambda_name = Prompt.ask(
                    "Enter a name for your Lambda function",
                    default=f"{project_root.name}-flask-app"
                )
        # Generate stack name from lambda name if not provided
        if stack_name is None:
            stack_name = f"{lambda_name}-stack"
        # Generate ECR repository name if not provided
        if ecr_repository is None:
            ecr_repository = f"{lambda_name}-repo"
        # Create .github/workflows directory
        workflows_dir = project_root / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        # Generate workflow file
        workflow_path = workflows_dir / "deploy.yml"
        if workflow_path.exists() and not force:
            if not Confirm.ask("Workflow file already exists. Overwrite?"):
                console.print("[yellow]Workflow creation cancelled.[/yellow]")
                raise typer.Exit(0)
        # Generate workflow content
        workflow_content = templates.GITHUB_ACTIONS_TEMPLATE.render(
            region=region,
            stack_name=stack_name,
            lambda_name=lambda_name,
            ecr_repository=ecr_repository
        )
        # Write workflow file
        with open(workflow_path, 'w') as f:
            f.write(workflow_content)
        console.print(f"[green]✅ GitHub Actions workflow created: {workflow_path}[/green]")
        # Create or update .gitignore to exclude deployment artifacts
        gitignore_path = project_root / ".gitignore"
        gitignore_entries = [
            "# devops-ai deployment artifacts",
            "cflabs-config.yaml",
            "template.yaml",
            ".aws-sam/",
            "Dockerfile",
            "lambda_entry.py",
            "samconfig.toml"
        ]
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                existing_content = f.read()
            # Add entries if they don't exist
            for entry in gitignore_entries:
                if entry not in existing_content:
                    with open(gitignore_path, 'a') as f:
                        f.write(f"\n{entry}")
        else:
            with open(gitignore_path, 'w') as f:
                f.write("\n".join(gitignore_entries))
        # Display next steps
        console.print("\n[bold blue]Next Steps:[/bold blue]")
        console.print("1. Add AWS credentials to your GitHub repository secrets:")
        console.print("   - AWS_ACCESS_KEY_ID")
        console.print("   - AWS_SECRET_ACCESS_KEY")
        console.print("2. Ensure your AWS user has the necessary permissions:")
        console.print("   - ECR: Create/update repositories")
        console.print("   - CloudFormation: Create/update stacks")
        console.print("   - Lambda: Create/update functions")
        console.print("   - API Gateway: Create/update APIs")
        console.print("   - S3: Create/update buckets")
        console.print("3. Push your code to trigger the workflow")
        console.print("\n[bold green]Your Flask app will be automatically deployed on every push to main/master![bold green]")
    except Exception as e:
        utils.print_error(f"Failed to create workflow: {str(e)}")
        raise typer.Exit(1) 