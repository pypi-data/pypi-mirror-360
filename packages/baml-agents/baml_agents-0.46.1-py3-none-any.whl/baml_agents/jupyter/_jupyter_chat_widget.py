"""
Jupyter Chat Widget.

Source: https://github.com/darinkist/MediumArticle_InteractiveChatGPTSessionsInJupyterNotebook

MIT License

Copyright (c) 2023 darinkist

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import asyncio
import datetime
import traceback
from collections.abc import Awaitable, Callable
from typing import Literal

from IPython.display import HTML, display
from ipywidgets import widgets
from pydantic import BaseModel, ConfigDict


class ChatMessage(BaseModel):
    content: str
    role: Literal["user", "assistant"]
    model_config = ConfigDict(frozen=True)


class JupyterChatWidget:
    def __init__(
        self,
        message_callback: (
            Callable[[list[ChatMessage]], Awaitable[list[ChatMessage]]] | None
        ),
        *,
        chat_history: list[ChatMessage] | None = None,
        user_label: str = "User",
        assistant_label: str = "Agent",
    ):
        self._chat_messages: list[ChatMessage] = []

        self._setup_css()
        self.output = widgets.Output()

        # Change to TextArea which often has better copy-paste support
        self.in_text = widgets.Textarea(
            placeholder="Type your message here...",
            layout=widgets.Layout(width="100%", height="60px"),
        )
        self.in_text.continuous_update = False

        # Add a button for sending messages as an alternative input method
        self.send_button = widgets.Button(
            description="Send", button_style="primary", icon="paper-plane"
        )
        self.send_button.on_click(self._handle_button_click)

        # Set up keyboard event handling
        self._setup_keyboard_handling()

        # Simple text loading indicator
        self.loading_bar = widgets.HTML("Loading...")
        self.loading_bar.layout.display = "none"

        self.message_callback = message_callback
        self.user_label = user_label
        self.assistant_label = assistant_label

        # Display initial chat history if provided
        if chat_history:
            for item in chat_history:
                self._add_message(content=item.content, role=item.role)

    async def run(self, initial_message: str | None = None):
        """
        Display the widget and optionally send an initial message.
        This method is awaitable and returns immediately after optional initial message is sent.
        """
        self.display()
        if initial_message and self.message_callback:
            await self._send_message(initial_message)

    async def _execute_with_loading(self, coroutine_func, *args, **kwargs):
        self.loading_bar.layout.display = "block"
        try:
            return await coroutine_func(*args, **kwargs)
        except Exception:  # noqa: BLE001
            traceback.print_exc()
            return None
        finally:
            self.loading_bar.layout.display = "none"

    def _add_message(self, content, role):
        """Add a message to the chat history."""
        self._chat_messages.append(ChatMessage(content=content, role=role))
        self._display_message(content, role)

    def _setup_keyboard_handling(self):
        # JavaScript to capture Shift+Enter to send messages
        js_code = """
        function captureEnter(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                document.getElementById('send-button').click();
                return false;
            }
            return true;
        }

        setTimeout(function() {
            var textareas = document.getElementsByClassName('jupyter-widgets-output-area')[0]
                            .getElementsByTagName('textarea');
            if (textareas.length > 0) {
                var textarea = textareas[textareas.length-1];
                textarea.addEventListener('keydown', captureEnter);
            }
        }, 1000);
        """

        display(
            HTML(
                f"""
        <script>
        {js_code}
        </script>
        """
            )
        )

    def _setup_css(self):
        display(
            HTML(
                """
        <link rel="stylesheet"
              href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css"
              integrity="sha384-TX8t27EcRE3e/ihU7zmQxVncDAy5uIKz4rEkgIXeMed4M0jlfIDPvg6uqKI2xXr2"
              crossorigin="anonymous">
        <style>
            body{margin-top:20px;}

            .chat-message-left,
            .chat-message-right {
                display: flex;
                flex-shrink: 0
            }

            .chat-message-left {
                margin-right: auto
            }

            .chat-message-right {
                flex-direction: row-reverse;
                margin-left: auto
            }

            .time-stamp {
                margin-left: 10px;
                margin-right: 10px;
                align-self: flex-end;
            }

            /* Make the textarea more responsive to copy/paste */
            .jupyter-widgets textarea {
                font-family: inherit;
                line-height: normal;
                resize: none;
                padding: 8px;
            }
        </style>
        """
            )
        )

    def display(self):
        display(
            widgets.HBox(
                [self.output],
                layout=widgets.Layout(
                    width="100%",
                    max_height="500px",
                    display="inline-flex",
                    flex_flow="column-reverse",
                ),
            )
        )

        # Modify the input area to use a button + textarea
        display(
            widgets.Box(
                children=[self.loading_bar, self.in_text, self.send_button],
                layout=widgets.Layout(
                    display="flex", flex_flow="row", align_items="center", width="100%"
                ),
            )
        )

        # Assign ID to the send button for JavaScript to find it
        display(
            HTML(
                """
        <script>
        document.querySelector(".jupyter-button:last-child").id = "send-button";
        </script>
        """
            )
        )

    def _handle_button_click(self, _):
        """Handle clicks on the send button."""
        return asyncio.create_task(self._send_message(self.in_text.value))

    async def _send_message(self, text):
        if not text or text.strip() == "":
            return

        question = text.strip()

        # Clear the input
        self.in_text.value = ""

        # Display user message in the UI
        self._add_message(content=question, role="user")

        # Validate callback is a coroutine function
        if not asyncio.iscoroutinefunction(self.message_callback):
            raise ValueError("message_callback must be a coroutine function")

        # Execute callback with loading indicator
        response = await self._execute_with_loading(
            self.message_callback, self._chat_messages[:]
        )

        # Display the assistant response
        if response:
            for item in response:
                self._add_message(item.content, item.role)

        # Focus back to the input textarea
        display(
            HTML(
                """
        <script>
        document.querySelector(".jupyter-widgets textarea:last-of-type").focus();
        </script>
        """
            )
        )

    def _display_message(self, content, role):
        # No longer maintaining internal chat history
        content_formatted = content.replace("$", r"\$")

        # Determine if message should be displayed as user or non-user (assistant)
        is_user = role == "user"

        # Set alignment based on user status
        message_class = "chat-message-left" if is_user else "chat-message-right"

        # Display the actual role in the UI
        display_label = self.user_label if is_user else (self.assistant_label)

        timestamp = datetime.datetime.now(datetime.UTC).strftime("%H:%M:%S")
        html = (
            f'<div class="{message_class} pb-4">'
            '<div class="flex-shrink-1 bg-light rounded py-2 px-3 ml-3">'
            f'<div class="font-weight-bold mb-1">{display_label}</div>{content_formatted}</div>'
            f'<div class="text-muted small time-stamp">{timestamp}</div></div>'
        )
        self.output.append_display_data(HTML(html))

    def _clear_chat(self):
        self.output.clear_output()

