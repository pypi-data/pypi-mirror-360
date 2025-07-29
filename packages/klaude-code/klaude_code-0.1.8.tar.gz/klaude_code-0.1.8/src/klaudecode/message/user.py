from enum import Enum
from typing import List, Literal, Optional

from anthropic.types import MessageParam
from openai.types.chat import ChatCompletionMessageParam
from rich.rule import Rule
from rich.text import Text

from ..tui import ColorStyle, render_message, render_suffix
from ..utils.file_utils import get_relative_path_for_display
from .base import BasicMessage


class SpecialUserMessageTypeEnum(Enum):
    INTERRUPTED = 'interrupted'
    COMPACT_RESULT = 'compact_result'


class UserMessage(BasicMessage):
    role: Literal['user'] = 'user'
    pre_system_reminders: Optional[List[str]] = None
    post_system_reminders: Optional[List[str]] = None
    user_msg_type: Optional[str] = None
    user_raw_input: Optional[str] = None

    def get_content(self):
        from .registry import _USER_MSG_CONTENT_FUNCS

        content_list = []
        if self.pre_system_reminders:
            for reminder in self.pre_system_reminders:
                content_list.append(
                    {
                        'type': 'text',
                        'text': reminder,
                    }
                )

        main_content = self.content
        if self.user_msg_type and self.user_msg_type in _USER_MSG_CONTENT_FUNCS:
            main_content = _USER_MSG_CONTENT_FUNCS[self.user_msg_type](self)

        content_list.append(
            {
                'type': 'text',
                'text': main_content,
            }
        )

        # Add attachments as separate content items
        if self.attachments:
            for attachment in self.attachments:
                content_list.extend(attachment.get_content())

        if self.post_system_reminders:
            for reminder in self.post_system_reminders:
                content_list.append(
                    {
                        'type': 'text',
                        'text': reminder,
                    }
                )
        return content_list

    def to_openai(self) -> ChatCompletionMessageParam:
        return {'role': 'user', 'content': self.get_content()}

    def to_anthropic(self) -> MessageParam:
        return MessageParam(role='user', content=self.get_content())

    def __rich_console__(self, console, options):
        from .registry import _USER_MSG_RENDERERS

        if not self.user_msg_type or self.user_msg_type not in _USER_MSG_RENDERERS:
            yield render_message(Text(self.content), mark='>')
        else:
            yield from _USER_MSG_RENDERERS[self.user_msg_type](self)
        yield from self.get_suffix_renderable()

    def get_suffix_renderable(self):
        from .registry import _USER_MSG_SUFFIX_RENDERERS

        if self.user_msg_type and self.user_msg_type in _USER_MSG_SUFFIX_RENDERERS:
            yield from _USER_MSG_SUFFIX_RENDERERS[self.user_msg_type](self)

        # Render attachments
        if self.attachments:
            for attachment in self.attachments:
                display_path = get_relative_path_for_display(attachment.path)

                if attachment.type == 'directory':
                    attachment_text = Text.assemble('Listed directory ', (display_path, 'bold'))
                elif attachment.type == 'image':
                    attachment_text = Text.assemble('Read image ', (display_path, 'bold'), f' ({attachment.size_str})' if attachment.size_str else '')
                else:
                    attachment_text = Text.assemble('Read ', (display_path, 'bold'), f' ({attachment.line_count} lines)')
                yield render_suffix(attachment_text)

        if self.get_extra_data('error_msgs'):
            for error in self.get_extra_data('error_msgs'):
                yield render_suffix(error, style=ColorStyle.ERROR)

    def __bool__(self):
        return not self.removed and bool(self.content)

    def append_pre_system_reminder(self, reminder: str):
        if not self.pre_system_reminders:
            self.pre_system_reminders = [reminder]
        else:
            self.pre_system_reminders.append(reminder)

    def append_post_system_reminder(self, reminder: str):
        if not self.post_system_reminders:
            self.post_system_reminders = [reminder]
        else:
            self.post_system_reminders.append(reminder)


INTERRUPTED_MSG = 'Interrupted by user'


def interrupted_renderer(user_msg: 'UserMessage'):
    yield render_message(INTERRUPTED_MSG, style=ColorStyle.ERROR, mark='>', mark_style=ColorStyle.ERROR)


def compact_renderer(user_msg: 'UserMessage'):
    yield Rule(title=Text('Previous Conversation Compacted', ColorStyle.HIGHLIGHT.bold), characters='=', style=ColorStyle.HIGHLIGHT)
    yield render_message(user_msg.content, mark='✻', mark_style=ColorStyle.AI_THINKING, style=ColorStyle.AI_THINKING.italic, render_text=True)


def initialize_default_renderers():
    from .registry import register_user_msg_renderer

    register_user_msg_renderer(SpecialUserMessageTypeEnum.INTERRUPTED.value, interrupted_renderer)
    register_user_msg_renderer(SpecialUserMessageTypeEnum.COMPACT_RESULT.value, compact_renderer)


initialize_default_renderers()
