"""CLI interface for AWS Amplify module."""

import typer
import boto3
import subprocess
from pathlib import Path
from typing import Optional, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from datetime import datetime
import json
import time
from devops_ai_amplify import templates

app = typer.Typer(
    name="amplify",
    help="Deploy React apps to AWS Amplify from GitHub repositories",
    add_completion=False,
)
console = Console()


def get_amplify_client(region: str = "us-east-1"):
    """Get AWS Amplify client."""
    try:
        return boto3.client('amplify', region_name=region)
    except Exception as e:
        console.print(f"[red]Failed to create Amplify client: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def create_app(
    app_name: str = typer.Option(None, "--name", "-n", help="Name for your Amplify app"),
    repository: str = typer.Option(None, "--repo", "-r", help="GitHub repository URL (https://github.com/user/repo)"),
    branch: str = typer.Option("main", "--branch", "-b", help="Default branch to deploy"),
    region: str = typer.Option("us-east-1", "--region", help="AWS region"),
    access_token: Optional[str] = typer.Option(None, "--token", "-t", help="GitHub access token"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing configuration"),
):
    """Create a new Amplify app and connect it to a GitHub repository."""
    try:
        # Get or prompt for app name
        if app_name is None:
            app_name = Prompt.ask(
                "Enter a name for your Amplify app",
                default="my-react-app"
            )
        
        # Get or prompt for repository URL
        if repository is None:
            repository = Prompt.ask(
                "Enter your GitHub repository URL",
                default="https://github.com/username/my-react-app"
            )
        
        # Get or prompt for GitHub access token
        if access_token is None:
            access_token = Prompt.ask(
                "Enter your GitHub access token (or press Enter to use AWS OAuth)",
                password=True,
                default=""
            )
        
        console.print(f"[blue]Creating Amplify app '{app_name}'...[/blue]")
        
        # Create Amplify client
        amplify = get_amplify_client(region)
        
        # Create the app
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Creating Amplify app...", total=None)
            
            try:
                # Create app
                response = amplify.create_app(
                    name=app_name,
                    repository=repository,
                    platform='WEB',
                    enableBranchAutoBuild=True,
                    enableBasicAuth=False,
                    enableAutoBranchCreation=False,
                    environmentVariables={
                        'NODE_ENV': 'production'
                    }
                )
                
                app_id = response['app']['appId']
                progress.update(task, description="App created successfully!")
                
                # Create branch
                progress.add_task("Creating branch...", total=None)
                branch_response = amplify.create_branch(
                    appId=app_id,
                    branchName=branch,
                    enableAutoBuild=True,
                    enablePerformanceMode=False,
                    enablePullRequestPreview=True
                )
                
                progress.add_task("Branch created successfully!", total=None)
                
                # Generate amplify.yml if it doesn't exist
                amplify_yml_path = Path("amplify.yml")
                if not amplify_yml_path.exists() or force:
                    amplify_content = templates.AMPLIFY_YML_TEMPLATE.render(
                        app_name=app_name,
                        branch=branch
                    )
                    
                    with open(amplify_yml_path, 'w') as f:
                        f.write(amplify_content)
                    
                    console.print(f"[green]✅ Generated: {amplify_yml_path}[/green]")
                
                # Display app information
                console.print(f"\n[bold green]✅ Amplify app created successfully![/bold green]")
                console.print(f"App ID: {app_id}")
                console.print(f"App URL: https://{app_id}.amplifyapp.com")
                console.print(f"Branch: {branch}")
                console.print(f"Repository: {repository}")
                
                # Save configuration
                config = {
                    "app": {
                        "name": app_name,
                        "id": app_id,
                        "repository": repository,
                        "branch": branch
                    },
                    "aws": {
                        "region": region
                    }
                }
                
                config_path = Path("amplify-config.json")
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
                
                console.print(f"[green]✅ Configuration saved to: {config_path}[/green]")
                
                console.print(f"\n[bold blue]Next Steps:[/bold blue]")
                console.print("1. Push your React app code to the GitHub repository")
                console.print("2. The app will automatically build and deploy")
                console.print("3. Visit the app URL to see your deployed React app")
                console.print("4. Use 'devops-ai-amplify deploy-branch' to deploy specific branches")
                
            except Exception as e:
                console.print(f"[red]Failed to create Amplify app: {e}[/red]")
                raise typer.Exit(1)
                
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def deploy_branch(
    branch: str = typer.Option(..., "--branch", "-b", help="Branch to deploy"),
    app_id: Optional[str] = typer.Option(None, "--app-id", "-a", help="Amplify app ID"),
    region: str = typer.Option("us-east-1", "--region", help="AWS region"),
    wait: bool = typer.Option(True, "--wait", "-w", help="Wait for deployment to complete"),
):
    """Deploy a specific branch to Amplify."""
    try:
        # Load config if app_id not provided
        if app_id is None:
            config_path = Path("amplify-config.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                app_id = config["app"]["id"]
            else:
                app_id = Prompt.ask("Enter your Amplify app ID")
        
        console.print(f"[blue]Deploying branch '{branch}' to Amplify app '{app_id}'...[/blue]")
        
        # Create Amplify client
        amplify = get_amplify_client(region)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Starting deployment...", total=None)
            
            try:
                # Start deployment job
                response = amplify.start_job(
                    appId=app_id,
                    branchName=branch,
                    jobType='RELEASE'
                )
                
                job_id = response['jobSummary']['jobId']
                progress.update(task, description=f"Deployment started (Job ID: {job_id})")
                
                if wait:
                    # Wait for deployment to complete
                    progress.add_task("Waiting for deployment to complete...", total=None)
                    
                    while True:
                        job_status = amplify.get_job(
                            appId=app_id,
                            branchName=branch,
                            jobId=job_id
                        )
                        
                        status = job_status['job']['summary']['status']
                        
                        if status == 'SUCCEED':
                            console.print(f"[green]✅ Deployment completed successfully![/green]")
                            break
                        elif status == 'FAILED':
                            console.print(f"[red]❌ Deployment failed![/red]")
                            raise typer.Exit(1)
                        elif status in ['PENDING', 'RUNNING']:
                            time.sleep(10)  # Wait 10 seconds before checking again
                        else:
                            console.print(f"[yellow]Unknown status: {status}[/yellow]")
                            break
                
                # Get app details
                app_response = amplify.get_app(appId=app_id)
                app_name = app_response['app']['name']
                
                console.print(f"\n[bold green]Deployment Summary:[/bold green]")
                console.print(f"App: {app_name}")
                console.print(f"Branch: {branch}")
                console.print(f"App URL: https://{app_id}.amplifyapp.com")
                console.print(f"Branch URL: https://{branch}.{app_id}.amplifyapp.com")
                
            except Exception as e:
                console.print(f"[red]Failed to deploy branch: {e}[/red]")
                raise typer.Exit(1)
                
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def list_apps(
    region: str = typer.Option("us-east-1", "--region", help="AWS region"),
):
    """List all Amplify apps in the specified region."""
    try:
        console.print(f"[blue]Listing Amplify apps in {region}...[/blue]")
        
        # Create Amplify client
        amplify = get_amplify_client(region)
        
        # List apps
        response = amplify.list_apps()
        
        if not response['apps']:
            console.print("[yellow]No Amplify apps found in this region.[/yellow]")
            return
        
        # Create table
        table = Table(title="Amplify Apps")
        table.add_column("App Name", style="cyan")
        table.add_column("App ID", style="green")
        table.add_column("Repository", style="blue")
        table.add_column("Platform", style="yellow")
        table.add_column("Created", style="magenta")
        
        for app in response['apps']:
            table.add_row(
                app['name'],
                app['appId'],
                app.get('repository', 'N/A'),
                app.get('platform', 'N/A'),
                app['createTime'].strftime('%Y-%m-%d %H:%M:%S')
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def list_branches(
    app_id: str = typer.Option(..., "--app-id", "-a", help="Amplify app ID"),
    region: str = typer.Option("us-east-1", "--region", help="AWS region"),
):
    """List all branches for an Amplify app."""
    try:
        console.print(f"[blue]Listing branches for app '{app_id}'...[/blue]")
        
        # Create Amplify client
        amplify = get_amplify_client(region)
        
        # List branches
        response = amplify.list_branches(appId=app_id)
        
        if not response['branches']:
            console.print("[yellow]No branches found for this app.[/yellow]")
            return
        
        # Create table
        table = Table(title=f"Branches for App {app_id}")
        table.add_column("Branch Name", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Auto Build", style="yellow")
        table.add_column("Last Deploy", style="magenta")
        
        for branch in response['branches']:
            status = branch.get('stage', 'N/A')
            auto_build = "Yes" if branch.get('enableAutoBuild', False) else "No"
            last_deploy = branch.get('lastDeployTime', 'N/A')
            if last_deploy != 'N/A':
                last_deploy = last_deploy.strftime('%Y-%m-%d %H:%M:%S')
            
            table.add_row(
                branch['branchName'],
                status,
                auto_build,
                last_deploy
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def delete_app(
    app_id: str = typer.Option(..., "--app-id", "-a", help="Amplify app ID"),
    region: str = typer.Option("us-east-1", "--region", help="AWS region"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Delete an Amplify app."""
    try:
        if not force:
            if not Confirm.ask(f"Are you sure you want to delete app '{app_id}'?"):
                console.print("[yellow]Deletion cancelled.[/yellow]")
                raise typer.Exit(0)
        
        console.print(f"[blue]Deleting Amplify app '{app_id}'...[/blue]")
        
        # Create Amplify client
        amplify = get_amplify_client(region)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Deleting app...", total=None)
            
            try:
                # Delete app
                amplify.delete_app(appId=app_id)
                
                progress.update(task, description="App deleted successfully!")
                console.print(f"[green]✅ Amplify app '{app_id}' deleted successfully![/green]")
                
                # Remove config file if it exists
                config_path = Path("amplify-config.json")
                if config_path.exists():
                    config_path.unlink()
                    console.print(f"[green]✅ Removed configuration file[/green]")
                
            except Exception as e:
                console.print(f"[red]Failed to delete app: {e}[/red]")
                raise typer.Exit(1)
                
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def status(
    app_id: Optional[str] = typer.Option(None, "--app-id", "-a", help="Amplify app ID"),
    region: str = typer.Option("us-east-1", "--region", help="AWS region"),
):
    """Show status of Amplify apps."""
    try:
        # Load config if app_id not provided
        if app_id is None:
            config_path = Path("amplify-config.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                app_id = config["app"]["id"]
            else:
                console.print("[red]No app ID provided and no config file found.[/red]")
                raise typer.Exit(1)
        
        console.print(f"[blue]Checking status for app '{app_id}'...[/blue]")
        
        # Create Amplify client
        amplify = get_amplify_client(region)
        
        try:
            # Get app details
            app_response = amplify.get_app(appId=app_id)
            app = app_response['app']
            
            # Get branches
            branches_response = amplify.list_branches(appId=app_id)
            
            console.print(f"\n[bold green]App Status:[/bold green]")
            console.print(f"Name: {app['name']}")
            console.print(f"ID: {app['appId']}")
            console.print(f"Repository: {app.get('repository', 'N/A')}")
            console.print(f"Platform: {app.get('platform', 'N/A')}")
            console.print(f"Created: {app['createTime'].strftime('%Y-%m-%d %H:%M:%S')}")
            
            if branches_response['branches']:
                console.print(f"\n[bold blue]Branches:[/bold blue]")
                for branch in branches_response['branches']:
                    status = branch.get('stage', 'N/A')
                    console.print(f"  • {branch['branchName']} ({status})")
            
        except Exception as e:
            console.print(f"[red]Failed to get app status: {e}[/red]")
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def create_branch(
    branch: str = typer.Option(..., "--branch", "-b", help="Branch name to create"),
    app_id: Optional[str] = typer.Option(None, "--app-id", "-a", help="Amplify app ID"),
    region: str = typer.Option("us-east-1", "--region", help="AWS region"),
    enable_auto_build: bool = typer.Option(True, "--auto-build", help="Enable auto build for branch"),
    enable_pull_request_preview: bool = typer.Option(True, "--pr-preview", help="Enable pull request preview"),
):
    """Create a new branch for an Amplify app."""
    try:
        # Load config if app_id not provided
        if app_id is None:
            config_path = Path("amplify-config.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                app_id = config["app"]["id"]
            else:
                app_id = Prompt.ask("Enter your Amplify app ID")
        
        console.print(f"[blue]Creating branch '{branch}' for app '{app_id}'...[/blue]")
        
        # Create Amplify client
        amplify = get_amplify_client(region)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Creating branch...", total=None)
            
            try:
                # Create branch
                response = amplify.create_branch(
                    appId=app_id,
                    branchName=branch,
                    enableAutoBuild=enable_auto_build,
                    enablePerformanceMode=False,
                    enablePullRequestPreview=enable_pull_request_preview
                )
                
                progress.update(task, description="Branch created successfully!")
                console.print(f"[green]✅ Branch '{branch}' created successfully![/green]")
                console.print(f"Branch URL: https://{branch}.{app_id}.amplifyapp.com")
                
            except Exception as e:
                console.print(f"[red]Failed to create branch: {e}[/red]")
                raise typer.Exit(1)
                
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def delete_branch(
    branch: str = typer.Option(..., "--branch", "-b", help="Branch name to delete"),
    app_id: Optional[str] = typer.Option(None, "--app-id", "-a", help="Amplify app ID"),
    region: str = typer.Option("us-east-1", "--region", help="AWS region"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Delete a branch from an Amplify app."""
    try:
        # Load config if app_id not provided
        if app_id is None:
            config_path = Path("amplify-config.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                app_id = config["app"]["id"]
            else:
                app_id = Prompt.ask("Enter your Amplify app ID")
        
        if not force:
            if not Confirm.ask(f"Are you sure you want to delete branch '{branch}'?"):
                console.print("[yellow]Branch deletion cancelled.[/yellow]")
                raise typer.Exit(0)
        
        console.print(f"[blue]Deleting branch '{branch}' from app '{app_id}'...[/blue]")
        
        # Create Amplify client
        amplify = get_amplify_client(region)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Deleting branch...", total=None)
            
            try:
                # Delete branch
                amplify.delete_branch(
                    appId=app_id,
                    branchName=branch
                )
                
                progress.update(task, description="Branch deleted successfully!")
                console.print(f"[green]✅ Branch '{branch}' deleted successfully![/green]")
                
            except Exception as e:
                console.print(f"[red]Failed to delete branch: {e}[/red]")
                raise typer.Exit(1)
                
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def configure_app(
    app_id: Optional[str] = typer.Option(None, "--app-id", "-a", help="Amplify app ID"),
    region: str = typer.Option("us-east-1", "--region", help="AWS region"),
    framework: str = typer.Option("react", "--framework", "-f", help="Framework (react, nextjs, vue, angular)"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files"),
):
    """Configure Amplify app with framework-specific settings."""
    try:
        # Load config if app_id not provided
        if app_id is None:
            config_path = Path("amplify-config.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                app_id = config["app"]["id"]
                app_name = config["app"]["name"]
            else:
                app_id = Prompt.ask("Enter your Amplify app ID")
                app_name = Prompt.ask("Enter your app name")
        else:
            app_name = Prompt.ask("Enter your app name")
        
        console.print(f"[blue]Configuring Amplify app '{app_name}' with {framework} settings...[/blue]")
        
        # Generate framework-specific amplify.yml
        if framework == "react":
            amplify_content = templates.REACT_AMPLIFY_YML_TEMPLATE.render(
                app_name=app_name
            )
        elif framework == "nextjs":
            amplify_content = templates.NEXTJS_AMPLIFY_YML_TEMPLATE.render(
                app_name=app_name
            )
        elif framework == "vue":
            amplify_content = templates.VUE_AMPLIFY_YML_TEMPLATE.render(
                app_name=app_name
            )
        elif framework == "angular":
            amplify_content = templates.ANGULAR_AMPLIFY_YML_TEMPLATE.render(
                app_name=app_name
            )
        else:
            console.print(f"[red]Unsupported framework: {framework}[/red]")
            raise typer.Exit(1)
        
        # Write amplify.yml
        amplify_yml_path = Path("amplify.yml")
        if amplify_yml_path.exists() and not force:
            if not Confirm.ask("amplify.yml already exists. Overwrite?"):
                console.print("[yellow]Skipping amplify.yml generation.[/yellow]")
            else:
                with open(amplify_yml_path, 'w') as f:
                    f.write(amplify_content)
                console.print(f"[green]✅ Generated: {amplify_yml_path}[/green]")
        else:
            with open(amplify_yml_path, 'w') as f:
                f.write(amplify_content)
            console.print(f"[green]✅ Generated: {amplify_yml_path}[/green]")
        
        # Generate redirects for SPA routing
        redirects_path = Path("public/_redirects")
        redirects_path.parent.mkdir(exist_ok=True)
        
        if not redirects_path.exists() or force:
            redirects_content = templates.REDIRECTS_TEMPLATE.render()
            with open(redirects_path, 'w') as f:
                f.write(redirects_content)
            console.print(f"[green]✅ Generated: {redirects_path}[/green]")
        
        # Generate .gitignore if it doesn't exist
        gitignore_path = Path(".gitignore")
        if not gitignore_path.exists():
            gitignore_content = templates.GITIGNORE_TEMPLATE.render()
            with open(gitignore_path, 'w') as f:
                f.write(gitignore_content)
            console.print(f"[green]✅ Generated: {gitignore_path}[/green]")
        
        console.print(f"\n[bold green]✅ Amplify app configured successfully![/bold green]")
        console.print(f"Framework: {framework}")
        console.print(f"App ID: {app_id}")
        console.print(f"App URL: https://{app_id}.amplifyapp.com")
        
        console.print(f"\n[bold blue]Next Steps:[/bold blue]")
        console.print("1. Push your code to trigger a build")
        console.print("2. Check the Amplify console for build status")
        console.print("3. Visit the app URL to see your deployed app")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app() 