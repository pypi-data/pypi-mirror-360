import html as html_lib
import json
import random
import string
from typing import Any, Literal

from IPython.display import HTML, display


def _hide_html_under_a_button(
    button_title: str,
    contents_html: str,
    visibility: Literal["always_hide", "always_show", "show", "hide"] = "show",
):
    id_ = "".join(random.choices(string.ascii_letters, k=10))  # noqa: S311

    if visibility == "always_show":
        html = contents_html
    else:
        display_style = "block" if visibility == "show" else "none"

        html = f"""
            <button type="button" onclick="toggle_text_{id_}()">{button_title}</button>
            <div id="collapsible_text_{id_}" style="display:{display_style};">
                {contents_html}
            </div>

            <script>
            function toggle_text_{id_}() {{
                var collapsible_text = document.getElementById("collapsible_text_{id_}");
                if (collapsible_text.style.display === "none") {{
                    collapsible_text.style.display = "block";
                }} else {{
                    collapsible_text.style.display = "none";
                }}
            }}
            </script>"""
    display(HTML(html))


def _format_content_as_html(content: str) -> str:
    """Format plain text content as HTML."""
    content = html_lib.escape(content)
    content = str(content).replace("\n", "</br>")
    return f"""<p><pre id="jsonOutput">{content}</pre></p>"""


def hide_text_under_a_button(
    button_title: str,
    txt: str,
    visibility: Literal["always_hide", "always_show", "show", "hide"] = "show",
):
    contents_html = _format_content_as_html(txt)
    _hide_html_under_a_button(button_title, contents_html, visibility=visibility)


def hide_text_under_a_button_nested(
    button_title: str,
    contents: str | dict[str, Any],
    visibility: Literal["always_hide", "always_show", "show", "hide"] = "show",
    hide_after_level: int = 0,
):
    if isinstance(contents, str):
        hide_text_under_a_button(button_title, contents, visibility)
        return

    def _build_nested_html(data, level=0):
        if isinstance(data, str):
            return _format_content_as_html(data)

        nested_html = []

        for key, value in data.items():
            if isinstance(value, (dict, str)):
                sub_id = "".join(
                    random.choices(string.ascii_letters, k=10)  # noqa: S311
                )
                sub_content = _build_nested_html(value, level + 1)

                # Apply the same visibility setting to nested elements
                # Force hide for levels beyond hide_after_level
                display_style = (
                    "none"
                    if level >= hide_after_level
                    else "block" if visibility == "show" else "none"
                )
                if visibility == "always_show":
                    nested_html.append(
                        f"""
                        <div style="margin-left: {(level + 1) * 20}px;">
                            <strong>{key}:</strong>
                            {sub_content}
                        </div>
                        """
                    )
                else:
                    nested_html.append(
                        f"""
                        <div style="margin-left: {(level + 1) * 20}px;">
                            <button type="button" onclick="toggle_text_{sub_id}()">{key}</button>
                            <div id="collapsible_text_{sub_id}" style="display:{display_style};">
                                {sub_content}
                            </div>
                        </div>
                        <script>
                        function toggle_text_{sub_id}() {{
                            var collapsible_text = document.getElementById("collapsible_text_{sub_id}");
                            if (collapsible_text.style.display === "none") {{
                                collapsible_text.style.display = "block";
                            }} else {{
                                collapsible_text.style.display = "none";
                            }}
                        }}
                        </script>
                    """
                    )
            else:
                # For non-dict, non-string values, display as JSON
                nested_html.append(
                    f"""
                    <div style="margin-left: {(level + 1) * 20}px;">
                        <strong>{key}:</strong> {json.dumps(value)}
                    </div>
                """
                )

        return "".join(nested_html)

    nested_content = _build_nested_html(contents)
    _hide_html_under_a_button(button_title, nested_content, visibility=visibility)

