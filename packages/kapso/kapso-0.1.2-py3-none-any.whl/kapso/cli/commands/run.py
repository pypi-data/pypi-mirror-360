"""
Implementation of the run command for the Kapso CLI.
"""
import os
import sys
import time
import logging
import asyncio

import dotenv
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, TypedDict, Tuple
import uuid
import typer
import inquirer
import yaml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

from kapso.cli.services.auth_service import AuthService
from kapso.cli.services.api_service import ApiManager, GenerationLimitError
from kapso.cli.utils.project_config import get_project_id, ensure_project_api_key
from kapso.cli.utils.agent import compile_agent, load_agent_graph
from kapso.runner.runners.test_chat import TestChatRunner
from kapso.runner.schemas import AgentChatRequest, MessagePayload
from kapso.runner.channels.whatsapp import WhatsAppAdapter
from kapso.runner.channels.factory import register_adapter
from kapso.runner.channels.models import MessageChannelType


dotenv.load_dotenv()

# Configure logger
logger = logging.getLogger('kapso.cli.commands.run')

# Type definitions for API responses
class AgentTestChatMessage(TypedDict):
    content: str
    role: str


class AgentSnapshotResponse(TypedDict):
    data: Dict[str, Any]


class AgentSnapshot(TypedDict):
    agent_id: str
    created_at: str
    graph: Dict[str, Any]
    id: str
    name: str
    updated_at: str


# Chat client interface
class ChatClient(ABC):
    """Abstract interface for chat clients (local or cloud)"""

    @abstractmethod
    async def initialize(self, spinner: Progress, spinner_task: Any) -> None:
        """Initialize the chat client"""
        pass

    @abstractmethod
    async def process_message(self, message: str) -> Dict[str, Any]:
        """Process a user message and return the response"""
        pass

    @abstractmethod
    def display_response(self, response: Dict[str, Any]) -> None:
        """Display the response from the agent"""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Clean up resources when done"""
        pass


# Local chat client implementation
class LocalChatClient(ChatClient):
    """Client for local chat execution"""

    def __init__(self, debug: bool, agent_config: Dict[str, Any], local_graph: Dict[str, Any]):
        self.debug = debug
        self.agent_config = agent_config
        self.local_graph = local_graph
        self.thread_id = f"local_{str(uuid.uuid4())}"
        self.test_chat_runner = TestChatRunner(debug=debug)
        self.loop = None
        self.console = Console()
        self.last_displayed_message_index = -1
        self.is_first_message = True

    async def initialize(self, spinner: Progress, spinner_task: Any) -> None:
        """Initialize the local runner"""
        # Create a single event loop to be used throughout
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        # Initialize the runner
        spinner.update(spinner_task, description="Initializing local runner...")
        try:
            await self.test_chat_runner.initialize()
        except Exception as e:
            ui.stop_spinner()  # Stop spinner before showing error
            raise e  # Re-raise the exception to be handled by caller

    async def process_message(self, message: str) -> Dict[str, Any]:
        """Process a user message locally and return the response"""
        if not self.loop:
            ui.stop_spinner()  # Stop spinner before showing error
            raise Exception("Event loop not initialized")
        
        llm_config = {
            "provider_name": os.getenv("LLM_PROVIDER_NAME", "Anthropic"),
            "provider_model_name": os.getenv("LLM_PROVIDER_MODEL_NAME", "claude-3-7-sonnet-latest"),
            "temperature": os.getenv("LLM_TEMPERATURE", 0),
            "max_tokens": os.getenv("LLM_MAX_TOKENS", 8000),
            "api_key": os.getenv("LLM_API_KEY", "")
        }

        # Create a MessagePayload for the user message
        message_payload = MessagePayload(
            type="user_input",
            content={"text": message}
        )

        register_adapter(MessageChannelType.WHATSAPP, WhatsAppAdapter)

        # Create an agent chat request
        chat_request = AgentChatRequest(
            graph=self.local_graph,
            thread_id=self.thread_id,
            message=message_payload,
            is_new_conversation=self.is_first_message,
            phone_number="+123456789",
            test_mode=True,
            agent_prompt=self.agent_config.get("system_prompt", ""),
            llm_config=llm_config,
            last_interrupt_tool_call_id=None,
            agent_test_chat_id=None,
        )

        try:
            result = await self.test_chat_runner.run(
                graph_definition=chat_request.graph,
                thread_id=chat_request.thread_id,
                message_input=chat_request.message.model_dump() if chat_request.message else None,
                is_new_conversation=chat_request.is_new_conversation,
                phone_number=chat_request.phone_number,
                test_mode=chat_request.test_mode,
                agent_prompt=chat_request.agent_prompt,
                llm_config=chat_request.llm_config,
                last_interrupt_tool_call_id=chat_request.last_interrupt_tool_call_id,
                agent_test_chat_id=chat_request.agent_test_chat_id
            )
            self.is_first_message = False
            return result
        except Exception as e:
            ui.stop_spinner()  # Stop spinner before showing error
            raise e  # Re-raise the exception to be handled by caller

    def display_response(self, response: Dict[str, Any]) -> None:
        """Display the response from the agent"""
        if not response:
            ui.stop_spinner()  # Stop spinner before showing error
            self.console.print("[red]Error: No response from agent[/red]")
            return

        # Format and display the response
        conversation_state = response.get("state", {}).get("values", {}).get("conversation", [])
        if not conversation_state or not isinstance(conversation_state, list):
            return

        # Find all new assistant messages and display them
        for i in range(self.last_displayed_message_index + 1, len(conversation_state)):
            message = conversation_state[i]
            if message.get("role") == "assistant":
                self.console.print(
                    f"\n[blue]Assistant:[/blue]\n",
                    format_message(message.get("content", "")),
                    "\n"
                )

        # Update the last displayed message index
        self.last_displayed_message_index = len(conversation_state) - 1

    def cleanup(self) -> None:
        """Clean up resources when done"""
        if self.loop:
            try:
                self.loop.close()
            except Exception:
                # Ignore any errors when closing the loop
                pass


# Cloud chat client implementation
class CloudChatClient(ChatClient):
    """Client for cloud chat execution"""

    def __init__(self,
                 agent_id: str,
                 project_id: str,
                 local_graph: Dict[str, Any],
                 open_browser: bool,
                 poll_interval: int):
        self.agent_id = agent_id
        self.project_id = project_id
        self.local_graph = local_graph
        self.open_browser = open_browser
        self.poll_interval = poll_interval
        self.agent_snapshot_id = None
        self.test_chat_id = None
        self.last_message_index = -1
        self.auth_service = AuthService()
        self.api_manager = ApiManager(self.auth_service)
        self.api = None
        self.console = Console()

    async def initialize(self, spinner: Progress, spinner_task: Any) -> None:
        """Initialize the cloud client and create a snapshot"""
        # Ensure we have an API key for this project
        if not ensure_project_api_key(self.project_id, self.auth_service, self.api_manager):
            ui.stop_spinner()  # Use the global UI helper to stop spinners
            self.console.print("[red]Error: Could not get or generate API key for the project.[/red]")
            sys.exit(1)

        # Configure API client with project ID
        self.api = self.api_manager.project(self.project_id)

        # Verify agent exists
        self.api.get_agent(self.agent_id)

        # Create a snapshot message
        if self.local_graph:
            spinner.update(spinner_task, description="Creating agent snapshot with local graph...")
        else:
            spinner.update(spinner_task, description="Creating agent snapshot...")

        # Create a snapshot of the agent, using local graph if available
        snapshot_response = self.api.create_agent_snapshot(self.agent_id, self.local_graph)
        self.agent_snapshot_id = snapshot_response["data"]["id"]

        # Open in browser if flag is set
        if self.open_browser:
            import webbrowser
            web_testing_url = f"https://app.kapso.ai/agent_snapshots/{self.agent_snapshot_id}/canvas"
            webbrowser.open(web_testing_url)

    async def process_message(self, message: str) -> Dict[str, Any]:
        """Process a user message in the cloud and return the response"""
        # Create a MessagePayload for the user message
        message_payload = {
            "type": "user_input",
            "content": {"text": message}
        }

        # Create or continue test chat using the snapshot
        test_chat_request = {
            "agent_test_chat_id": self.test_chat_id,
            "message": message_payload
        }

        if not self.api:
            ui.stop_spinner()  # Stop any spinners before raising exception
            raise Exception("API client not initialized properly")

        response = None
        if self.agent_snapshot_id:
            response = self.api.create_agent_test_chat_from_snapshot(
                self.agent_snapshot_id,
                test_chat_request
            )
        else:
            # Fallback to the old method if snapshot creation failed
            response = self.api.create_agent_test_chat(self.agent_id, test_chat_request)

        test_chat = response["data"]
        self.test_chat_id = test_chat["id"]

        # Poll for updates until status is completed or error
        completed_chat = None

        while not completed_chat:
            # Wait for the polling interval
            time.sleep(self.poll_interval / 1000)  # Convert to seconds

            if not self.api:
                ui.stop_spinner()  # Stop any spinners before raising exception
                raise Exception("API client not initialized properly")

            # Get the latest state of the test chat
            chat_response = self.api.get_agent_test_chat(self.test_chat_id)
            current_chat = chat_response["data"]

            # Display any new messages
            self._display_new_messages(current_chat)

            # Check if the chat is complete
            if current_chat["status"] in ["completed", "error"]:
                completed_chat = current_chat
                if current_chat["status"] == "error" and current_chat.get("error"):
                    ui.stop_spinner()  # Stop spinner before showing error
                    self.console.print(f"[red]Error: {current_chat['error']}[/red]")

        return completed_chat

    def _display_new_messages(self, test_chat: Dict[str, Any]) -> None:
        """Display new messages from the test chat"""
        if not test_chat.get("conversation") or not isinstance(test_chat["conversation"], list):
            return

        # Check if there are new messages since we last displayed
        for i in range(self.last_message_index + 1, len(test_chat["conversation"])):
            message = test_chat["conversation"][i]

            # Skip displaying user messages as they're already shown via input
            if message.get("role") == "assistant":
                self.console.print(
                    f"\n[blue]Assistant:[/blue]\n",
                    format_message(message.get("content", "")),
                    "\n"
                )

        self.last_message_index = len(test_chat["conversation"]) - 1

    def display_response(self, response: Dict[str, Any]) -> None:
        """Display the response from the agent"""
        # Responses are already displayed during polling
        pass

    def cleanup(self) -> None:
        """Clean up resources when done"""
        pass


# UI Utilities
class UIHelper:
    """Helper class for UI-related functions"""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.active_progress = None
        self.active_task_id = None

    def start_spinner(self, text: str) -> Tuple[Progress, Any]:
        """
        Start a spinner with text.

        Args:
            text: Text to display with spinner

        Returns:
            Tuple of (Progress object, task_id) that can be used to update the spinner
        """
        # Make sure any existing spinner is stopped first
        self.stop_spinner()

        # Create a new progress display
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold]{task.description}"),
            console=self.console,
            transient=True
        )
        task_id = progress.add_task(description=text, total=None)
        progress.start()

        # Store references to the active progress display
        self.active_progress = progress
        self.active_task_id = task_id

        return progress, task_id

    def stop_spinner(self) -> None:
        """Stop any active spinner"""
        if self.active_progress:
            try:
                self.active_progress.stop()
            except Exception:
                # Ignore errors when stopping (might already be stopped)
                pass
            self.active_progress = None
            self.active_task_id = None

    def error_box(self, message: str) -> Panel:
        """
        Create an error panel.

        Args:
            message: Error message to display

        Returns:
            Rich panel with formatted error message
        """
        return Panel(
            message,
            title="Error",
            border_style="red",
            padding=(1, 2),
        )

    def info_panel(self, title: str, content: str, web_url: Optional[str] = None) -> None:
        """
        Display an informational panel.

        Args:
            title: Title of the panel
            content: Content for the panel
            web_url: Optional URL to display
        """
        # Make sure any spinner is stopped before displaying a panel
        self.stop_spinner()

        panel_content = f"[cyan]{title}[/cyan]\n\n{content}"
        if web_url:
            panel_content += f"\n\n[cyan]Web testing URL:[/cyan]\n[white]{web_url}[/white]"

        self.console.print(
            Panel(
                panel_content,
                border_style="cyan",
                expand=False,
                padding=(1, 2)
            )
        )

    def display_user_message(self, message: str) -> None:
        """Display a user message with formatting"""
        self.console.print(f"[green]You:[/green] {message}")

    def display_error(self, error_message: str) -> None:
        """Display an error message"""
        self.console.print(f"[red]Error: {error_message}[/red]")


app = typer.Typer(name="run", help="Interactive chat with a Kapso agent.")
console = Console()
ui = UIHelper(console)


def format_message(content: str) -> str:
    """
    Format message content for display.

    Args:
        content: Message content

    Returns:
        Formatted message
    """
    # Apply formatting to make code blocks, lists, etc. look better
    return "\n".join(f"  {line}" for line in content.split("\n"))

async def run_chat_loop(chat_client: ChatClient) -> None:
    """
    Run the main chat loop with the given client.

    Args:
        chat_client: The chat client to use
    """
    try:
        while True:
            try:
                # Get user input
                user_input = inquirer.prompt([
                    inquirer.Text("message", message="You", default="")
                ])

                if not user_input:
                    continue

                message = user_input["message"]

                # Check for exit command
                if message.lower() == "/exit":
                    console.print("[yellow]Conversation ended.[/yellow]")
                    break

                # Process message with appropriate client
                loading_spinner, loading_task = ui.start_spinner("Waiting for response...\n")

                try:
                    # Process the message with the client
                    response = await chat_client.process_message(message)
                    ui.stop_spinner()
                    # Display the response
                    chat_client.display_response(response)

                except GenerationLimitError as e:
                    ui.stop_spinner()
                    console.print(
                        ui.error_box(
                            f"Out of free generations!\n\n"
                            f"You've reached your free generations limit. "
                            f"You have {e.free_generations_remaining} free generations remaining.\n\n"
                            f"Please visit https://app.kapso.ai/ to configure an LLM provider for your project."
                        )
                    )
                except Exception as e:
                    ui.stop_spinner()
                    ui.display_error(str(e))

            except KeyboardInterrupt:
                console.print("[yellow]\nConversation ended.[/yellow]")
                break
    finally:
        # Clean up resources
        chat_client.cleanup()


def load_agent_configuration() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Load agent configuration and graph.

    Returns:
        Tuple of (agent_config, local_graph)
    """
    # Try to read local graph definition
    local_graph, _ = load_agent_graph()

    if not local_graph:
        console.print("[red]Error: Could not load agent graph. Make sure agent.yaml exists in the current directory.[/red]")
        sys.exit(1)

    # Load the full agent config to get the system prompt
    agent_config = {}
    try:
        agent_config_path = Path.cwd() / "agent.yaml"
        with open(agent_config_path, "r") as f:
            agent_config = yaml.safe_load(f) or {}
    except Exception as e:
        console.print(f"[red]Error loading agent config: {str(e)}[/red]")
        sys.exit(1)

    return agent_config, local_graph


def compile_agent_if_needed(verbose: bool) -> None:
    """
    Compile agent.py to update agent.yaml if needed.

    Args:
        verbose: Whether to show verbose output
    """
    spinner, spinner_task = ui.start_spinner("Compiling agent to update agent.yaml...")

    try:
        # Use the compile_agent utility function directly
        agent_path = compile_agent(
            agent_file="agent.py",
            output_file=None,
            verbose=verbose
        )

        if agent_path:
            spinner.update(spinner_task, description="Compile successful, initializing chat session...")
        else:
            spinner.update(spinner_task, description="Compile failed, continuing with existing agent.yaml...")
    except Exception as e:
        # Just log a warning and continue if compile fails
        console.print(f"[yellow]Warning: Failed to compile agent: {str(e)}[/yellow]")
        spinner.update(spinner_task, description="Continuing with existing agent.yaml...")
    finally:
        ui.stop_spinner()


async def async_main(
    agent_id: Optional[str] = None,
    open_browser: bool = False,
    poll_interval: int = 1000,
    project_id: Optional[str] = None,
    cloud: bool = False,
    debug: bool = False,
    verbose: bool = False
) -> None:
    """
    Async implementation of the main function.
    """
    # Initialize main spinner
    spinner, spinner_task = ui.start_spinner("Initializing chat session")

    try:
        # First run compile_agent utility to ensure agent.yaml is up-to-date
        compile_agent_if_needed(verbose)

        # Load agent configuration
        spinner.update(spinner_task, description="Loading agent definition...")
        agent_config, local_graph = load_agent_configuration()

        # Create appropriate client based on mode
        chat_client = None

        if cloud:
            # Get project ID
            resolved_project_id = project_id or get_project_id()
            if not resolved_project_id:
                ui.stop_spinner()
                console.print("[red]Error: No project ID found. Please specify a project ID with --project-id or set it in kapso.yaml.[/red]")
                sys.exit(1)

            # Get agent ID
            try:
                resolved_agent_id = get_agent_id(agent_id)
            except Exception as e:
                ui.stop_spinner()
                console.print(f"[red]Error: {str(e)}[/red]")
                sys.exit(1)

            # Create cloud client
            chat_client = CloudChatClient(
                agent_id=resolved_agent_id,
                project_id=resolved_project_id,
                local_graph=local_graph,
                open_browser=open_browser,
                poll_interval=poll_interval
            )

            # Initialize client
            await chat_client.initialize(spinner, spinner_task)

            # Stop spinner and show success message
            ui.stop_spinner()

            # Success message based on whether we used a local graph
            if local_graph:
                console.print("[green]Chat session initialized with local graph snapshot[/green]")
            else:
                console.print("[green]Chat session initialized with agent snapshot[/green]")

            # Get the web testing URL
            web_testing_url = f"https://app.kapso.ai/agent_snapshots/{chat_client.agent_snapshot_id}/canvas"

            # Welcome message
            ui.info_panel(
                "Kapso Agent Chat (Cloud Mode)",
                "[white]Type your messages and press Enter to send.[/white]\n"
                "[white]Type \"/exit\" or press Ctrl+C to end the conversation.[/white]",
                web_testing_url if chat_client.agent_snapshot_id else None
            )

        else:
            # Check for LLM API key before proceeding with local mode
            spinner.update(spinner_task, description="Checking LLM configuration...")
            llm_api_key = os.getenv("LLM_API_KEY", "")
            
            if not llm_api_key:
                ui.stop_spinner()
                console.print("\n[red]Error: LLM_API_KEY not found for local execution[/red]\n")
                console.print("You need to configure an LLM API key to run agents locally.\n")
                console.print("[yellow]Options:[/yellow]")
                console.print("1. Set up your environment variables:")
                console.print("   • Copy .env.example to .env: [cyan]cp .env.example .env[/cyan]")
                console.print("   • Edit .env and add your API key:")
                console.print("     [cyan]LLM_API_KEY=your-anthropic-api-key[/cyan]\n")
                console.print("2. Export the environment variable directly:")
                console.print("   [cyan]export LLM_API_KEY=your-api-key[/cyan]\n")
                console.print("3. Use --cloud flag to run on Kapso Cloud instead\n")
                console.print("Get an Anthropic API key at: https://console.anthropic.com/")
                console.print("Get an OpenAI API key at: https://platform.openai.com/")
                sys.exit(1)
            
            # Check PostgreSQL availability for local mode
            spinner.update(spinner_task, description="Checking PostgreSQL connection...")
            from kapso.runner.core.persistence import check_postgres_connection
            
            is_available, error_msg = await check_postgres_connection()
            if not is_available:
                ui.stop_spinner()
                console.print("\n[red]Error: PostgreSQL is required for local execution[/red]\n")
                console.print("PostgreSQL enables multi-turn conversations and state persistence.\n")
                console.print("[yellow]Options:[/yellow]")
                console.print("1. Install PostgreSQL and set POSTGRES_URL environment variable")
                console.print("   Example: POSTGRES_URL=postgresql://user:password@localhost:5432/dbname")
                console.print("2. Use --cloud flag to run on Kapso Cloud instead\n")
                if error_msg:
                    console.print(f"[dim]Error details: {error_msg}[/dim]\n")
                sys.exit(1)
            
            # Create local client
            chat_client = LocalChatClient(
                debug=debug,
                agent_config=agent_config,
                local_graph=local_graph
            )

            # Initialize client
            await chat_client.initialize(spinner, spinner_task)

            # Stop spinner
            ui.stop_spinner()

            # Welcome message for local mode
            ui.info_panel(
                "Kapso Agent Chat (Local Mode)",
                "[white]Type your messages and press Enter to send.[/white]\n"
                "[white]Type \"/exit\" or press Ctrl+C to end the conversation.[/white]"
            )

        # Run the chat loop with the appropriate client
        await run_chat_loop(chat_client)

    except Exception as e:
        ui.stop_spinner()
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    agent_id: Optional[str] = typer.Argument(
        None,
        help="The ID of the agent to chat with. If not provided, will try to read from kapso.yaml"
    ),
    open_browser: bool = typer.Option(
        False,
        "--open-browser",
        "-o",
        help="Open the agent snapshot in browser"
    ),
    poll_interval: int = typer.Option(
        1000,
        "--poll-interval",
        help="Interval in milliseconds to poll for updates"
    ),
    project_id: Optional[str] = typer.Option(
        None,
        "--project-id",
        "-p",
        help="Project ID to use for API authentication"
    ),
    cloud: bool = typer.Option(
        False,
        "--cloud",
        "-c",
        help="Run the agent in the cloud instead of locally"
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        "-d",
        help="Enable debug logging"
    ),
):
    """
    Interactive chat with a Kapso agent.

    This command starts an interactive chat session with a Kapso agent in your terminal.
    By default, the agent runs locally. Use the --cloud flag to run in Kapso Cloud.

    Examples:

        kapso run

        kapso run <agent_id>

        kapso run --cloud

        kapso run --debug
    """
    # Configure logging
    if debug:
        # Set up root logger for debug output
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            force=True
        )
        logger.debug("Debug logging enabled")

    # If subcommand was invoked, we skip this
    if ctx.invoked_subcommand is not None:
        return

    # Access common options from context
    common_options = ctx.obj
    verbose = common_options.verbose if common_options else False

    # Run the async main function using asyncio
    try:
        asyncio.run(
            async_main(
                agent_id=agent_id,
                open_browser=open_browser,
                poll_interval=poll_interval,
                project_id=project_id,
                cloud=cloud,
                debug=debug,
                verbose=verbose
            )
        )
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        console.print("[yellow]\nConversation ended.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


def get_agent_id(provided_id: Optional[str] = None) -> str:
    """
    Get agent ID from provided argument or configuration files.

    Args:
        provided_id: Optionally provided agent ID

    Returns:
        Resolved agent ID

    Raises:
        Exception: If no agent ID can be resolved
    """
    if provided_id:
        return provided_id

    # First try to read from kapso.yaml using the utility function
    project_config = get_project_config()
    agent_id = project_config.get("agent_id")

    if agent_id:
        return agent_id

    # Fallback to agent.yaml for backward compatibility
    try:
        agent_config_path = Path.cwd() / "agent.yaml"
        with open(agent_config_path, "r") as f:
            config = yaml.safe_load(f)

        if config.get("id"):
            return config["id"]
    except Exception:
        pass

    raise Exception("No agent ID provided and could not read from kapso.yaml or agent.yaml. Please provide an agent ID or ensure kapso.yaml exists with an 'agent_id' field.")


def get_project_config() -> Dict[str, Any]:
    """
    Get project configuration from kapso.yaml.

    Returns:
        Project configuration
    """
    try:
        config_path = Path.cwd() / "kapso.yaml"
        if config_path.exists():
            with open(config_path, "r") as f:
                return yaml.safe_load(f) or {}
    except Exception:
        pass

    return {}