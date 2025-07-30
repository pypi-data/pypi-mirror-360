#!/usr/bin/env python3
"""CatSCAN CLI - Terraform Infrastructure Scanner"""

import requests
import os
import json
import time
import getpass
import subprocess
import sys
import platform
from datetime import datetime
from pathlib import Path
from rich import print
from rich.table import Table
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
from typing import List, Dict, Optional

# Platform-specific keyboard handling
if platform.system() == "Windows":
    import msvcrt
else:
    import termios
    import tty

# Configuration
TFC_API_URL = "https://app.terraform.io/api/v2"
CONFIG_FILE = Path.home() / ".catscan_config.json"
HISTORY_DIR = Path.home() / ".catscan_history"

console = Console()

def print_banner():
    """Print elaborate ASCII banner for CatSCAN tool"""
    banner = r"""
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                      ║
║   ░█████╗░░█████╗░████████╗░░░░░░░░██████╗░█████╗░░█████╗░███╗░██╗                   ║
║   ██╔══██╗██╔══██╗╚══██╔══╝░░░░░░██╔════╝██╔══██╗██╔══██╗████╗░██║                   ║
║   ██║░░╚═╝███████║░░░██║░░░█████╗╚█████╗░██║░░╚═╝███████║██╔██╗██║                   ║
║   ██║░░██╗██╔══██║░░░██║░░░╚════╝░╚═══██╗██║░░██╗██╔══██║██║╚████║                   ║
║   ╚█████╔╝██║░░██║░░░██║░░░░░░░░░██████╔╝╚█████╔╝██║░░██║██║░╚███║                   ║
║   ░╚════╝░╚═╝░░╚═╝░░░╚═╝░░░░░░░░░╚═════╝░░╚════╝░╚═╝░░╚═╝╚═╝░░╚══╝                   ║
║                                                                                      ║
║              /\_ _/\                Terraform Infrastructure Scanner v1.0            ║
║             (  o.o  )    ╭─────╮                                                     ║
║              )==Y==(     │ ╭─╮ │    ┌─────────────────────────────────────────────┐  ║
║             /       \    │ │ │ │    │   AWS Resource Discovery & Visualization    │  ║
║            /         \   │ ╰─╯ │    │   Multi-Workspace Terraform Analysis        │  ║
║           (   | || |  )  ╰─────╯    │   Infrastructure Observability Tool         │  ║
║            \__\_/\_/__/      |      └─────────────────────────────────────────────┘  ║
║                   ||         |                                                       ║
║                   ||      .--'                                                       ║
║             \\    //      /                                                          ║
║              \\__//      /            ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░     ║
║                        (              ░ Scanning AWS Resources... Meow!     ░░░░     ║
║                        \              ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░     ║
║                         '--.__                                                       ║
║                               )                                                      ║
║                              /                                                       ║
║                             /                                                        ║
║                                                        Built by Simon Farrell        ║
╚══════════════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)
    time.sleep(0.5)

def load_config() -> Dict:
    """Load saved configuration from file"""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    return {}

def save_config(config: Dict):
    """Save configuration to file (excluding sensitive data)"""
    try:
        # Only save non-sensitive configuration
        safe_config = {k: v for k, v in config.items() if k != 'token'}
        with open(CONFIG_FILE, 'w') as f:
            json.dump(safe_config, f, indent=2)
    except IOError:
        console.print("[yellow]⚠️ Could not save configuration[/yellow]")

def set_persistent_env_vars_windows(org_name: str, token: str) -> bool:
    """Set persistent environment variables on Windows using registry"""
    try:
        # Use PowerShell to set user environment variables
        ps_commands = [
            f'[Environment]::SetEnvironmentVariable("TFC_ORG_NAME", "{org_name}", "User")',
            f'[Environment]::SetEnvironmentVariable("TFC_TOKEN", "{token}", "User")'
        ]
        
        for cmd in ps_commands:
            result = subprocess.run([
                "powershell", "-Command", cmd
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, cmd)
        
        # Set for current session as well
        os.environ['TFC_ORG_NAME'] = org_name
        os.environ['TFC_TOKEN'] = token
        
        return True
        
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return False

def set_persistent_env_vars_unix(org_name: str, token: str) -> str:
    """Set persistent environment variables on Unix-like systems"""
    home = Path.home()
    
    # Determine which shell config file to use
    shell_configs = [
        home / ".bashrc",
        home / ".zshrc", 
        home / ".bash_profile",
        home / ".profile"
    ]
    
    # Find existing config file or use .bashrc as default
    config_file = None
    for config in shell_configs:
        if config.exists():
            config_file = config
            break
    
    if not config_file:
        config_file = home / ".bashrc"  # Default fallback
    
    try:
        # Read existing content
        existing_content = ""
        if config_file.exists():
            with open(config_file, 'r') as f:
                existing_content = f.read()
        
        # Remove any existing CatSCAN entries
        lines = existing_content.split('\n')
        filtered_lines = [line for line in lines if not line.startswith('# CatSCAN') and 
                         'TFC_ORG_NAME=' not in line and 'TFC_TOKEN=' not in line]
        
        # Add new CatSCAN entries
        new_lines = filtered_lines + [
            "",
            "# CatSCAN Terraform Cloud Configuration",
            f"export TFC_ORG_NAME='{org_name}'",
            f"export TFC_TOKEN='{token}'",
            ""
        ]
        
        # Write back to file
        with open(config_file, 'w') as f:
            f.write('\n'.join(new_lines))
        
        return config_file.name
        
    except IOError:
        return None

def set_persistent_env_vars(org_name: str, token: str):
    """Set persistent environment variables cross-platform"""
    is_windows = platform.system() == "Windows"
    
    # Set in current environment immediately
    os.environ['TFC_ORG_NAME'] = org_name
    os.environ['TFC_TOKEN'] = token
    
    if is_windows:
        success = set_persistent_env_vars_windows(org_name, token)
        if success:
            return "Windows Registry (User Environment Variables)"
        else:
            console.print(f"[yellow]⚠️ Could not update Windows environment variables[/yellow]")
            console.print("[yellow]Setting environment variables for current session only[/yellow]")
            return None
    else:
        config_file = set_persistent_env_vars_unix(org_name, token)
        if config_file:
            return config_file
        else:
            console.print(f"[yellow]⚠️ Could not update shell config[/yellow]")
            console.print("[yellow]Setting environment variables for current session only[/yellow]")
            return None

def get_interactive_config() -> tuple[str, str]:
    """Get configuration through interactive prompts"""
    saved_config = load_config()
    is_windows = platform.system() == "Windows"
    
    # Show setup panel with security notice
    setup_text = Text()
    setup_text.append("🛠️  ", style="bold blue")
    setup_text.append("Configuration Setup", style="bold white")
    setup_text.append("\nPlease provide your Terraform Cloud credentials", style="dim white")
    
    if is_windows:
        setup_text.append("\n⚠️  These will be stored in Windows User Environment Variables", style="bold yellow")
    else:
        setup_text.append("\n⚠️  These will be stored persistently in your shell config", style="bold yellow")
    
    setup_text.append("\n   Consider using a token with limited scope/duration", style="dim yellow")
    
    console.print(Panel(
        setup_text,
        border_style="blue",
        padding=(1, 2),
        title="[bold blue]Setup Required[/bold blue]",
        title_align="left"
    ))
    print()
    
    # Confirm user wants to proceed with persistent storage
    if not Confirm.ask("📝 Do you want to store credentials persistently?", default=True):
        console.print("[yellow]Cancelled. Use environment variables TFC_ORG_NAME and TFC_TOKEN instead.[/yellow]")
        exit(0)
    
    print()
    
    # Get organization name
    saved_org = saved_config.get('org_name')
    if saved_org:
        org_prompt = f"🏢 Organization name [{saved_org}]"
        org_name = Prompt.ask(org_prompt, default=saved_org)
    else:
        org_name = Prompt.ask("🏢 Organization name", console=console)
    
    if not org_name or org_name.strip() == "":
        console.print("[bold red]❌ Organization name is required[/bold red]")
        exit(1)
    
    # Get token (masked input)
    console.print("🔐 Terraform Cloud API Token (input will be hidden)")
    token = getpass.getpass("   Enter token: ")
    
    if not token or token.strip() == "":
        console.print("[bold red]❌ API token is required[/bold red]")
        exit(1)
    
    # Set persistent environment variables
    storage_location = set_persistent_env_vars(org_name.strip(), token.strip())
    
    # Save organization name to config file as well
    config_to_save = {'org_name': org_name.strip()}
    save_config(config_to_save)
    
    # Show confirmation based on platform
    if storage_location:
        if is_windows:
            console.print(Panel(
                f"✅ [bold green]Credentials stored persistently[/bold green]\n"
                f"   Location: [cyan]{storage_location}[/cyan]\n"
                f"   [dim]Restart terminal or start new PowerShell session to apply[/dim]\n\n"
                f"🗑️  [bold yellow]To remove later:[/bold yellow]\n"
                f"   Run: [cyan]Remove-Item Env:TFC_ORG_NAME,TFC_TOKEN[/cyan]\n"
                f"   Or use System Properties → Environment Variables",
                border_style="green",
                padding=(1, 2),
                title="[bold green]Credentials Saved[/bold green]",
                title_align="left"
            ))
        else:
            console.print(Panel(
                f"✅ [bold green]Credentials stored persistently[/bold green]\n"
                f"   Updated: [cyan]~/{storage_location}[/cyan]\n"
                f"   [dim]Restart terminal or run 'source ~/{storage_location}' to apply[/dim]\n\n"
                f"🗑️  [bold yellow]To remove later:[/bold yellow]\n"
                f"   Edit [cyan]~/{storage_location}[/cyan] and delete the CatSCAN section",
                border_style="green",
                padding=(1, 2),
                title="[bold green]Credentials Saved[/bold green]",
                title_align="left"
            ))
    else:
        console.print(Panel(
            "✅ [bold green]Credentials set for current session[/bold green]\n"
            "   Could not update persistent storage, using session-only storage",
            border_style="yellow",
            padding=(1, 2),
            title="[bold yellow]Session Only[/bold yellow]",
            title_align="left"
        ))
    print()
    
    return org_name.strip(), token.strip()

def get_windows_user_env_var(var_name: str) -> Optional[str]:
    """Get user environment variable from Windows registry"""
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _ = winreg.QueryValueEx(key, var_name)
            return value
    except (ImportError, OSError, FileNotFoundError):
        return None

def get_config() -> tuple[str, str]:
    """Get configuration from environment variables or interactive input"""
    # Check if environment variables are set (for CI/CD compatibility)
    env_org = os.getenv("TFC_ORG_NAME")
    env_token = os.getenv("TFC_TOKEN")
    
    # On Windows, also check the registry for user environment variables
    if platform.system() == "Windows" and (not env_org or not env_token):
        if not env_org:
            env_org = get_windows_user_env_var("TFC_ORG_NAME")
        if not env_token:
            env_token = get_windows_user_env_var("TFC_TOKEN")
    
    if env_org and env_token and env_org != "your-org-name":
        # Environment variables mode
        console.print(Panel(
            "🤖 [bold green]Environment variables detected[/bold green]\n"
            f"   Organization: [cyan]{env_org}[/cyan]\n"
            f"   Token: [dim]••••••••[/dim] (from environment)",
            border_style="green",
            padding=(1, 2),
            title="[bold green]Automated Mode[/bold green]",
            title_align="left"
        ))
        print()
        return env_org, env_token
    else:
        # Interactive mode
        return get_interactive_config()

def show_scanning_panel(org_name: str):
    """Display scanning announcement panel"""
    scanning_text = Text()
    scanning_text.append("🔍 ", style="bold cyan")
    scanning_text.append("Initializing Infrastructure Scan", style="bold white")
    scanning_text.append(f"\n   Target Organization: ", style="dim white")
    scanning_text.append(f"{org_name}", style="bold cyan")
    scanning_text.append(f"\n   Discovering Terraform workspaces and resources...", style="dim white")
    
    console.print(Panel(
        scanning_text,
        border_style="cyan",
        padding=(1, 2),
        title="[bold cyan]🐾 CatSCAN Active[/bold cyan]",
        title_align="left"
    ))
    print()

def get_workspaces(headers: Dict) -> List[Dict]:
    """Fetch all workspaces from Terraform Cloud"""
    try:
        url = f"{TFC_API_URL}/organizations/{headers['org_name']}/workspaces"
        response = requests.get(url, headers={
            "Authorization": headers["Authorization"],
            "Content-Type": "application/vnd.api+json"
        }, timeout=30)
        response.raise_for_status()
        return response.json()["data"]
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error fetching workspaces: {e}[/bold red]")
        return []
    except KeyError:
        console.print("[bold red]Unexpected API response format[/bold red]")
        return []

def get_state_version(workspace_id: str, headers: Dict) -> Optional[str]:
    """Get current state version download URL for a workspace"""
    try:
        url = f"{TFC_API_URL}/workspaces/{workspace_id}/current-state-version"
        response = requests.get(url, headers={
            "Authorization": headers["Authorization"],
            "Content-Type": "application/vnd.api+json"
        }, timeout=30)
        
        if response.status_code == 404:
            return None
            
        response.raise_for_status()
        data = response.json()
        return data["data"]["attributes"]["hosted-state-download-url"]
        
    except requests.exceptions.RequestException:
        return None
    except (KeyError, TypeError):
        return None

def fetch_resources_from_state(state_url: str, headers: Dict) -> Dict[str, int]:
    """Fetch and count resources from state file"""
    try:
        # Pass authorization headers when fetching state
        response = requests.get(state_url, headers={
            "Authorization": headers["Authorization"],
            "Content-Type": "application/vnd.api+json"
        }, timeout=30)
        response.raise_for_status()
        state = response.json()
        
        resource_counts = {}
        
        # Handle different state file formats
        # Modern format: values.root_module.resources
        if "values" in state and "root_module" in state["values"]:
            resources = state["values"]["root_module"].get("resources", [])
        # Legacy format: resources at top level
        elif "resources" in state:
            resources = state.get("resources", [])
        else:
            # No resources found in expected locations
            return {}
        
        for resource in resources:
            resource_type = resource.get("type", "unknown")
            resource_counts[resource_type] = resource_counts.get(resource_type, 0) + 1
            
        return resource_counts
        
    except requests.exceptions.RequestException:
        return {}
    except (json.JSONDecodeError, KeyError, TypeError):
        return {}

def format_resource_summary(resource_counts: Dict[str, int]) -> str:
    """Format resource counts into a readable string"""
    if not resource_counts:
        return "[dim]No resources[/dim]"
    
    # Sort by count (descending) then by name
    sorted_resources = sorted(resource_counts.items(), key=lambda x: (-x[1], x[0]))
    
    if len(sorted_resources) <= 3:
        return ", ".join([f"{rtype}({count})" for rtype, count in sorted_resources])
    else:
        # Show top 3 and total count
        top_3 = ", ".join([f"{rtype}({count})" for rtype, count in sorted_resources[:3]])
        total = sum(resource_counts.values())
        return f"{top_3} + {len(sorted_resources)-3} more ({total} total)"

def save_scan_results(org_name: str, workspaces_data: List[Dict], processed_count: int, error_count: int):
    """Save scan results to history"""
    try:
        # Ensure history directory exists
        HISTORY_DIR.mkdir(exist_ok=True)
        
        # Create scan record
        timestamp = datetime.now()
        scan_data = {
            "timestamp": timestamp.isoformat(),
            "organization": org_name,
            "workspaces": workspaces_data,
            "summary": {
                "total_workspaces": len(workspaces_data),
                "processed_workspaces": processed_count,
                "error_workspaces": error_count,
                "total_resources": sum(ws.get("resource_count", 0) for ws in workspaces_data)
            }
        }
        
        # Save to timestamped file
        filename = f"scan_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        scan_file = HISTORY_DIR / filename
        
        with open(scan_file, 'w') as f:
            json.dump(scan_data, f, indent=2)
        
        # Update scan index
        index_file = HISTORY_DIR / "scans.json"
        scans_index = []
        
        if index_file.exists():
            try:
                with open(index_file, 'r') as f:
                    scans_index = json.load(f)
            except (json.JSONDecodeError, IOError):
                scans_index = []
        
        # Add new scan to index
        scans_index.append({
            "filename": filename,
            "timestamp": scan_data["timestamp"],
            "organization": org_name,
            "summary": scan_data["summary"]
        })
        
        # Keep only last 30 scans
        scans_index = scans_index[-30:]
        
        # Save updated index
        with open(index_file, 'w') as f:
            json.dump(scans_index, f, indent=2)
        
        # Clean up old scan files
        cleanup_old_scans(scans_index)
        
        return True
        
    except (IOError, OSError):
        return False

def cleanup_old_scans(scans_index: List[Dict]):
    """Remove scan files not in the index"""
    try:
        if not HISTORY_DIR.exists():
            return
            
        # Get filenames that should exist
        valid_files = {scan["filename"] for scan in scans_index}
        valid_files.add("scans.json")  # Don't delete the index
        
        # Remove any scan files not in index
        for file in HISTORY_DIR.glob("scan_*.json"):
            if file.name not in valid_files:
                file.unlink()
                
    except (IOError, OSError):
        pass

def load_scan_history() -> List[Dict]:
    """Load scan history from index"""
    try:
        index_file = HISTORY_DIR / "scans.json"
        if not index_file.exists():
            return []
            
        with open(index_file, 'r') as f:
            return json.load(f)
            
    except (json.JSONDecodeError, IOError):
        return []

def load_scan_details(filename: str) -> Optional[Dict]:
    """Load details for a specific scan"""
    try:
        scan_file = HISTORY_DIR / filename
        if not scan_file.exists():
            return None
            
        with open(scan_file, 'r') as f:
            return json.load(f)
            
    except (json.JSONDecodeError, IOError):
        return None

def get_key():
    """Cross-platform function to get a single keypress"""
    if platform.system() == "Windows":
        # Windows implementation
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b'\xe0':  # Special key prefix on Windows
                    key = msvcrt.getch()
                    if key == b'H':  # Up arrow
                        return 'UP'
                    elif key == b'P':  # Down arrow
                        return 'DOWN'
                elif key == b'\r':  # Enter
                    return 'ENTER'
                elif key == b'\x1b':  # Escape
                    return 'ESCAPE'
                elif key in [b'h', b'H']:
                    return 'h'
                elif key in [b'r', b'R']:
                    return 'r'
                elif key in [b'q', b'Q']:
                    return 'q'
            time.sleep(0.01)
    else:
        # Unix/Linux implementation
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            key = sys.stdin.read(1)
            
            if key == '\x1b':  # Escape sequence
                next_chars = sys.stdin.read(2)
                if next_chars == '[A':  # Up arrow
                    return 'UP'
                elif next_chars == '[B':  # Down arrow
                    return 'DOWN'
                else:
                    return 'ESCAPE'
            elif key == '\r' or key == '\n':  # Enter
                return 'ENTER'
            elif key.lower() in ['h', 'r', 'q']:
                return key.lower()
            else:
                return key
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def format_timestamp(iso_timestamp: str) -> str:
    """Format ISO timestamp for display"""
    try:
        dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return iso_timestamp

def show_scan_history():
    """Interactive scan history viewer"""
    history = load_scan_history()
    
    if not history:
        console.print(Panel(
            "📭 [yellow]No scan history found[/yellow]\n"
            "   Run a scan first to build your history!",
            border_style="yellow",
            padding=(1, 2),
            title="[bold yellow]Empty History[/bold yellow]",
            title_align="left"
        ))
        console.print("\n[dim]Press any key to return to menu...[/dim]")
        get_key()
        return
    
    # Sort by timestamp (newest first)
    history.sort(key=lambda x: x["timestamp"], reverse=True)
    
    selected_index = 0
    
    while True:
        # Create history table
        table = Table(
            title="📈 Scan History (Use ↑↓ to navigate, Enter to view, Escape to return)",
            show_header=True,
            header_style="bold magenta"
        )
        table.add_column("Date/Time", style="cyan", width=20)
        table.add_column("Organization", style="green", width=25)
        table.add_column("Workspaces", style="yellow", width=12)
        table.add_column("Resources", style="blue", width=12)
        table.add_column("Status", style="white", width=15)
        
        for i, scan in enumerate(history):
            timestamp = format_timestamp(scan["timestamp"])
            org = scan["organization"]
            ws_count = scan["summary"]["processed_workspaces"]
            total_ws = scan["summary"]["total_workspaces"]
            resources = scan["summary"]["total_resources"]
            
            if scan["summary"]["error_workspaces"] > 0:
                status = f"✅ {ws_count} ⚠️ {scan['summary']['error_workspaces']}"
            else:
                status = f"✅ {ws_count}/{total_ws}"
            
            # Highlight selected row
            style = "bold white on blue" if i == selected_index else None
            
            table.add_row(
                timestamp, org, str(total_ws), str(resources), status,
                style=style
            )
        
        # Show instructions
        instructions = Panel(
            "🔍 [bold cyan]Navigation:[/bold cyan] ↑/↓ arrows | [bold green]Enter:[/bold green] View details | [bold red]Escape:[/bold red] Return to menu",
            border_style="dim white",
            padding=(0, 1)
        )
        
        console.clear()
        console.print(table)
        console.print()
        console.print(instructions)
        
        # Get user input
        key = get_key()
        
        if key == 'UP':
            selected_index = max(0, selected_index - 1)
        elif key == 'DOWN':
            selected_index = min(len(history) - 1, selected_index + 1)
        elif key == 'ENTER':
            show_scan_details(history[selected_index])
        elif key == 'ESCAPE':
            break

def show_scan_details(scan_summary: Dict):
    """Show detailed view of a specific scan"""
    scan_data = load_scan_details(scan_summary["filename"])
    
    if not scan_data:
        console.print("[red]❌ Could not load scan details[/red]")
        console.print("[dim]Press any key to continue...[/dim]")
        get_key()
        return
    
    while True:
        console.clear()
        
        # Header info
        timestamp = format_timestamp(scan_data["timestamp"])
        header = Panel(
            f"📊 [bold cyan]Scan Details[/bold cyan]\n"
            f"   Date: [white]{timestamp}[/white]\n"
            f"   Organization: [green]{scan_data['organization']}[/green]",
            border_style="cyan",
            padding=(1, 2),
            title="[bold cyan]Infrastructure Snapshot[/bold cyan]",
            title_align="left"
        )
        
        # Workspace details table
        table = Table(
            title=f"Resources by Workspace ({scan_data['organization']})",
            show_header=True,
            header_style="bold magenta"
        )
        table.add_column("Workspace", style="cyan", no_wrap=True)
        table.add_column("Resources", style="green")
        table.add_column("Total", style="yellow")
        
        for workspace in scan_data["workspaces"]:
            resource_summary = workspace.get("resource_summary", "No resources")
            total_resources = workspace.get("resource_count", 0)
            
            table.add_row(
                workspace["name"],
                resource_summary,
                str(total_resources)
            )
        
        # Summary panel
        summary = Panel(
            f"📈 [bold white]Summary[/bold white]\n"
            f"   Total Workspaces: [cyan]{scan_data['summary']['total_workspaces']}[/cyan]\n"
            f"   Processed Successfully: [green]{scan_data['summary']['processed_workspaces']}[/green]\n"
            f"   Errors/Empty: [yellow]{scan_data['summary']['error_workspaces']}[/yellow]\n"
            f"   Total Resources: [blue]{scan_data['summary']['total_resources']}[/blue]",
            border_style="white",
            padding=(1, 2)
        )
        
        # Instructions
        instructions = Panel(
            "[bold red]Escape:[/bold red] Return to history list",
            border_style="dim white",
            padding=(0, 1)
        )
        
        console.print(header)
        console.print()
        console.print(table)
        console.print()
        console.print(summary)
        console.print()
        console.print(instructions)
        
        # Wait for escape key
        key = get_key()
        if key == 'ESCAPE':
            break

def show_post_scan_menu(org_name: str):
    """Show interactive menu after scan completion"""
    while True:
        console.print()
        
        # Create the post-scan menu with proper formatting
        console.print("""
╭────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│                                                                                                                │
│   What would you like to do?                                                                                   │
│                                                                                                                │
│   ╭─────────────────────────────╮         ░█████╗░░█████╗░████████╗░░░░░░░░██████╗░█████╗░░█████╗░███╗░██╗     │
│   │ [H] View scan history       │         ██╔══██╗██╔══██╗╚══██╔══╝░░░░░░██╔════╝██╔══██╗██╔══██╗████╗░██║     │
│   │ [R] Run another scan        │         ██║░░╚═╝███████║░░░██║░░░█████╗╚█████╗░██║░░╚═╝███████║██╔██╗██║     │
│   │ [Q] Quit                    │         ██║░░██╗██╔══██║░░░██║░░░╚════╝░╚═══██╗██║░░██╗██╔══██║██║╚████║     │
│   ╰─────────────────────────────╯         ╚█████╔╝██║░░██║░░░██║░░░░░░░░░██████╔╝╚█████╔╝██║░░██║██║░╚███║     │
│                                           ░╚════╝░╚═╝░░╚═╝░░░╚═╝░░░░░░░░░╚═════╝░░╚════╝░╚═╝░░╚═╝╚═╝░░╚══╝     │
│                                                                                                                │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
""")
        
        choice = Prompt.ask("Choose an option", choices=["h", "r", "q", "H", "R", "Q"], default="q").lower()
        
        if choice == "h":
            show_scan_history()
        elif choice == "r":
            return "run_again"
        elif choice == "q":
            console.print("\n[bold cyan]🐾 Thanks for using CatSCAN! Meow![/bold cyan]")
            return "quit"

def main():
    """Main execution function"""
    while True:
        print_banner()
        
        # Get configuration (interactive or environment)
        org_name, token = get_config()
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/vnd.api+json",
            "org_name": org_name  # Store for convenience
        }
        
        # Show scanning panel
        show_scanning_panel(org_name)
        
        # Store workspace data for history
        workspaces_data = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            
            # Fetch workspaces
            task = progress.add_task("Fetching workspaces...", total=None)
            workspaces = get_workspaces(headers)
            progress.update(task, completed=True)
            
            if not workspaces:
                console.print("[bold red]No workspaces found or error occurred[/bold red]")
                exit(1)
            
            console.print(f"[green]Found {len(workspaces)} workspaces[/green]\n")
            
            # Create table
            table = Table(
                title=f"📊 Deployed Resources by Workspace ({org_name})",
                show_header=True,
                header_style="bold magenta"
            )
            table.add_column("Workspace", style="cyan", no_wrap=True)
            table.add_column("Resources", style="green")
            table.add_column("Status", style="yellow")
            
            # Process each workspace
            processed_count = 0
            error_count = 0
            
            for ws in workspaces:
                name = ws["attributes"]["name"]
                ws_id = ws["id"]
                
                # Add rate limiting
                time.sleep(0.1)
                
                state_url = get_state_version(ws_id, headers)
                if not state_url:
                    table.add_row(name, "[dim]No state[/dim]", "🚫 No State")
                    workspaces_data.append({
                        "name": name,
                        "resource_summary": "No state",
                        "resource_count": 0,
                        "status": "no_state"
                    })
                    continue
                
                resource_counts = fetch_resources_from_state(state_url, headers)
                
                if not resource_counts:
                    table.add_row(name, "[dim]Empty/Error[/dim]", "⚠️ Empty")
                    workspaces_data.append({
                        "name": name,
                        "resource_summary": "Empty/Error",
                        "resource_count": 0,
                        "status": "error"
                    })
                    error_count += 1
                else:
                    resource_summary = format_resource_summary(resource_counts)
                    total_resources = sum(resource_counts.values())
                    table.add_row(name, resource_summary, f"✅ {total_resources}")
                    
                    workspaces_data.append({
                        "name": name,
                        "resource_summary": resource_summary,
                        "resource_count": total_resources,
                        "resource_details": resource_counts,
                        "status": "success"
                    })
                    processed_count += 1
        
        # Display results
        console.print(table)
        print()
        
        # Show completion summary
        completion_text = Text()
        completion_text.append("✅ ", style="bold green")
        completion_text.append("Scan Complete!", style="bold white")
        completion_text.append(f"\n   Successfully processed: ", style="dim white")
        completion_text.append(f"{processed_count}", style="bold green")
        completion_text.append(f" workspaces", style="dim white")
        
        if error_count > 0:
            completion_text.append(f"\n   Empty/Error workspaces: ", style="dim white")
            completion_text.append(f"{error_count}", style="bold yellow")
        
        console.print(Panel(
            completion_text,
            border_style="green",
            padding=(1, 2),
            title="[bold green]📊 Results Summary[/bold green]",
            title_align="left"
        ))
        
        # Save scan results to history
        if save_scan_results(org_name, workspaces_data, processed_count, error_count):
            console.print("[dim]💾 Scan results saved to history[/dim]")
        
        # Show post-scan menu
        action = show_post_scan_menu(org_name)
        
        if action == "quit":
            break
        elif action == "run_again":
            console.clear()
            continue

if __name__ == "__main__":
    main()