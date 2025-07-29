import asyncio
import shutil
from pathlib import Path
from typing import Optional

import typer

from .agent import get_main_agent
from .config import ConfigManager, ConfigModel
from .message import SystemMessage
from .prompt.system import STATIC_SYSTEM_PROMPT, get_system_prompt_dynamic_part
from .session import Session
from .tui import ColorStyle, Text, console, render_hello, render_logo, render_tips
from .user_input import user_select
from .utils.exception import format_exception
from .utils.str_utils import format_relative_time

app = typer.Typer(help='Coding Agent CLI', add_completion=False)


def setup_config(**kwargs) -> ConfigModel:
    config_manager = ConfigManager.setup(**kwargs)
    config_model = config_manager.get_config_model()
    if hasattr(config_model, 'theme') and config_model.theme:
        console.set_theme(config_model.theme.value)
    return config_model


async def get_session(ctx: typer.Context) -> Optional[Session]:
    if ctx.obj['continue_latest']:
        # --continue
        session = Session.get_latest_session(Path.cwd())
        if not session:
            console.print(Text(f'No session found in {Path.cwd()}', style=ColorStyle.ERROR))
            return None
        session = session.create_new_session()
    elif ctx.obj['resume']:
        # --resume
        sessions = Session.load_session_list(Path.cwd())
        if not sessions or len(sessions) == 0:
            console.print(Text(f'No session found in {Path.cwd()}', style=ColorStyle.ERROR))
            return None
        options = []
        for idx, session in enumerate(sessions):
            title_msg = session.get('title_msg', '')[:20]
            message_count = session.get('message_count', 0)
            modified_at = format_relative_time(session.get('updated_at'))
            created_at = format_relative_time(session.get('created_at'))
            option = f'{idx + 1:3}.{modified_at:>10}{created_at:>9}{message_count:>12}  {title_msg:<20}'
            options.append(option)
        header = f'{" " * 4}{"Modified":>10}{"Created":>9}{"# Messages":>12}  Title'
        idx = await user_select(
            options,
            title=header,
        )
        if idx is None:
            return None
        session = Session.load(sessions[idx].get('id'))
    else:
        session = Session(
            Path.cwd(),
            messages=[
                SystemMessage(content=STATIC_SYSTEM_PROMPT, cached=True),
                SystemMessage(content=get_system_prompt_dynamic_part(Path.cwd(), ctx.obj['config'].model_name)),
            ],
        )
    return session


async def main_async(ctx: typer.Context):
    session = await get_session(ctx)
    if not session:
        return
    agent = await get_main_agent(session, config=ctx.obj['config'], enable_mcp=ctx.obj['mcp'])
    try:
        if ctx.obj['prompt']:
            await agent.headless_run(ctx.obj['prompt'])
        else:
            width, _ = shutil.get_terminal_size()
            has_session = (Path.cwd() / '.klaude' / 'sessions').exists()
            auto_show_logo = not has_session
            console.print(render_hello(show_info=not auto_show_logo))
            if (auto_show_logo or ctx.obj['logo']) and width >= 49:  # MIN LENGTH REQUIRED FOR LOGO
                console.print()
                console.print(render_logo('KLAUDE', ColorStyle.CLAUDE))
                console.print(render_logo('CODE', ColorStyle.CLAUDE))
            console.print()
            console.print(render_tips())
            try:
                await agent.chat_interactive()
            finally:
                # Show token usage statistics
                console.print()
                agent.print_usage()
                console.print(Text('\nBye!', style=ColorStyle.CLAUDE))
    except KeyboardInterrupt:
        pass


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    prompt: Optional[str] = typer.Option(None, '-p', '--print', help='Run in headless mode with the given prompt'),
    resume: bool = typer.Option(
        False,
        '-r',
        '--resume',
        help='Resume from an existing session (only for interactive mode)',
    ),
    continue_latest: bool = typer.Option(
        False,
        '-c',
        '--continue',
        help='Continue from the latest session in current directory',
    ),
    api_key: Optional[str] = typer.Option(None, '--api-key', help='Override API key from config'),
    model: Optional[str] = typer.Option(None, '--model', help='Override model name from config'),
    base_url: Optional[str] = typer.Option(None, '--base-url', help='Override base URL from config'),
    max_tokens: Optional[int] = typer.Option(None, '--max-tokens', help='Override max tokens from config'),
    model_azure: Optional[bool] = typer.Option(None, '--model-azure', help='Override model is azure from config'),
    thinking: Optional[bool] = typer.Option(
        None,
        '--thinking',
        help='Enable Claude Extended Thinking capability (only for Anthropic Offical API yet)',
    ),
    api_version: Optional[str] = typer.Option(None, '--api-version', help='Override API version from config'),
    extra_header: Optional[str] = typer.Option(None, '--extra-header', help='Override extra header from config (JSON string)'),
    extra_body: Optional[str] = typer.Option(None, '--extra-body', help='Override extra body from config (JSON string)'),
    mcp: bool = typer.Option(False, '--mcp', help='Enable MCP (Model Context Protocol) tools'),
    logo: bool = typer.Option(False, '--logo', help='Show logo'),
):
    ctx.ensure_object(dict)
    if ctx.invoked_subcommand is None:
        try:
            config_model = setup_config(
                api_key=api_key,
                model_name=model,
                base_url=base_url,
                model_azure=model_azure,
                max_tokens=max_tokens,
                enable_thinking=thinking,
                api_version=api_version,
                extra_header=extra_header,
                extra_body=extra_body,
            )
        except ValueError as e:
            console.print(Text(f'Error: {format_exception(e)}', style=ColorStyle.ERROR))
            raise typer.Exit(code=1)

        ctx.obj['prompt'] = prompt
        ctx.obj['resume'] = resume
        ctx.obj['continue_latest'] = continue_latest
        ctx.obj['mcp'] = mcp
        ctx.obj['config'] = config_model
        ctx.obj['logo'] = logo
        asyncio.run(main_async(ctx))


config_app = typer.Typer(help='Manage global configuration')
app.add_typer(config_app, name='config')


@config_app.command('show')
def config_show():
    """
    Show global configuration
    """
    config_manager = ConfigManager.setup()
    console.print(config_manager)


@config_app.command('edit')
def config_edit():
    """
    Init or edit global configuration file
    """
    from .config import GlobalConfigSource

    GlobalConfigSource.edit_config_file()


mcp_app = typer.Typer(help='Manage MCP (Model Context Protocol) servers')
app.add_typer(mcp_app, name='mcp')


@mcp_app.command('show')
def mcp_show():
    """Show current MCP configuration and available tools"""
    import asyncio

    from .mcp.mcp_tool import MCPManager

    _ = setup_config()

    async def show_mcp_info():
        mcp_manager = MCPManager()
        try:
            await mcp_manager.initialize()
            console.print(mcp_manager)
        except Exception as e:
            console.print(Text(f'Error connecting to MCP servers: {format_exception(e)}', style=ColorStyle.ERROR))
        finally:
            await mcp_manager.shutdown()

    asyncio.run(show_mcp_info())


@mcp_app.command('edit')
def mcp_edit():
    """Init or edit MCP configuration file"""
    from .mcp.mcp_config import MCPConfigManager

    config_manager = MCPConfigManager()
    config_manager.edit_config_file()


@app.command('version')
def version_command():
    """Show version information"""
    # Import here to avoid circular imports
    from importlib.metadata import version

    try:
        pkg_version = version('klaude-code')
        console.print(Text(f'klaude-code {pkg_version}', style=ColorStyle.SUCCESS))
    except Exception:
        console.print(Text('klaude-code (development)', style=ColorStyle.SUCCESS))


@app.command('update')
def update_command():
    """Update klaude-code to the latest version"""
    import subprocess
    import sys

    console.print(Text('Updating klaude-code...', style=ColorStyle.INFO))

    try:
        # Try uv first (recommended)
        result = subprocess.run(['uv', 'tool', 'upgrade', 'klaude-code'], capture_output=True, text=True)
        if result.returncode == 0:
            console.print(Text('✓ Updated successfully with uv', style=ColorStyle.SUCCESS))
            return
    except FileNotFoundError:
        pass

    try:
        # Fallback to pip
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'klaude-code'], capture_output=True, text=True)
        if result.returncode == 0:
            console.print(Text('✓ Updated successfully with pip', style=ColorStyle.SUCCESS))
        else:
            console.print(Text(f'✗ Update failed: {result.stderr}', style=ColorStyle.ERROR))
    except Exception as e:
        console.print(Text(f'✗ Update failed: {format_exception(e)}', style=ColorStyle.ERROR))
