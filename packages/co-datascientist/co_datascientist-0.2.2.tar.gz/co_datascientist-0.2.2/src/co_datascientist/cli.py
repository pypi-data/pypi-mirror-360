import asyncio
import logging
from pathlib import Path

import click
from yaspin import yaspin

from co_datascientist.workflow_runner import workflow_runner
from . import co_datascientist_api, mcp_local_server
from .settings import settings

logging.basicConfig(level=settings.log_level)
logging.info(f"settings: {settings.model_dump()}")


def print_section_header(title: str, emoji: str = ""):
    """Print a section header with consistent formatting"""
    print(f"\n{emoji} {title}" if emoji else f"\n{title}")
    print("─" * (len(title) + (3 if emoji else 0)))


def print_success(message: str):
    """Print a success message with consistent formatting"""
    print(f"✅ {message}")


def print_info(message: str):
    """Print an info message with consistent formatting"""
    print(f"ℹ️  {message}")


def print_warning(message: str):
    """Print a warning message with consistent formatting"""
    print(f"⚠️  {message}")


def print_error(message: str):
    """Print an error message with consistent formatting"""
    print(f"❌ {message}")


@click.group()
@click.option('--reset-token', is_flag=True, help='Reset the API token')
@click.option('--reset-openai-key', is_flag=True, help='Reset the OpenAI API key')
def main(reset_token: bool, reset_openai_key: bool):
    """Welcome to CoDatascientist CLI!"""
    print_section_header("Co-DataScientist CLI", "🚀")
    
    if reset_token:
        settings.delete_api_key()
        print()
    
    if reset_openai_key:
        settings.delete_openai_key()
        print()
    
    settings.get_api_key()
    
    # Check for existing OpenAI key without prompting (users can add it with 'openai_key' command)
    if not reset_openai_key:
        settings.get_openai_key(prompt_if_missing=False)

    try:
        with yaspin(text=f"Connecting to server at {settings.backend_url}...", color="cyan") as spinner:
            response = asyncio.run(co_datascientist_api.test_connection())
            spinner.ok("✅ ")
        
        print_success(f"Connected to server: {response}")
        print()
    except Exception as e:
        print_error(f"Connection failed: {e}")
        print()
        print_info("Make sure your token is correct. Use --reset-token to reset it.")
        print()
        exit(1)


@main.command()
def mcp_server():
    """Start the MCP server which allows agents to use CoDatascientist"""
    print_section_header("MCP Server", "🔌")
    print_info("Starting MCP server... Press Ctrl+C to exit.")
    print()
    asyncio.run(mcp_local_server.run_mcp_server())


@main.command()
@click.option('--script-path', required=True, type=click.Path(), help='Absolute path to the python code to improve')
@click.option('--python-path', required=True, type=click.Path(), default="python", show_default=True,
              help='Path to the python interpreter to use')
@click.option('--best-only', is_flag=True, help='Only show best KPI updates (quiet mode)')
@click.option('--checkpoint-interval', type=int, default=10, show_default=True,
              help='Save checkpoint every N iterations when using --best-only')
@click.option('--debug', is_flag=True, help='Show detailed logs (default: minimal output)')
def run(script_path, python_path, best_only, checkpoint_interval, debug):
    """Process a file"""
    print_section_header("Code Processing", "🔬")
    print_info(f"Script: {script_path}")
    print_info(f"Python: {python_path}")
    print()
    
    if not Path(script_path).exists():
        print_error("Python code file path doesn't exist.")
        return

    if not Path(script_path).is_absolute():
        print_error("Python code file path must be absolute.")
        return

    if python_path != "python":
        if not Path(python_path).exists():
            print_error("Python interpreter executable path doesn't exist.")
            return

        if not Path(python_path).is_absolute():
            print_error("Python interpreter executable path must be absolute or 'python'.")
            return

    code = Path(script_path).read_text()
    project_path = Path(script_path).parent
    
    print_section_header("Workflow Execution", "⚡")
    if best_only:
        print()
    
    if not debug:
        print()
    
    # Batch mode removed – always sequential execution
    
    with yaspin(text="Initializing workflow...", color="magenta") as spinner:
        try:
            asyncio.run(workflow_runner.run_workflow(
                code, python_path, project_path, spinner,
                best_only, checkpoint_interval, 1, None, debug
            ))
            spinner.stop()  # Stop spinner without success symbol
        except Exception as e:
            spinner.fail("❌ ")
            raise
    
    print()


@main.command()
@click.option('--detailed', is_flag=True, help='Show detailed cost breakdown including all workflows and model calls')
def costs(detailed):
    """Show your usage costs and token consumption"""
    try:
        # Get usage status with remaining money info
        with yaspin(text="Fetching usage data...", color="blue") as spinner:
            usage_status = asyncio.run(co_datascientist_api.get_user_usage_status())
            spinner.ok("✅ ")
        
        if detailed:
            with yaspin(text="Loading detailed breakdown...", color="green") as spinner:
                response = asyncio.run(co_datascientist_api.get_user_costs())
                spinner.ok("✅ ")
            
            print_section_header("Usage Details", "💰")
            print(f"Total Cost: ${response['total_cost_usd']:.8f}")
            print(f"Usage Limit: ${usage_status['limit_usd']:.2f}")
            print(f"Remaining: ${usage_status['remaining_usd']:.2f}")
            print(f"Usage: {usage_status['usage_percentage']:.1f}% of limit")
            
            if usage_status['is_blocked']:
                print_error("BLOCKED (limit exceeded)")
            elif usage_status['usage_percentage'] >= 80:
                print_warning(f"Approaching limit ({usage_status['usage_percentage']:.1f}%)")
            else:
                print_success(f"Active ({usage_status['usage_percentage']:.1f}% used)")
            
            print(f"Total Tokens: {response['total_tokens']:,} ({response['total_input_tokens']:,} input + {response['total_output_tokens']:,} output)")
            print(f"Workflows: {response['workflows_count']}")
            if response.get('last_updated'):
                print(f"Last Updated: {response['last_updated']}")
            
            if response['workflows']:
                print("\n📊 Workflow Breakdown:")
                for workflow_id, workflow_data in response['workflows'].items():
                    print(f"  {workflow_id[:8]}... | ${workflow_data['cost']:.8f} | {workflow_data['input_tokens'] + workflow_data['output_tokens']:,} tokens")
                    if len(workflow_data['model_calls']) > 0:
                        print(f"    Model calls: {len(workflow_data['model_calls'])}")
                        for call in workflow_data['model_calls'][-3:]:  # Show last 3 calls
                            print(f"      • {call['model']}: ${call['cost']:.8f} ({call['input_tokens']}+{call['output_tokens']} tokens)")
                        if len(workflow_data['model_calls']) > 3:
                            print(f"      ... and {len(workflow_data['model_calls']) - 3} more calls")
        else:
            with yaspin(text="Loading usage summary...", color="green") as spinner:
                response = asyncio.run(co_datascientist_api.get_user_costs_summary())
                spinner.ok("✅ ")
            
            print_section_header("Usage Summary", "💰")
            print(f"Total Cost: ${response['total_cost_usd']:.8f}")
            print(f"Usage Limit: ${usage_status['limit_usd']:.2f}")
            print(f"Remaining: ${usage_status['remaining_usd']:.2f} ({usage_status['usage_percentage']:.1f}% used)")
            
            # Status indicator
            if usage_status['is_blocked']:
                print_error("BLOCKED - Free tokens exhausted!")
                print(f"   You've used ${usage_status['current_usage_usd']:.2f} of your ${usage_status['limit_usd']:.2f} limit.")
            elif usage_status['usage_percentage'] >= 80:
                print_warning(f"Approaching limit - {usage_status['usage_percentage']:.1f}% used")
            else:
                print_success(f"Active - {usage_status['usage_percentage']:.1f}% of limit used")
            
            print(f"Total Tokens: {response['total_tokens']:,}")
            print(f"Workflows Completed: {response['workflows_completed']}")
            if response.get('last_updated'):
                print(f"Last Updated: {response['last_updated']}")
            
            print("\n💡 Use '--detailed' flag for full breakdown")
        
        print()
    except Exception as e:
        print_error(f"Error getting costs: {e}")
        # If the new endpoint isn't available, fall back to old behavior
        try:
            if detailed:
                response = asyncio.run(co_datascientist_api.get_user_costs())
                print_section_header("Usage Details", "💰")
                print(f"Total Cost: ${response['total_cost_usd']:.8f}")
                print(f"Total Tokens: {response['total_tokens']:,}")
                print(f"Workflows: {response['workflows_count']}")
            else:
                response = asyncio.run(co_datascientist_api.get_user_costs_summary())
                print_section_header("Usage Summary", "💰")
                print(f"Total Cost: ${response['total_cost_usd']:.8f}")
                print(f"Total Tokens: {response['total_tokens']:,}")
                print(f"Workflows Completed: {response['workflows_completed']}")
            print()
        except Exception as fallback_error:
            print_error(f"Error getting basic costs: {fallback_error}")
            print()


@main.command()
def status():
    """Quick check of your usage status and remaining balance"""
    try:
        with yaspin(text="Checking status...", color="yellow") as spinner:
            usage_status = asyncio.run(co_datascientist_api.get_user_usage_status())
            spinner.ok("✅ ")
        
        print_section_header("Usage Status", "🔍")
        print(f"Used: ${usage_status['current_usage_usd']:.2f} / ${usage_status['limit_usd']:.2f}")
        print(f"Remaining: ${usage_status['remaining_usd']:.2f}")
        
        # Show OpenAI key status
        openai_key = settings.get_openai_key(prompt_if_missing=False)
        if openai_key:
            print("🔑 Using your OpenAI account (unlimited usage)")
        else:
            print("🆓 Using TropiFlow's free tier")
        
        # Progress bar
        percentage = usage_status['usage_percentage']
        bar_width = 20
        filled = int(bar_width * percentage / 100)
        bar = "█" * filled + "░" * (bar_width - filled)
        print(f"Progress: [{bar}] {percentage:.1f}%")
        
        # Status with emoji
        if usage_status['is_blocked']:
            print_error("BLOCKED - Free tokens exhausted! Contact support or wait for reset.")
            if not openai_key:
                print_info("Add your OpenAI key with --reset-openai-key for unlimited usage")
        elif percentage >= 90:
            print_error(f"CRITICAL - Only ${usage_status['remaining_usd']:.2f} remaining!")
            if not openai_key:
                print_info("Add your OpenAI key with --reset-openai-key for unlimited usage")
        elif percentage >= 80:
            print_warning(f"WARNING - Approaching limit ({percentage:.1f}% used)")
        elif percentage >= 50:
            print("🟦 MODERATE - {percentage:.1f}% of limit used")
        else:
            print("🟩 GOOD - Plenty of free tokens remaining")
        
        print("\n💡 Use 'costs' command for detailed breakdown")
        print()
        
    except Exception as e:
        print_error(f"Error getting status: {e}")
        print()


@main.command()
@click.option('--remove', is_flag=True, help='Remove stored OpenAI key')
def openai_key(remove):
    """Manage your OpenAI API key for unlimited usage"""
    print_section_header("OpenAI Key Management", "🔑")
    
    if remove:
        settings.delete_openai_key()
        print()
    else:
        current_key = settings.get_openai_key(prompt_if_missing=False)
        if current_key:
            print_success("OpenAI key is currently configured.")
            print_info("Your requests use your OpenAI account for unlimited usage.")
            print_info("Use '--remove' flag to switch back to TropiFlow's free tier.")
        else:
            print_info("No OpenAI key configured. Using TropiFlow's free tier.")
            print_info("Add your key for unlimited usage:")
            print()
            settings.get_openai_key(prompt_if_missing=True)
        print()


if __name__ == "__main__":
    main()
