import sys
import argparse
from pathlib import Path
from src.config import load_config
from src.cli import CLIInterface
from src.agent import AIAgent
from src.omniparser_launcher import OmniParserLauncher
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


def install_omniparser(install_dir=None):
    """Atuo installOmniParser"""
    console.print(Panel(
        Markdown("## OmniParser Atuo install\n\n"
                 "This will:\n"
                 "1. Clone OmniParser repository\n"
                 "2. Download model weights from HuggingFace\n"
                 "3. Install dependencies\n\n"
                 "**This may take several minutes.**"),
        title="[bold cyan]Installation[/bold cyan]",
        border_style="cyan",
        padding=(1, 2)
    ))
    
    launcher = OmniParserLauncher(install_dir=install_dir)
    
    console.print()
    console.print("[bold]Step 1/3:[/] Cloning OmniParser repository...")
    if not launcher.clone_omniparser():
        console.print("[bold red]Failed to clone OmniParser![/bold red]")
        console.print("[yellow]Please check if git is installed and you have internet connection.[/yellow]")
        return False
    console.print("[bold green]✓ OmniParser cloned[/bold green]")
    
    console.print()
    console.print("[bold]Step 2/3:[/] Downloading model weights...")
    console.print("[dim]Files to download:[/dim]")
    for f in launcher.WEIGHT_FILES:
        console.print(f"  - {f}")
    console.print()
    
    if launcher.download_weights():
        console.print("[bold green]✓ Weights downloaded[/bold green]")
    else:
        console.print("[bold yellow]⚠ Some weights may have failed to download[/bold yellow]")
        console.print("[dim]You can re-run the installer to retry.[/dim]")
    
    console.print()
    console.print("[bold]Step 3/3:[/] Installing dependencies...")
    if launcher.install_dependencies():
        console.print("[bold green]✓ Dependencies installed[/bold green]")
    else:
        console.print("[bold yellow]⚠ Dependency installation failed[/bold yellow]")
        console.print("[yellow]Please install requirements.txt manually:[/yellow]")
        console.print(f"  cd {launcher.install_dir}")
        console.print("  pip install -r requirements.txt")
    
    console.print()
    console.print(Panel(
        "[bold green]Installation completed![/bold green]\n\n"
        f"OmniParser installed at: [cyan]{launcher.install_dir}[/cyan]\n\n"
        "You can now start the AI Computer Controller and it will auto-launch OmniParser.",
        title="[bold]Done[/bold]",
        border_style="green",
        padding=(1, 2)
    ))
    return True


def try_start_omniparser(config, cli):
    """尝试自动启动OmniParser"""
    if not config.OMNIPARSER_AUTO_START:
        cli.print_status("OmniParser auto-start is disabled", "info")
        return None
    
    cli.print_status("Checking OmniParser service...", "info")
    
    install_dir = Path(config.OMNIPARSER_PATH) if config.OMNIPARSER_PATH else None
    launcher = OmniParserLauncher(
        base_url=config.OMNIPARSER_URL,
        timeout=30,
        install_dir=install_dir
    )
    
    # 检测是否已在运行
    if launcher.is_running():
        cli.print_status(f"OmniParser is already running at {config.OMNIPARSER_URL}", "success")
        return launcher
    
    # 查找OmniParser安装
    omni_path = launcher.find_omniparser_path()
    if omni_path is None:
        cli.print_status("OmniParser not installed", "warning")
        cli.print_status("Run 'python main.py --install-omniparser' to install", "warning")
        return None
    
    # 自动配置检测到的路径
    omni_project_dir = omni_path.parent if omni_path.name.endswith('.py') else omni_path
    if config.OMNIPARSER_PATH != str(omni_project_dir):
        config.update_omniparser_path(str(omni_project_dir))
        cli.print_status(f"Detected OmniParser at: {omni_project_dir}", "info")
    
    # 尝试自动启动
    cli.print_status("Starting OmniParser...", "info")
    
    if launcher.launch(omni_path, device=config.OMNIPARSER_DEVICE):
        cli.print_status(f"OmniParser started successfully at {config.OMNIPARSER_URL}", "success")
        return launcher
    else:
        cli.print_status("Failed to start OmniParser", "warning")
        cli.print_status("Please start OmniParser manually", "warning")
        return None


def main():
    parser = argparse.ArgumentParser(description="AI Computer Controller - Let AI control your computer")
    parser.add_argument("--unsafe-fast-mode", action="store_true", 
                       help="Disable safety confirmations (use with caution)")
    parser.add_argument("--prompt", type=str, default=None,
                       help="Run a single prompt and exit")
    parser.add_argument("--no-omniparser", action="store_true",
                       help="Disable OmniParser auto-start")
    parser.add_argument("--omniparser-path", type=str, default=None,
                       help="Path to OmniParser installation")
    parser.add_argument("--install-omniparser", action="store_true",
                       help="Install OmniParser (clone, download weights, install deps)")
    parser.add_argument("--omniparser-install-dir", type=str, default=None,
                       help="Directory to install OmniParser (default: ~/OmniParser)")
    args = parser.parse_args()
    
    config = load_config()
    cli = CLIInterface()
    
    # 如果请求安装OmniParser
    if args.install_omniparser:
        install_dir = args.omniparser_install_dir
        if install_dir:
            config.update_omniparser_path(install_dir)
            config.save_to_env()
        install_omniparser(Path(install_dir) if install_dir else None)
        return
    
    # 命令行参数覆盖配置文件
    if args.no_omniparser:
        config.set_omniparser_auto_start(False)
    if args.omniparser_path:
        config.update_omniparser_path(args.omniparser_path)
    
    # 如果API密钥未配置，启动配置向导
    if not config.is_configured():
        cli.print_status("API key not configured!", "warning")
        cli.print_status("Starting configuration wizard...", "info")
        console.print()
        cli.run_config_wizard(config)
        console.print()
        
        # 配置后检查是否设置了API密钥
        if not config.is_configured():
            cli.print_status("No API key provided. Please run /config later to set it up.", "warning")
    
    # 尝试启动OmniParser
    omniparser_launcher = try_start_omniparser(config, cli)
    
    safe_mode = not args.unsafe_fast_mode
    if not safe_mode:
        cli.print_status("UNSAFE FAST MODE - Safety confirmations disabled!", "warning")
    
    agent = AIAgent(config=config, safe_mode=safe_mode)
    cli.print_welcome()
    console.print()
    
    if args.prompt:
        if not config.is_configured():
            cli.print_error("Cannot run prompt without API key. Configure with /config first.")
            sys.exit(1)
        agent.run(args.prompt)
    else:
        cli.run_interactive_loop(agent=agent, config=config)

if __name__ == "__main__":
    main()
