import datetime
import logging
import os
import traceback
import zoneinfo
from collections.abc import Callable, Coroutine
from typing import Any

from rich.console import Console
from rich.json import JSON
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

MAX_LINE_LENGTH = 140

# Try to import our markdown converter
try:
    from .object_to_markdown import (
        convert_api_response_to_markdown,
        convert_object_to_markdown,
    )

    MARKDOWN_CONVERTER_AVAILABLE = True
except ImportError:
    MARKDOWN_CONVERTER_AVAILABLE = False


def _display_response_rich(
    response: Any,
    console: Console,
    render_as_markdown: bool = False,
    *,
    logger: logging.Logger,
) -> None:
    """Display response using Rich library for beautiful output."""
    # If markdown rendering is requested and available, try that first
    if render_as_markdown and MARKDOWN_CONVERTER_AVAILABLE:
        try:
            if isinstance(response, dict) and any(
                key in response for key in ["error", "response", "warning", "step"]
            ):
                markdown_content = convert_api_response_to_markdown(response)
            else:
                markdown_content = convert_object_to_markdown(response, "Response")

            console.print(Markdown(markdown_content))
            return
        except Exception:
            # Fall back to regular Rich rendering if markdown conversion fails
            pass

    if isinstance(response, str):
        # Try to detect if it's JSON, markdown, or plain text
        try:
            import json

            json.loads(response)
            console.print(JSON(response))
            return
        except (json.JSONDecodeError, ValueError):
            pass

        # Check if it looks like markdown (contains #, *, etc.)
        if any(marker in response for marker in ["#", "*", "-", "`", "|"]):
            try:
                console.print(Markdown(response))
                return
            except Exception:
                pass

        # Fallback to styled text
        console.print(Text(response, style="green"))

    elif isinstance(response, dict):
        if response.get("error") is not None:
            error_panel = Panel(
                _rich_format_value(response["error"]),
                title="❌ Error",
                title_align="left",
                border_style="red",
                padding=(1, 2),
            )
            if os.environ.get("QCOG_DEBUG"):
                logger.error(response["error"])
            console.print(error_panel)

        elif response.get("response") is not None:
            success_panel = Panel(
                _rich_format_value(response["response"]),
                title="✅ Success",
                title_align="left",
                border_style="green",
                padding=(1, 2),
            )
            console.print(success_panel)

        elif response.get("warning") is not None:
            warning_panel = Panel(
                _rich_format_value(response["warning"]),
                title="⚠️ Warning",
                title_align="left",
                border_style="yellow",
                padding=(1, 2),
            )
            console.print(warning_panel)

        elif response.get("step") is not None:
            if len(response["step"]) != 1:
                raise ValueError(
                    f"Step must contain exactly one key. Got {response['step'].keys()}"
                )
            step_title = list(response["step"].keys())[0]
            step_panel = Panel(
                _rich_format_value(response["step"][step_title]),
                title=f"🔄 {step_title}",
                title_align="left",
                border_style="blue",
                padding=(1, 2),
            )
            console.print(step_panel)
        else:
            # Regular dict - try to display as JSON or table
            _display_dict_rich(response, console)
    else:
        # Try to display as JSON first
        try:
            import json

            json_str = json.dumps(response, indent=2, default=str)
            console.print(JSON(json_str))
        except (TypeError, ValueError):
            console.print(Text(str(response), style="cyan"))


def _rich_format_value(value: Any, max_depth: int = 4, current_depth: int = 0) -> Any:
    """Format a value for Rich display with recursive handling."""
    if current_depth >= max_depth:
        return Text("[dim]<nested data, depth limit reached>[/dim]")

    if isinstance(value, dict):
        return _dict_to_rich_table(value, max_depth, current_depth + 1)
    elif isinstance(value, list):
        return _list_to_rich_tree(value, max_depth, current_depth + 1)
    elif isinstance(value, str):
        # Try to detect structured content
        try:
            import json

            json.loads(value)
            return JSON(value)
        except (json.JSONDecodeError, ValueError):
            pass

        # Check for markdown-like content
        if any(marker in value for marker in ["#", "*", "-", "`", "|"]):
            try:
                return Markdown(value)
            except Exception:
                pass

        return Text(value)
    else:
        return Text(str(value))


def _is_datetime(value: str) -> str | None:
    """Check if a string is a valid datetime."""
    datetime_formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO with microseconds and Z
        "%Y-%m-%dT%H:%M:%SZ",  # ISO with Z
        "%Y-%m-%dT%H:%M:%S.%f",  # ISO with microseconds
        "%Y-%m-%dT%H:%M:%S",  # ISO basic
        "%Y-%m-%d %H:%M:%S.%f",  # Space separated with microseconds
        "%Y-%m-%d %H:%M:%S",  # Space separated basic
    ]
    try:
        parsed_dt: datetime.datetime | None = None

        for fmt in datetime_formats:
            try:
                parsed_dt = datetime.datetime.strptime(value, fmt)
            except Exception:
                continue

            if parsed_dt is None:
                return None

            try:
                import time

                local_tz = zoneinfo.ZoneInfo(time.tzname[0])
            except Exception:
                # Default to UTC if the local timezone is not available
                local_tz = zoneinfo.ZoneInfo("UTC")

            # If the datetime is not timezone aware assume
            # that has been stored as UTC
            if parsed_dt.tzinfo is None:
                parsed_dt = parsed_dt.replace(tzinfo=zoneinfo.ZoneInfo("UTC"))

            # Convert to local timezone
            local_dt = parsed_dt.astimezone(local_tz)
            return local_dt.strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception:
        return None

    return None


def _dict_to_rich_table(
    data: dict, max_depth: int = 4, current_depth: int = 0
) -> Table:
    """Convert dictionary to a Rich table with recursive nested tables."""
    table = Table(
        show_header=True, header_style="bold magenta", box=None, padding=(0, 1)
    )
    table.add_column("Key", style="cyan", no_wrap=True, min_width=15)
    table.add_column("Value", style="green", overflow="fold")

    for key, value in data.items():
        if isinstance(value, dict) and current_depth < max_depth:
            # Create nested table for dictionary values
            nested_table = _dict_to_rich_table(value, max_depth, current_depth + 1)
            nested_panel = Panel(
                nested_table,
                title=f"📂 {key}",
                title_align="left",
                border_style="blue",
                padding=(0, 1),
            )
            table.add_row("", nested_panel)
        elif isinstance(value, list):
            # Check if it's a simple list (all items are simple types)
            is_simple_list = all(
                isinstance(item, str | int | float | bool | type(None))
                for item in value
            )

            if is_simple_list and len(value) <= 10:
                # Display simple lists inline with proper formatting
                if len(value) == 0:
                    table.add_row(str(key), Text("[]", style="dim"))
                else:
                    # Create formatted list display
                    formatted_items = []
                    for item in value:
                        if isinstance(item, str):
                            formatted_items.append(f'"{item}"')
                        elif item is None:
                            formatted_items.append("null")
                        else:
                            formatted_items.append(str(item))
                    list_display = ", ".join(formatted_items)
                    table.add_row(
                        str(key), Text(f"[{list_display}]", style="bright_blue")
                    )
            elif len(value) > 0 and current_depth < max_depth:
                # Create tree for complex list values
                list_tree = _list_to_rich_tree(value, max_depth, current_depth + 1)
                list_panel = Panel(
                    list_tree,
                    title=f"📋 {key} ({len(value)} items)",
                    title_align="left",
                    border_style="green",
                    padding=(0, 1),
                )
                table.add_row("", list_panel)
            elif len(value) == 0:
                table.add_row(str(key), Text("[]", style="dim"))
            else:
                # Depth limit reached for complex list
                table.add_row(
                    str(key),
                    Text(
                        f"<list with {len(value)} items> (too deep to display)",
                        style="dim",
                    ),
                )
        else:
            # Simple value or depth limit reached
            if isinstance(value, dict | list) and current_depth >= max_depth:
                value_str = f"<{type(value).__name__}> (too deep to display)"
                table.add_row(str(key), Text(value_str, style="dim"))
            elif isinstance(value, str) and (formatted := _is_datetime(value)):
                table.add_row(str(key), Text(formatted, style="green"))
            elif isinstance(value, str) and len(value) > 100:
                # Truncate very long strings
                truncated = value[:MAX_LINE_LENGTH] + "..."
                table.add_row(str(key), Text(truncated))
            else:
                table.add_row(str(key), str(value))

    return table


def _list_to_rich_tree(data: list, max_depth: int = 4, current_depth: int = 0) -> Tree:
    """Convert list to a Rich tree with recursive nested structures."""
    tree = Tree("📋 Items")

    # Limit the number of items shown to avoid overwhelming output
    max_items = 10
    items_to_show = min(len(data), max_items)

    for i, item in enumerate(data[:items_to_show]):
        if isinstance(item, dict) and current_depth < max_depth:
            branch = tree.add(f"[bold cyan]Item {i + 1}[/bold cyan]")
            # For dictionaries in lists, show key-value pairs
            for key, value in item.items():
                if isinstance(value, dict) and current_depth < max_depth - 1:
                    sub_branch = branch.add(f"[yellow]{key}[/yellow]:")
                    for sub_key, sub_value in value.items():
                        sub_branch.add(
                            f"[blue]{sub_key}[/blue]: {str(sub_value)[:MAX_LINE_LENGTH]}{'...' if len(str(sub_value)) > MAX_LINE_LENGTH else ''}"  # noqa: E501
                        )
                elif isinstance(value, list) and current_depth < max_depth - 1:
                    sub_branch = branch.add(
                        f"[yellow]{key}[/yellow]: [dim]({len(value)} items)[/dim]"
                    )
                    for j, list_item in enumerate(value[:3]):  # Show first 3 items
                        sub_branch.add(
                            f"[green]{j + 1}.[/green] {str(list_item)[:30]}{'...' if len(str(list_item)) > 30 else ''}"  # noqa: E501
                        )
                    if len(value) > 3:
                        sub_branch.add(f"[dim]... and {len(value) - 3} more[/dim]")
                else:
                    value_display = (
                        str(value)[:MAX_LINE_LENGTH] + "..."
                        if len(str(value)) > MAX_LINE_LENGTH
                        else str(value)  # noqa: E501
                    )
                    branch.add(f"[yellow]{key}[/yellow]: {value_display}")
        else:
            if current_depth >= max_depth:
                tree.add(
                    f"[green]{i + 1}.[/green] [dim]<nested data, depth limit reached>[/dim]"  # noqa
                )
            else:
                item_display = (
                    str(item)[:50] + "..." if len(str(item)) > 50 else str(item)
                )
                tree.add(f"[green]{i + 1}.[/green] {item_display}")

    if len(data) > max_items:
        tree.add(f"[dim]... and {len(data) - max_items} more items[/dim]")

    return tree


def _display_dict_rich(data: dict, console: Console) -> None:
    """Display a dictionary using Rich formatting."""
    # Use the recursive table generation for better nested data display
    console.print(_dict_to_rich_table(data))


def display(
    logger: logging.Logger,
    async_: bool = False,
    use_rich: bool = True,
    render_as_markdown: bool = False,
) -> Callable:
    """
    Display decorator that formats and logs responses with beautiful output.

    Args:
        logger: Logger instance to use for output
        async_: Whether the decorated function is async
        use_rich: Whether to use Rich library for enhanced display (default: True)
        render_as_markdown: Whether to render responses as markdown (default: False)
    """

    def decorator(func: Callable) -> Callable | Coroutine:
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                response = func(*args, **kwargs)

                console = Console()
                _display_response_rich(
                    response,
                    console,
                    render_as_markdown,
                    logger=logger,
                )

                return response
            except Exception as e:
                console = Console()
                error_panel = Panel(
                    Text(str(e), style="red"),
                    title="❌ Error",
                    border_style="red",
                    padding=(1, 2),
                )
                console.print(error_panel)

                # Also log the error for test compatibility and proper error tracking
                if os.environ.get("QCOG_DEBUG"):
                    logger.error(str(e))

                if os.environ.get("QCOG_DEBUG"):
                    console.print(
                        Panel(
                            Syntax(traceback.format_exc(), "python", theme="monokai"),
                            title="🐛 Debug Traceback",
                            border_style="red",
                        )
                    )
                    logger.debug(traceback.format_exc())

        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                response = await func(*args, **kwargs)

                console = Console()
                _display_response_rich(
                    response,
                    console,
                    render_as_markdown,
                    logger=logger,
                )

                return response
            except Exception as e:
                console = Console()
                error_panel = Panel(
                    Text(str(e), style="red"),
                    title="❌ Error",
                    border_style="red",
                    padding=(1, 2),
                )
                console.print(error_panel)

                # Also log the error for test compatibility and proper error tracking
                if os.environ.get("QCOG_DEBUG"):
                    logger.error(str(e))

                if os.environ.get("QCOG_DEBUG"):
                    console.print(
                        Panel(
                            Syntax(traceback.format_exc(), "python", theme="monokai"),
                            title="🐛 Debug Traceback",
                            border_style="red",
                        )
                    )
                    logger.debug(traceback.format_exc())
                return None

        return async_wrapper if async_ else sync_wrapper

    return decorator


# Convenience decorators for specific rendering modes
def display_as_markdown(logger: logging.Logger, async_: bool = False) -> Callable:
    """Display decorator that renders responses as markdown."""
    return display(logger, async_=async_, use_rich=True, render_as_markdown=True)


def display_as_json(logger: logging.Logger, async_: bool = False) -> Callable:
    """Display decorator that renders responses as JSON with syntax highlighting."""
    return display(logger, async_=async_, use_rich=True, render_as_markdown=False)
