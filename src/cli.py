import sys
import os
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.markdown import Markdown

console = Console()


class CLIInterface:
    def __init__(self):
        self.history = []
        self.operation_log = []

    def print_welcome(self):
        welcome_text = (
            "# Ferris Automation\n\n"
            "**AI Computer Controller** | Version 1.0.0\n\n"
            "Control your computer with natural language AI commands.\n"
            "Type `/help` for available commands or start typing to interact with the AI agent."
        )
        console.print(Panel(
            Markdown(welcome_text),
            title="[bold cyan]Welcome[/bold cyan]",
            border_style="cyan",
            padding=(1, 2)
        ))

    def print_status(self, message, status="info"):
        emojis = {
            "info": "[blue]ℹ[/blue]",
            "success": "[green]✓[/green]",
            "error": "[red]✗[/red]",
            "warning": "[yellow]⚠[/yellow]"
        }
        colors = {
            "info": "blue",
            "success": "green",
            "error": "red",
            "warning": "yellow"
        }
        emoji = emojis.get(status, emojis["info"])
        color = colors.get(status, colors["info"])
        console.print(f"{emoji} [{color}]{message}[/]")

    def print_operation(self, operation, details=""):
        operation_text = f"[bold cyan]{operation}[/]"
        if details:
            operation_text += f"\n[dim]{details}[/]"
        console.print(Panel(
            operation_text,
            title="[bold]Operation[/bold]",
            border_style="cyan",
            padding=(0, 1)
        ))

    def prompt_input(self, prompt_text="> ", default=""):
        return Prompt.ask(
            f"[bold green]{prompt_text}[/]",
            default=default
        )

    def add_to_history(self, user_input, ai_response):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.history.append({
            "timestamp": timestamp,
            "input": user_input,
            "response": ai_response
        })

    def show_history(self):
        if not self.history:
            self.print_status("No command history available.", "warning")
            return

        table = Table(
            title="[bold]Command History[/bold]",
            show_header=True,
            header_style="bold magenta",
            border_style="blue"
        )
        table.add_column("#", style="dim", width=4)
        table.add_column("Time", width=10)
        table.add_column("Input", width=30)
        table.add_column("Response", width=50)

        recent = self.history[-10:]
        for idx, entry in enumerate(recent, start=max(1, len(self.history) - 9)):
            input_summary = entry["input"][:50] + "..." if len(entry["input"]) > 50 else entry["input"]
            response_summary = entry["response"][:80] + "..." if len(entry["response"]) > 80 else entry["response"]
            table.add_row(
                str(idx),
                entry["timestamp"],
                input_summary,
                response_summary
            )

        console.print(table)

    def add_operation_log(self, operation_type, details, status="success"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.operation_log.append({
            "timestamp": timestamp,
            "type": operation_type,
            "details": details,
            "status": status
        })

    def show_operation_log(self):
        if not self.operation_log:
            self.print_status("No operation log available.", "warning")
            return

        table = Table(
            title="[bold]Operation Log[/bold]",
            show_header=True,
            header_style="bold magenta",
            border_style="blue"
        )
        table.add_column("#", style="dim", width=4)
        table.add_column("Time", width=10)
        table.add_column("Type", width=15)
        table.add_column("Status", width=10)
        table.add_column("Details", width=50)

        recent = self.operation_log[-10:]
        for idx, entry in enumerate(recent, start=max(1, len(self.operation_log) - 9)):
            status_color = {
                "success": "green",
                "error": "red",
                "warning": "yellow",
                "info": "blue"
            }.get(entry["status"], "white")

            details_summary = entry["details"][:50] + "..." if len(entry["details"]) > 50 else entry["details"]
            table.add_row(
                str(idx),
                entry["timestamp"],
                entry["type"],
                f"[{status_color}]{entry['status']}[/]",
                details_summary
            )

        console.print(table)

    def print_help(self):
        help_text = (
            "## Available Commands\n\n"
            "| Command | Description |\n"
            "|---------|-------------|\n"
            "| `/help` | Show this help message |\n"
            "| `/config` | Configure API settings |\n"
            "| `/history` | Show command history (last 10) |\n"
            "| `/log` | Show operation log (last 10) |\n"
            "| `/screenshot` | Take and show screenshot |\n"
            "| `/status` | Show system status |\n"
            "| `/quit` | Exit the program |\n\n"
            "**Usage:** Type any text to send it to the AI agent for processing."
        )
        console.print(Panel(
            Markdown(help_text),
            title="[bold]Help[/bold]",
            border_style="green",
            padding=(1, 2)
        ))
    
    def prompt_config(self, label, current_value, is_password=False):
        """提示配置项，显示当前值"""
        if is_password and current_value:
            masked = "*" * min(len(current_value), 20)
            hint = f"[dim]current: {masked}[/dim]"
        elif current_value:
            hint = f"[dim]current: {current_value}[/dim]"
        else:
            hint = "[dim]not set[/dim]"
        
        value = Prompt.ask(f"  {label} {hint}")
        return value if value.strip() else current_value
    
    def show_config(self, config):
        """显示当前配置"""
        from rich.table import Table
        table = Table(title="[bold]Current Configuration[/bold]", border_style="cyan")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        api_key_masked = "*" * min(len(config.OPENAI_API_KEY), 20) if config.OPENAI_API_KEY else "(not set)"
        table.add_row("API Key", api_key_masked)
        table.add_row("API Base URL", config.OPENAI_BASE_URL)
        table.add_row("Model", config.DEFAULT_MODEL)
        table.add_row("OmniParser URL", config.OMNIPARSER_URL)
        table.add_row("OmniParser Auto-Start", "Yes" if config.OMNIPARSER_AUTO_START else "No")
        table.add_row("OmniParser Path", config.OMNIPARSER_PATH or "(auto-detect)")
        
        console.print(table)
    
    def run_config_wizard(self, config):
        """运行配置向导"""
        console.print(Panel(
            "[bold cyan]API Configuration Wizard[/bold cyan]\n\n"
            "Configure your AI API settings. Leave blank to keep current values.\n"
            "Settings will be saved to .env file.",
            border_style="cyan",
            padding=(1, 2)
        ))
        
        # 显示当前配置
        self.show_config(config)
        console.print()
        
        # 配置API密钥
        new_api_key = self.prompt_config(
            "API Key",
            config.OPENAI_API_KEY,
            is_password=True
        )
        if new_api_key != config.OPENAI_API_KEY:
            config.update_api_key(new_api_key)
        
        # 配置API地址
        new_base_url = self.prompt_config(
            "API Base URL",
            config.OPENAI_BASE_URL
        )
        if new_base_url != config.OPENAI_BASE_URL:
            config.update_base_url(new_base_url)
        
        # 配置模型
        new_model = self.prompt_config(
            "Model Name",
            config.DEFAULT_MODEL
        )
        if new_model != config.DEFAULT_MODEL:
            config.update_model(new_model)
        
        # 配置OmniParser URL
        new_omni_url = self.prompt_config(
            "OmniParser URL",
            config.OMNIPARSER_URL
        )
        if new_omni_url != config.OMNIPARSER_URL:
            config.update_omniparser_url(new_omni_url)
        
        # 配置OmniParser安装路径
        new_omni_path = self.prompt_config(
            "OmniParser Path",
            config.OMNIPARSER_PATH
        )
        if new_omni_path != config.OMNIPARSER_PATH:
            config.update_omniparser_path(new_omni_path)
        
        # 配置OmniParser自动启动
        auto_start_choices = ["y", "n"]
        current_auto = "y" if config.OMNIPARSER_AUTO_START else "n"
        new_auto = Prompt.ask(
            f"  OmniParser Auto-Start [dim]current: {current_auto}[/dim]",
            choices=auto_start_choices,
            default=current_auto
        )
        config.set_omniparser_auto_start(new_auto.lower() == "y")
        
        # 保存配置
        if self.confirm("Save configuration to .env file?"):
            config.save_to_env()
            self.print_status("Configuration saved successfully!", "success")
        else:
            self.print_status("Configuration kept in memory only (not saved)", "warning")
        
        console.print()
        self.show_config(config)

    def print_error(self, message):
        console.print(f"[bold red]Error:[/] {message}")

    def confirm(self, message):
        response = Prompt.ask(
            f"[yellow]{message}[/]",
            choices=["y", "n"],
            default="y"
        )
        return response.lower() == "y"

    def run_interactive_loop(self, agent=None, config=None):
        self.print_welcome()
        console.print()

        while True:
            try:
                user_input = self.prompt_input()

                if not user_input.strip():
                    continue

                stripped = user_input.strip()

                if stripped.startswith("/"):
                    command = stripped.lower()

                    if command == "/help":
                        self.print_help()
                    elif command == "/config":
                        if config:
                            self.run_config_wizard(config)
                            if agent:
                                # Reinitialize agent with new config
                                try:
                                    agent.llm_client = agent.llm_client.__class__(
                                        api_key=config.OPENAI_API_KEY,
                                        base_url=config.OPENAI_BASE_URL,
                                        model=config.DEFAULT_MODEL
                                    )
                                    self.print_status("Agent reconfigured with new settings", "success")
                                except Exception as e:
                                    self.print_error(f"Failed to reconfigure agent: {e}")
                        else:
                            self.print_status("Configuration not available", "warning")
                    elif command == "/history":
                        self.show_history()
                    elif command == "/log":
                        self.show_operation_log()
                    elif command == "/screenshot":
                        self.print_operation("Screenshot", "Taking screenshot...")
                        self.add_operation_log("screenshot", "Screenshot requested", "info")
                        if agent and hasattr(agent, "take_screenshot"):
                            try:
                                result = agent.take_screenshot()
                                self.print_status(f"Screenshot taken: {result}", "success")
                                self.add_operation_log("screenshot", str(result), "success")
                            except Exception as e:
                                self.print_error(f"Failed to take screenshot: {e}")
                                self.add_operation_log("screenshot", str(e), "error")
                        else:
                            self.print_status("Screenshot functionality not available.", "warning")
                    elif command == "/status":
                        self.print_operation("System Status", "Checking system status...")
                        self.add_operation_log("status", "Status check requested", "info")
                        if agent and hasattr(agent, "get_status"):
                            try:
                                status = agent.get_status()
                                self.print_status(f"System status: {status}", "success")
                                self.add_operation_log("status", str(status), "success")
                            except Exception as e:
                                self.print_error(f"Failed to get status: {e}")
                                self.add_operation_log("status", str(e), "error")
                        else:
                            self.print_status("Status functionality not available.", "warning")
                    elif command == "/quit" or command == "/exit":
                        self.print_status("Goodbye!", "success")
                        sys.exit(0)
                    else:
                        self.print_error(f"Unknown command: {command}. Type /help for available commands.")
                else:
                    if agent:
                        try:
                            self.print_operation("Processing", f"Sending to AI agent...")
                            self.add_operation_log("agent", f"Input: {user_input[:50]}", "info")

                            response = agent.run(user_input)

                            console.print(Panel(
                                str(response),
                                title="[bold cyan]AI Response[/bold cyan]",
                                border_style="cyan",
                                padding=(1, 2)
                            ))

                            self.add_to_history(user_input, str(response))
                            self.add_operation_log("agent", "Response received", "success")
                        except Exception as e:
                            self.print_error(f"Agent error: {e}")
                            self.add_operation_log("agent", str(e), "error")
                    else:
                        self.print_status("No AI agent available. Type /help for commands.", "warning")

            except KeyboardInterrupt:
                console.print()
                self.print_status("Interrupted. Type /quit to exit.", "warning")
            except EOFError:
                console.print()
                self.print_status("EOF detected. Exiting...", "warning")
                sys.exit(0)
