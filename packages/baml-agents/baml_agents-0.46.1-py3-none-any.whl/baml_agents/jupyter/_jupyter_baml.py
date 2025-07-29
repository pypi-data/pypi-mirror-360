import asyncio
import html
import inspect
import json
import uuid
from collections.abc import Callable
from pprint import pformat
from typing import Any, Generic, Literal, TypeVar, cast

from baml_py import Collector
from IPython.display import Javascript, display

from baml_agents._utils._sole import sole

from ._jupyter_button_hide import (
    hide_text_under_a_button,
    hide_text_under_a_button_nested,
)
from ._token_cost_estimator import TokenCostEstimator

T = TypeVar("T")


def _format_price_and_duration(
    cost_usd_per_thousand: float, duration_ms: int | None
) -> str:
    duration_sec = f"{duration_ms/1000:.2f}s" if duration_ms is not None else "N/A"
    return f"{cost_usd_per_thousand:.2f}$/1k | {duration_sec}"


def _get_call_duration_ms(call) -> int | None:
    timing = getattr(call, "timing", None)
    if timing is not None:
        return getattr(timing, "duration_ms", None)
    return None


def _get_log_duration_ms(log) -> int | None:
    timing = getattr(log, "timing", None)
    if timing is not None:
        return getattr(timing, "duration_ms", None)
    return None


class JupyterOutputBox:
    """
    Context manager that:
      - Renders pretty <pre> formatted output (preserves whitespace and newlines).
      - Updates the content efficiently via Jupyter's display_id mechanism.
      - Removes the HTML element on exit, hiding the output when done.
    """

    def __init__(
        self,
        initial_message: str = "Initializing…",
        *,
        display_id: str | None = None,
        clear_after_finish: bool = True,
    ):
        self.display_id = display_id or f"stream-{uuid.uuid4()}"
        self.clear_after_finish = clear_after_finish
        escaped_msg = html.escape(initial_message, quote=False)
        self._initial_html = f'<pre id="{self.display_id}">{escaped_msg}</pre>'
        self._active = False
        self._handle = None

    def __enter__(self):
        if not self._active:
            self._handle = display(
                {"text/html": self._initial_html},
                display_id=self.display_id,
                raw=True,
            )
            self._active = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.clear_after_finish and self._active:
            js = f"""
            (function(){{
              var el = document.getElementById("{self.display_id}");
              if (el) el.remove();
            }})();
            """
            display(Javascript(js))
        self._active = False
        self._handle = None

    def update(self, data, *, use_br: bool = False):
        if not isinstance(data, str):
            try:
                s = data.model_dump_json(indent=4)
            except AttributeError:
                s = json.dumps(data, indent=4)
        else:
            s = data

        escaped = html.escape(s, quote=False)

        if use_br:
            html_body = escaped.replace("\n", "<br>")
            new_html = (
                f'<div id="{self.display_id}" style="font-family:monospace">'
                f"{html_body}</div>"
            )
        else:
            new_html = f'<pre id="{self.display_id}">{escaped}</pre>'

        if self._handle is None:
            raise RuntimeError(
                "Display handle is None. Did you forget to enter the context manager?"
            )
        self._handle.update({"text/html": new_html}, raw=True)

    def display(
        self,
        formatter: Literal["json", "pformat"] | Callable[[Any], None] | None = None,
    ):
        formatter = formatter or "pformat"

        def update_result(result):
            if formatter == "json":
                try:
                    s = result.model_dump_json(indent=4)
                except AttributeError:
                    s = json.dumps(result, indent=4)
                self.update(s)
            elif formatter == "pformat":
                self.update(pformat(result.model_dump(), width=200, sort_dicts=False))
            elif callable(formatter):
                formatter(result)
            else:
                raise ValueError(f"Unknown formatter: {formatter}")

        return update_result


class _StreamingInterceptorWrapper:
    def __init__(self, ai: Any, callback: Callable, /):
        self._ai = ai
        self._callback = callback

    def __getattribute__(self, name: str) -> Any:
        # Use object.__getattribute__ to access instance variables directly
        # to avoid recursive calls to this __getattribute__ method.
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            # If the attribute is not directly on the wrapper, get it from the wrapped object.
            pass

        ai_instance = object.__getattribute__(self, "_ai")
        callback = object.__getattribute__(self, "_callback")

        # Special handling for methods required by the wrapper itself or python internals
        # Note: __getattr__ might be simpler if we only intercept non-dunder methods.
        # But __getattribute__ is more powerful for intercepting *everything*.
        if name in {
            "_ai",
            "_callback",
            "__class__",
            "__init__",
            "__getattribute__",
            "__setattr__",  # Added for completeness, though not strictly needed for the example
            "__delattr__",  # Added for completeness
            "__dict__",
            "__dir__",  # Often useful to proxy dir() calls
            "__repr__",  # Might want to customize repr
            "__str__",  # Might want to customize str
            # Async specific methods often checked by libraries
            "__await__",
            "__aiter__",
            "__anext__",
            "__aenter__",
            "__aexit__",
        }:
            # If it's one of our internal/special methods, get it directly from self
            # This was handled by the try/except block above now. Redundant but kept for clarity.
            return object.__getattribute__(self, name)

        # Get the attribute from the *stream* property of the wrapped object
        # This is specific to the Streaming Interceptor's logic
        attr = getattr(ai_instance.stream, name)

        # Only wrap if it's callable (likely a method)
        if not callable(attr):
            return attr  # Return non-callable attributes directly

        # --- Streaming Specific Wrapping Logic ---
        # This wrapper assumes the underlying method is async and returns a stream
        async def stream_wrapper(*args, **kwargs):
            stream_obj = attr(*args, **kwargs)
            async for partial in stream_obj:
                callback(partial)
            # Ensure get_final_response exists and is awaitable if needed
            # This part might need adjustment based on the actual stream object interface
            final_response = None
            if hasattr(
                stream_obj, "get_final_response"
            ) and inspect.iscoroutinefunction(stream_obj.get_final_response):
                final_response = await stream_obj.get_final_response()
                callback(final_response)
            # What if get_final_response doesn't exist or isn't async? Need fallback?
            # For now, assume it exists and is async as per the original code.
            return (
                final_response  # Or maybe the stream_obj itself if no final response?
            )

        # Copy metadata
        stream_wrapper.__name__ = name
        stream_wrapper.__qualname__ = f"{type(self).__name__}.{name}"
        stream_wrapper.__doc__ = getattr(attr, "__doc__", None)
        stream_wrapper.__annotations__ = getattr(attr, "__annotations__", {})
        # Consider adding functools.wraps for more robust metadata copying

        return stream_wrapper


class JupyterBamlCollector(Generic[T]):
    def __init__(
        self,
        ai: T,
        *,
        stream_callback: Callable | None = None,
        intent_summarizer: Callable | None = None,
    ):
        self._original_ai = ai
        self.collector = Collector(name="collector")
        self._ai = self._original_ai.with_options(collector=self.collector)  # type: ignore
        self.cost_estimator = TokenCostEstimator()
        self._stream_callback = stream_callback
        self._intent_summarizer = intent_summarizer

    @property
    def ai(self) -> T:
        if self._stream_callback:
            return _StreamingInterceptorWrapper(self._ai, self._stream_callback)  # type: ignore
        return self._ai

    @property
    def b(self) -> T:
        return self.ai

    @staticmethod
    def _format_log_messages(messages):
        prompt_parts = []
        for message in messages:
            content = sole(message["content"])
            if content["type"] != "text":
                raise ValueError(
                    f"Expected content type 'text', but got '{content['type']}'"
                )
            prompt_parts.append(f"[{message['role']}]\n{content['text']}")
        return "\n\n".join(prompt_parts)

    def _get_prompt_buttons(self, calls, *, omit_cost_and_model: bool = False):
        ret = {}
        for call in calls:
            request_body = call.http_request.body.json()
            messages = request_body["messages"]

            cost = self.cost_estimator.calculate_cost(
                request_body["model"],
                call.usage.input_tokens,
                call.usage.output_tokens,
            )
            cost_usd_per_thousand = cost["total_cost_usd"] * 1_000
            duration_ms = _get_call_duration_ms(call)

            formatted = self._format_log_messages(messages)
            if omit_cost_and_model:
                label = f"Prompt | messages={len(messages)} |"
            else:
                price_and_duration = _format_price_and_duration(
                    cost_usd_per_thousand, duration_ms
                )
                label = (
                    f"Prompt | messages={len(messages)} | "
                    f"{price_and_duration} | {cost['model_info']['model_name']}"
                )
            ret[label] = formatted
        return ret

    async def _get_completion_button(
        self, raw_llm_response, log=None, *, omit_cost_and_model: bool = False
    ):
        summary_label = None
        if self._intent_summarizer is not None:
            summary_label = await self._intent_summarizer(raw_llm_response)
            # Defensive: fallback to default label if summarizer fails
            summary_label = None

        price_and_duration = ""
        model_name = ""
        if not omit_cost_and_model and log is not None and log.calls:
            last_call = log.calls[-1]
            request_body = last_call.http_request.body.json()
            cost = self.cost_estimator.calculate_cost(
                request_body["model"],
                last_call.usage.input_tokens,
                last_call.usage.output_tokens,
            )
            cost_usd_per_thousand = cost["total_cost_usd"] * 1_000
            duration_ms = _get_call_duration_ms(last_call)
            price_and_duration = (
                f" { _format_price_and_duration(cost_usd_per_thousand, duration_ms) }"
            )
            model_name = f" | {cost['model_info']['model_name']}"
        # Use summarizer output as label if available, else fallback to default
        if summary_label is not None:
            label = f"Completion | {summary_label}"
        else:
            suffix = ""
            if not omit_cost_and_model:
                suffix = f"{price_and_duration}{model_name}"
            label = f"Completion{' |'if suffix else ''}{suffix}"
        return label, str(raw_llm_response)

    async def display_calls(
        self,
        *,
        prompts: Literal["always_hide", "always_show", "show", "hide"] = "hide",
        completions: Literal["always_hide", "always_show", "show", "hide"] = "hide",
    ):
        logs = list(self.collector.logs)
        show_step = len(logs) > 1

        def get_key(i, k):
            if show_step:
                return f"{i} | {k}"
            return k

        completion_button_coros = [
            (
                self._get_completion_button(log.raw_llm_response, log=log)
                if completions != "always_hide"
                else None
            )
            for log in logs
        ]
        completion_buttons = (
            await asyncio.gather(
                *[coro for coro in completion_button_coros if coro is not None]
            )
            if completions != "always_hide"
            else []
        )

        completion_idx = 0
        for i, log in enumerate(logs, start=1):
            if prompts != "always_hide":
                for k, v in self._get_prompt_buttons(log.calls).items():
                    hide_text_under_a_button(get_key(i, k), v, visibility=prompts)
            if completions != "always_hide":
                k, v = completion_buttons[completion_idx]
                hide_text_under_a_button(get_key(i, k), v, visibility=completions)
                completion_idx += 1

    async def display_session(
        self,
        root_name: str,
        *,
        show_depth=0,
        prompts: Literal["always_hide", "hide"] = "hide",
        completions: Literal["always_hide", "hide"] = "hide",
        show_everything: bool = False,
    ):
        nested_buttons = {}
        logs = list(self.collector.logs)  # Ensure it's a list for indexing

        # --- Populate nested_buttons with unique keys ---
        # Gather completion buttons first as they might involve async calls (summarizer)
        completion_button_coros = []
        if completions != "always_hide":
            completion_button_coros = [
                self._get_completion_button(
                    log.raw_llm_response,
                    log=log,
                    omit_cost_and_model=False,  # Keep True as per original logic for this func
                )
                for log in logs
            ]

        # Gather results, handling potential exceptions during gather
        completion_results = []
        if completions != "always_hide":
            completion_results = await asyncio.gather(
                *completion_button_coros, return_exceptions=True
            )

        # Now iterate through logs *with their index* to build the final dict
        for i, log in enumerate(logs, start=1):
            log_prefix = f"{i} | "

            # 1. Add Prompt Buttons for this log with unique keys
            # Use omit_cost_and_model=False to show cost/model details on prompts here
            prompt_buttons = self._get_prompt_buttons(
                log.calls, omit_cost_and_model=False
            )
            for k, v in prompt_buttons.items():
                # Add index prefix for guaranteed uniqueness
                unique_key = f"{log_prefix}{k}"
                if prompts != "always_hide":
                    nested_buttons[unique_key] = v

            # 2. Add Completion Button for this log with unique key
            if completions != "always_hide":
                completion_data = completion_results[i - 1]  # Use i-1 for 0-based index

                if isinstance(completion_data, Exception):
                    raise completion_data

                if completion_data is not None:  # Check if button generation succeeded
                    completion_k, completion_v = completion_data  # type: ignore
                    # Add index prefix for guaranteed uniqueness
                    unique_key = f"{log_prefix}{completion_k}"
                    nested_buttons[unique_key] = completion_v
                else:
                    # Handle case where button generation returned None unexpectedly
                    nested_buttons[f"{log_prefix}Completion (Not Available)"] = (
                        "Completion data could not be generated."
                    )

        # --- Display using the populated nested_buttons ---
        root_label = f"{root_name} | Cost: {self.format_total_cost()}"
        hide_text_under_a_button_nested(
            root_label,
            nested_buttons,
            visibility="always_show" if show_everything else "hide",
            hide_after_level=show_depth,
        )

    def format_total_cost(self):
        all_models = set()
        total_cost_usd_per_thousand = 0
        total_duration_ms = 0
        for log in self.collector.logs:
            log_duration_ms = _get_log_duration_ms(log)
            if log_duration_ms is not None:
                total_duration_ms += log_duration_ms
            for call in log.calls:
                if call.http_request is None:
                    raise ValueError(
                        "Expected call.http_request to be not None, but got None"
                    )
                request_body = call.http_request.body.json()
                cost = self.cost_estimator.calculate_cost(
                    request_body["model"],
                    call.usage.input_tokens,
                    call.usage.output_tokens,
                )
                cost_usd_per_thousand = cost["total_cost_usd"] * 1_000
                total_cost_usd_per_thousand += cost_usd_per_thousand
                all_models.add(cost["model_info"]["model_name"])

        duration_sec = f"{total_duration_ms/1000:.2f}s" if total_duration_ms else "N/A"
        return f"{total_cost_usd_per_thousand:.2f}$/1k | {duration_sec} | {', '.join(all_models)}"


class JupyterBamlMonitor(Generic[T]):
    def __init__(self, ai: T, *, summarizer=None):
        self._ai = ai
        self._summarizer = summarizer
        self._streamer: JupyterOutputBox | None = None
        self._collector: JupyterBamlCollector | None = None

    @property
    def ai(self) -> T:
        if self._collector is None:
            raise RuntimeError("JupyterTraceLLMCalls tracer has not been initialized.")
        return cast("T", self._collector.ai)

    @property
    def b(self) -> T:
        return self.ai

    async def display_calls(
        self,
        *,
        prompts: Literal["always_hide", "always_show", "show", "hide"] = "hide",
        completions: Literal["always_hide", "always_show", "show", "hide"] = "hide",
    ):
        if self._collector is None:
            raise RuntimeError("JupyterTraceLLMCalls tracer has not been initialized.")
        await self._collector.display_calls(prompts=prompts, completions=completions)

    async def display_session(
        self,
        name: str,
        *,
        prompts: Literal["always_hide", "hide"] = "hide",
        completions: Literal["always_hide", "hide"] = "hide",
        show_everything: bool = False,
    ):
        if self._collector is None:
            raise RuntimeError("JupyterTraceLLMCalls tracer has not been initialized.")
        await self._collector.display_session(
            name,
            prompts=prompts,
            completions=completions,
            show_everything=show_everything,
        )

    def __enter__(self):
        self._streamer = JupyterOutputBox(clear_after_finish=True)
        self._streamer.__enter__()
        self._collector = JupyterBamlCollector(
            self._ai,
            stream_callback=self._streamer.display(),
            intent_summarizer=self._summarizer,
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._streamer is not None:
            self._streamer.__exit__(exc_type, exc_val, exc_tb)
            self._streamer = None
