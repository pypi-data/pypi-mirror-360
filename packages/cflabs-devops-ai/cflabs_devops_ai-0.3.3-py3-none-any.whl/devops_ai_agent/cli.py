"""CLI interface for devops-ai-agent."""

import os
import typer
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from .agent import DevOpsAIAgent

app = typer.Typer(
    name="devops-ai-agent",
    help="AI agent for natural language DevOps commands",
    add_completion=False,
)
console = Console()


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


if __name__ == "__main__":
    app() 