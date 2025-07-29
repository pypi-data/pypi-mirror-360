import asyncio
import threading
import traceback
from typing import Callable, List, Optional

from anthropic import AnthropicError
from openai import OpenAIError
from rich.text import Text

from . import user_command  # noqa: F401 # import user_command to trigger command registration
from .config import ConfigModel
from .llm import LLMManager
from .mcp.mcp_tool import MCPManager
from .message import INTERRUPTED_MSG, AgentUsage, AIMessage, SpecialUserMessageTypeEnum, ToolCall, ToolMessage, UserMessage
from .prompt.plan_mode import APPROVE_MSG, PLAN_MODE_REMINDER, REJECT_MSG
from .prompt.reminder import EMPTY_TODO_REMINDER, FILE_DELETED_EXTERNAL_REMINDER, FILE_MODIFIED_EXTERNAL_REMINDER, get_context_reminder
from .session import Session
from .tool import Tool, ToolHandler
from .tools import BASIC_TOOLS, ExitPlanModeTool, TodoWriteTool
from .tools.read import execute_read
from .tools.task import TaskToolMixin
from .tui import INTERRUPT_TIP, ColorStyle, console, render_dot_status, render_message, render_suffix
from .user_command import custom_command_manager
from .user_input import _INPUT_MODES, NORMAL_MODE_NAME, InputSession, UserInputHandler, user_select
from .utils.exception import format_exception
from .utils.file_utils import cleanup_all_backups

DEFAULT_MAX_STEPS = 100
TOKEN_WARNING_THRESHOLD = 0.85
COMPACT_THRESHOLD = 0.9
QUIT_COMMAND = ['quit', 'exit']


class Agent(TaskToolMixin, Tool):
    def __init__(
        self,
        session: Session,
        config: Optional[ConfigModel] = None,
        availiable_tools: Optional[List[Tool]] = None,
        print_switch: bool = True,
        enable_plan_mode_reminder: bool = True,
    ):
        self.session: Session = session
        self.config: Optional[ConfigModel] = config
        self.llm_manager: Optional[LLMManager] = None
        self.print_switch = print_switch

        # Plan Mode
        self.enable_plan_mode_reminder = enable_plan_mode_reminder
        self.plan_mode_activated: bool = False

        # Tools
        self.availiable_tools = availiable_tools
        self.tool_handler = ToolHandler(self, self.availiable_tools or [], show_live=print_switch)
        self.mcp_manager: Optional[MCPManager] = None

        self._interrupt_flag = threading.Event()  # Global interrupt flag for this agent

        # Usage tracking
        self.usage = AgentUsage()

        # User Input
        self.input_session = InputSession(session.work_dir)
        self.user_input_handler = UserInputHandler(self, self.input_session)
        # Initialize custom commands
        try:
            custom_command_manager.discover_and_register_commands(session.work_dir)
        except Exception as e:
            if self.print_switch:
                traceback.print_exc()
                console.print(f'Warning: Failed to load custom commands: {format_exception(e)}', style=ColorStyle.WARNING)

    async def chat_interactive(self, first_message: str = None):
        self._initialize_llm()

        self.session.messages.print_all_message()  # For continue and resume scene.

        epoch = 0
        try:
            while True:
                # Clear interrupt flag at the start of each interaction
                self._clear_interrupt()

                if epoch == 0 and first_message:
                    user_input_text = first_message
                else:
                    user_input_text = await self.input_session.prompt_async()
                if user_input_text.strip().lower() in QUIT_COMMAND:
                    break
                need_agent_run = await self.user_input_handler.handle(user_input_text, print_msg=bool(first_message))
                if need_agent_run:
                    if epoch == 0:
                        self._handle_claudemd_reminder()
                        self._handle_empty_todo_reminder()
                    await self.run(max_steps=DEFAULT_MAX_STEPS, tools=self._get_all_tools())
                else:
                    self.session.save()
                epoch += 1
        finally:
            self.session.save()
            # Clean up MCP resources
            if self.mcp_manager:
                await self.mcp_manager.shutdown()
            # Clean up backup files
            cleanup_all_backups()

    async def run(self, max_steps: int = DEFAULT_MAX_STEPS, check_interrupt: Callable[[], bool] = None, tools: Optional[List[Tool]] = None):
        try:
            usage_token_count = 0
            for _ in range(max_steps):
                # Check if task was canceled (for subagent execution)
                if check_interrupt and check_interrupt():
                    return INTERRUPTED_MSG

                # Check token count and compact if necessary
                await self._auto_compact_conversation(tools, usage_token_count)

                if self.enable_plan_mode_reminder:
                    self._handle_plan_mode_reminder()
                self._handle_file_external_modified_reminder()

                self.session.save()

                ai_msg = await self.llm_manager.call(
                    msgs=self.session.messages,
                    tools=tools,
                    show_status=self.print_switch,
                    interrupt_check=self._should_interrupt,
                )
                ai_msg: AIMessage
                if ai_msg.usage:
                    usage_token_count = (ai_msg.usage.prompt_tokens or 0) + (ai_msg.usage.completion_tokens or 0)
                self.usage.update(ai_msg)
                self.session.append_message(ai_msg)
                if ai_msg.finish_reason == 'stop':
                    # Cannot directly use this AI response's content as result,
                    # because Claude might execute a tool call (e.g. TodoWrite) at the end and return empty content
                    last_ai_msg = self.session.messages.get_last_message(role='assistant', filter_empty=True)
                    self.session.save()
                    return last_ai_msg.content if last_ai_msg else ''
                if ai_msg.finish_reason == 'tool_calls' or len(ai_msg.tool_calls) > 0:
                    if not await self._handle_exit_plan_mode(ai_msg.tool_calls):
                        return 'Plan mode maintained, awaiting further instructions.'
                    # Update tool handler with MCP tools
                    self._update_tool_handler_tools(tools)
                    await self.tool_handler.handle(ai_msg)

        except (OpenAIError, AnthropicError) as e:
            console.print(render_suffix(f'LLM error: {format_exception(e)}', style=ColorStyle.ERROR))
            return f'LLM error: {format_exception(e)}'
        except (KeyboardInterrupt, asyncio.CancelledError):
            # Clear any live displays before handling interruption
            return self._handle_interruption()
        except Exception as e:
            traceback.print_exc()
            console.print(render_suffix(f'Error: {format_exception(e)}', style=ColorStyle.ERROR))
            return f'Error: {format_exception(e)}'
        max_step_msg = f'Max steps {max_steps} reached'
        if self.print_switch:
            console.print(render_message(max_step_msg, mark_style=ColorStyle.INFO))
        return max_step_msg

    def _handle_claudemd_reminder(self):
        reminder = get_context_reminder(self.session.work_dir)
        last_user_msg = self.session.messages.get_last_message(role='user')
        if last_user_msg and isinstance(last_user_msg, UserMessage):
            last_user_msg.append_pre_system_reminder(reminder)

    def _handle_empty_todo_reminder(self):
        if TodoWriteTool in self.availiable_tools:
            last_msg = self.session.messages.get_last_message(filter_empty=True)
            if last_msg and isinstance(last_msg, (UserMessage, ToolMessage)):
                last_msg.append_post_system_reminder(EMPTY_TODO_REMINDER)

    def _handle_plan_mode_reminder(self):
        if not self.plan_mode_activated:
            return
        last_msg = self.session.messages.get_last_message(filter_empty=True)
        if last_msg and isinstance(last_msg, (UserMessage, ToolMessage)):
            last_msg.append_post_system_reminder(PLAN_MODE_REMINDER)

    def _handle_file_external_modified_reminder(self):
        modified_files = self.session.file_tracker.get_all_modified()
        if not modified_files:
            return

        last_msg = self.session.messages.get_last_message(filter_empty=True)
        if not last_msg or not isinstance(last_msg, (UserMessage, ToolMessage)):
            return

        for file_path in modified_files:
            try:
                result = execute_read(file_path, tracker=self.session.file_tracker)
                if result.success:
                    reminder = FILE_MODIFIED_EXTERNAL_REMINDER.format(file_path=file_path, file_content=result.content)
                    last_msg.append_post_system_reminder(reminder)
                else:
                    reminder = FILE_DELETED_EXTERNAL_REMINDER.format(file_path=file_path)
                    last_msg.append_post_system_reminder(reminder)
            except Exception:
                reminder = FILE_DELETED_EXTERNAL_REMINDER.format(file_path=file_path)
                last_msg.append_post_system_reminder(reminder)

    async def _handle_exit_plan_mode(self, tool_calls: List[ToolCall]) -> bool:
        exit_plan_call: Optional[ToolCall] = next((call for call in tool_calls.values() if call.tool_name == ExitPlanModeTool.get_name()), None)
        if not exit_plan_call:
            return True
        exit_plan_call.status = 'success'
        console.print(exit_plan_call)
        # Ask user for confirmation
        options = ['Yes', 'No, keep planning']
        selection = await user_select(options, 'Would you like to proceed?')
        approved = selection == 0
        if approved:
            if hasattr(self, 'input_session') and self.input_session:
                self.input_session.current_input_mode = _INPUT_MODES[NORMAL_MODE_NAME]
            self.plan_mode_activated = False
        tool_msg = ToolMessage(tool_call_id=exit_plan_call.id, tool_call_cache=exit_plan_call, content=APPROVE_MSG if approved else REJECT_MSG)
        tool_msg.set_extra_data('approved', approved)
        console.print(*tool_msg.get_suffix_renderable())
        self.session.append_message(tool_msg)
        return approved

    def _handle_interruption(self):
        # Set the interrupt flag
        self._interrupt_flag.set()

        # Clean up any live displays
        asyncio.create_task(asyncio.sleep(0.1))
        if hasattr(console.console, '_live') and console.console._live:
            try:
                console.console._live.stop()
            except Exception as e:
                console.print(f'Error stopping live display: {format_exception(e)}')
                pass

        # Add interrupted message
        user_msg = UserMessage(content=INTERRUPTED_MSG, user_msg_type=SpecialUserMessageTypeEnum.INTERRUPTED.value)
        console.print()
        console.print(user_msg)
        self.session.append_message(user_msg)
        return INTERRUPTED_MSG

    def _should_interrupt(self) -> bool:
        """Check if the agent should be interrupted"""
        return self._interrupt_flag.is_set()

    def _clear_interrupt(self):
        """Clear the interrupt flag (for testing or reset)"""
        self._interrupt_flag.clear()

    def _initialize_llm(self):
        if not self.llm_manager:
            self.llm_manager = LLMManager()
        self.llm_manager.initialize_from_config(self.config)

    async def _auto_compact_conversation(self, tools: Optional[List[Tool]] = None, usage_token_count: int = 0):
        """Check token count and compact conversation history if necessary"""
        if not self.config or not self.config.context_window_threshold:
            return
        total_tokens = 0
        if usage_token_count > 0:
            total_tokens = usage_token_count
        else:
            messages_tokens = sum(msg.tokens for msg in self.session.messages if msg)
            tools_tokens = sum(tool.tokens() for tool in (tools or self.tools))
            total_tokens = messages_tokens + tools_tokens
        total_tokens += self.config.max_tokens.value
        if total_tokens > self.config.context_window_threshold.value * TOKEN_WARNING_THRESHOLD:
            console.print(
                Text(
                    f'Notice: total tokens: {total_tokens}, threshold: {self.config.context_window_threshold.value}',
                    style=ColorStyle.WARNING,
                )
            )
        if total_tokens > self.config.context_window_threshold.value * COMPACT_THRESHOLD:
            await self.session.compact_conversation_history(show_status=self.print_switch, llm_manager=self.llm_manager)

    async def headless_run(self, user_input_text: str, print_trace: bool = False):
        self._initialize_llm()

        try:
            # Clear any previous interrupt state
            self._clear_interrupt()
            need_agent_run = await self.user_input_handler.handle(user_input_text, print_msg=False)
            if not need_agent_run:
                return
            self.print_switch = print_trace
            self.tool_handler.show_live = print_trace
            if print_trace:
                await self.run(tools=self._get_all_tools())
                return
            status = render_dot_status('Running')
            status.start()
            running = True

            async def update_status():
                while running:
                    tool_msg_count = len([msg for msg in self.session.messages if msg.role == 'tool'])
                    status.update(
                        description=Text.assemble(
                            Text.from_markup(f'([bold]{tool_msg_count}[/bold] tool uses) '),
                            (INTERRUPT_TIP, ColorStyle.MUTED),
                        ),
                    )
                    await asyncio.sleep(0.1)

            update_task = asyncio.create_task(update_status())
            try:
                result = await self.run(tools=self._get_all_tools())
            finally:
                running = False
                status.stop()
                update_task.cancel()
                try:
                    await update_task
                except asyncio.CancelledError:
                    pass
            console.print(result)
        finally:
            self.session.save()
            # Clean up MCP resources
            if self.mcp_manager:
                await self.mcp_manager.shutdown()
            # Clean up backup files
            cleanup_all_backups()

    async def initialize_mcp(self) -> bool:
        """Initialize MCP manager"""
        if self.mcp_manager is None:
            self.mcp_manager = MCPManager(self.session.work_dir)
            return await self.mcp_manager.initialize()
        return True

    def _get_all_tools(self) -> List[Tool]:
        """Get all available tools including MCP tools"""
        tools = self.availiable_tools.copy() if self.availiable_tools else []

        # Add MCP tools
        if self.mcp_manager and self.mcp_manager.is_initialized():
            mcp_tools = self.mcp_manager.get_mcp_tools()
            tools.extend(mcp_tools)

        return tools

    def _update_tool_handler_tools(self, tools: List[Tool]):
        """Update ToolHandler's tool dictionary"""
        self.tool_handler.tool_dict = {tool.name: tool for tool in tools} if tools else {}

    def print_usage(self):
        console.print()
        console.print(self.usage)


async def get_main_agent(session: Session, config: ConfigModel, enable_mcp: bool = False) -> Agent:
    agent = Agent(session, config, availiable_tools=[Agent] + BASIC_TOOLS)
    if enable_mcp:
        await agent.initialize_mcp()
    return agent
