"""
CLI interface for EventBridge management.
"""

import typer
import json
import logging
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from .core import EventBridgeManager
from .cron_converter import CronConverter

app = typer.Typer(
    name="eventbridge",
    help="Manage AWS EventBridge rules from natural language descriptions",
    add_completion=False
)

console = Console()
logger = logging.getLogger(__name__)


@app.command()
def create(
    rule_name: str = typer.Argument(..., help="Name of the EventBridge rule"),
    description: str = typer.Argument(..., help="Natural language description of the schedule (e.g., 'daily at 9am', 'every monday at 2pm')"),
    target_arn: Optional[str] = typer.Argument(None, help="ARN of the target (Lambda, SQS, etc.) - optional"),
    region: str = typer.Option("us-east-1", "--region", "-r", help="AWS region"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="AWS profile name"),
    target_id: Optional[str] = typer.Option(None, "--target-id", "-t", help="Target ID (optional)"),
    output: str = typer.Option("table", "--output", "-o", help="Output format: table, json"),
):
    """Create an EventBridge rule from natural language description."""
    try:
        manager = EventBridgeManager(region_name=region, profile_name=profile)
        
        # Show what we're about to do
        cron_converter = CronConverter()
        cron_expression = cron_converter.text_to_cron(description)
        
        # Prepare the panel content
        panel_content = f"[bold blue]Creating EventBridge Rule[/bold blue]\n"
        panel_content += f"Rule Name: [bold]{rule_name}[/bold]\n"
        panel_content += f"Description: [italic]{description}[/italic]\n"
        panel_content += f"Cron Expression: [code]{cron_expression}[/code]\n"
        
        if target_arn:
            panel_content += f"Target ARN: [dim]{target_arn}[/dim]"
        else:
            panel_content += f"Target ARN: [yellow]None (rule will be created without target)[/yellow]"
        
        console.print(Panel(
            panel_content,
            title="EventBridge Rule Creation",
            border_style="blue"
        ))
        
        # Create the rule
        # Handle the case where target_arn is "None" string or None
        actual_target_arn = None if (target_arn is None or target_arn == "None" or target_arn == "") else target_arn
        
        result = manager.create_rule_from_text(
            rule_name=rule_name,
            description=description,
            target_arn=actual_target_arn,
            target_id=target_id
        )
        
        if output == "json":
            console.print(json.dumps(result, indent=2))
        else:
            table = Table(title="EventBridge Rule Created")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            
            for key, value in result.items():
                table.add_row(key.replace("_", " ").title(), str(value))
            
            console.print(table)
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(1)


@app.command()
def list(
    prefix: Optional[str] = typer.Option(None, "--prefix", "-p", help="Filter rules by name prefix"),
    region: str = typer.Option("ap-south-1", "--region", "-r", help="AWS region"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="AWS profile name"),
    output: str = typer.Option("table", "--output", "-o", help="Output format: table, json"),
):
    """List EventBridge rules."""
    try:
        manager = EventBridgeManager(region_name=region, profile_name=profile)
        rules = manager.list_rules(name_prefix=prefix)
        
        if output == "json":
            console.print(json.dumps(rules, indent=2))
        else:
            if not rules:
                console.print("[yellow]No rules found[/yellow]")
                return
            
            table = Table(title="EventBridge Rules")
            table.add_column("Name", style="cyan")
            table.add_column("Schedule", style="green")
            table.add_column("State", style="yellow")
            table.add_column("Description", style="dim")
            
            for rule in rules:
                state_color = "green" if rule["state"] == "ENABLED" else "red"
                table.add_row(
                    rule["name"],
                    rule["schedule"] or "N/A",
                    f"[{state_color}]{rule['state']}[/{state_color}]",
                    rule["description"] or "N/A"
                )
            
            console.print(table)
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(1)


@app.command()
def delete(
    rule_name: str = typer.Argument(..., help="Name of the rule to delete"),
    region: str = typer.Option("ap-south-1", "--region", "-r", help="AWS region"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="AWS profile name"),
    force: bool = typer.Option(False, "--force", "-f", help="Force deletion by removing targets first"),
    output: str = typer.Option("table", "--output", "-o", help="Output format: table, json"),
):
    """Delete an EventBridge rule."""
    try:
        manager = EventBridgeManager(region_name=region, profile_name=profile)
        
        # Confirm deletion
        if not force:
            console.print(f"[yellow]Are you sure you want to delete rule '{rule_name}'?[/yellow]")
            if not typer.confirm("Continue?"):
                console.print("[blue]Operation cancelled[/blue]")
                return
        
        result = manager.delete_rule(rule_name=rule_name, force=force)
        
        if output == "json":
            console.print(json.dumps(result, indent=2))
        else:
            console.print(f"[bold green]✓[/bold green] Rule '{rule_name}' deleted successfully")
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(1)


@app.command()
def show(
    rule_name: str = typer.Argument(..., help="Name of the rule to show"),
    region: str = typer.Option("us-east-1", "--region", "-r", help="AWS region"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="AWS profile name"),
    openai_api_key: Optional[str] = typer.Option(None, "--openai-key", "-k", help="OpenAI API key for enhanced natural language processing"),
    output: str = typer.Option("table", "--output", "-o", help="Output format: table, json"),
):
    """Show detailed information about an EventBridge rule."""
    try:
        manager = EventBridgeManager(region_name=region, profile_name=profile, openai_api_key=openai_api_key)
        rule_details = manager.get_rule_details(rule_name)
        
        if output == "json":
            console.print(json.dumps(rule_details, indent=2))
        else:
            table = Table(title=f"EventBridge Rule: {rule_name}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            
            for key, value in rule_details.items():
                if key == "targets":
                    if value:
                        target_info = "\n".join([f"• {t.get('Id', 'N/A')}: {t.get('Arn', 'N/A')}" for t in value])
                        table.add_row("Targets", target_info)
                    else:
                        table.add_row("Targets", "None")
                else:
                    table.add_row(key.replace("_", " ").title(), str(value))
            
            console.print(table)
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(1)


@app.command()
def update(
    rule_name: str = typer.Argument(..., help="Name of the rule to update"),
    description: str = typer.Argument(..., help="New natural language description of the schedule"),
    region: str = typer.Option("us-east-1", "--region", "-r", help="AWS region"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="AWS profile name"),
    output: str = typer.Option("table", "--output", "-o", help="Output format: table, json"),
):
    """Update an EventBridge rule's schedule from natural language description."""
    try:
        manager = EventBridgeManager(region_name=region, profile_name=profile)
        
        # Show what we're about to do
        cron_converter = CronConverter()
        cron_expression = cron_converter.text_to_cron(description)
        
        console.print(Panel(
            f"[bold blue]Updating EventBridge Rule[/bold blue]\n"
            f"Rule Name: [bold]{rule_name}[/bold]\n"
            f"New Description: [italic]{description}[/italic]\n"
            f"New Cron Expression: [code]{cron_expression}[/code]",
            title="EventBridge Rule Update",
            border_style="blue"
        ))
        
        result = manager.update_rule_schedule(rule_name=rule_name, description=description)
        
        if output == "json":
            console.print(json.dumps(result, indent=2))
        else:
            table = Table(title="EventBridge Rule Updated")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            
            for key, value in result.items():
                table.add_row(key.replace("_", " ").title(), str(value))
            
            console.print(table)
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(1)


@app.command()
def convert(
    description: str = typer.Argument(..., help="Natural language description to convert to cron"),
    output: str = typer.Option("table", "--output", "-o", help="Output format: table, json"),
):
    """Convert natural language description to cron expression."""
    try:
        cron_converter = CronConverter()
        cron_expression = cron_converter.text_to_cron(description)
        
        if output == "json":
            result = {
                "description": description,
                "cron_expression": cron_expression,
                "is_valid": cron_converter.validate_cron(cron_expression)
            }
            console.print(json.dumps(result, indent=2))
        else:
            table = Table(title="Cron Expression Conversion")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Description", description)
            table.add_row("Cron Expression", cron_expression)
            table.add_row("Valid", "✓" if cron_converter.validate_cron(cron_expression) else "✗")
            
            console.print(table)
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(1)


@app.command()
def examples():
    """Show examples of natural language descriptions."""
    examples_data = [
        ("daily at 9am", "cron(0 9 * * ? *)"),
        ("every monday at 2pm", "cron(0 14 ? * 1 *)"),
        ("weekly on friday at 5pm", "cron(0 17 ? * 5 *)"),
        ("monthly on the 15th", "cron(0 0 15 * ? *)"),
        ("every 30 minutes", "rate(30 minutes)"),
        ("every 2 hours", "rate(2 hours)"),
        ("every 1 day", "rate(1 day)"),
        ("weekdays at 8am", "cron(0 8 ? * 1-5 *)"),
        ("weekends at 10am", "cron(0 10 ? * 0,6 *)"),
        ("yearly on january 1st", "cron(0 0 1 1 ? *)"),
        ("every 3 days", "rate(3 days)"),
    ]
    
    table = Table(title="Natural Language to Cron Examples")
    table.add_column("Description", style="cyan")
    table.add_column("Cron Expression", style="green")
    
    for description, cron in examples_data:
        table.add_row(description, cron)
    
    console.print(table)
    console.print("\n[dim]Use 'convert' command to test your own descriptions[/dim]")


if __name__ == "__main__":
    app() 