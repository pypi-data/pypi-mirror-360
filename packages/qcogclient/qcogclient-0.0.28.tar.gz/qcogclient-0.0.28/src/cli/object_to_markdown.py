"""
Object to Markdown Converter

This module provides utilities to convert Python objects, dictionaries,
dataclasses, and other structures into markdown format for better console
visualization with Rich library.
"""

from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from typing import Any


class MarkdownConverter:
    """Convert Python objects to markdown format."""

    def __init__(self, max_string_length: int = 100, max_list_items: int = 10):
        self.max_string_length = max_string_length
        self.max_list_items = max_list_items

    def convert(self, obj: Any, title: str = "Data") -> str:
        """Convert any object to markdown."""
        if obj is None:
            return f"# {title}\n\n*No data*"

        md = f"# {title}\n\n"
        md += self._convert_value(obj, level=2)
        return md

    def _convert_value(self, value: Any, level: int = 2) -> str:
        """Convert a value to markdown format."""
        if value is None:
            return "*None*\n\n"

        elif isinstance(value, bool):
            return f"**{value}**\n\n"

        elif isinstance(value, (int | float)):
            return f"`{value:,}`\n\n"

        elif isinstance(value, str):
            if len(value) > self.max_string_length:
                return f"```\n{value[: self.max_string_length]}...\n```\n\n"
            elif "\n" in value:
                return f"```\n{value}\n```\n\n"
            else:
                return f"{value}\n\n"

        elif isinstance(value, (datetime | date)):
            return f"📅 `{value.isoformat()}`\n\n"

        elif isinstance(value, dict):
            return self._convert_dict(value, level)

        elif isinstance(value, (list | tuple)):
            return self._convert_list(value, level)  # type: ignore

        elif is_dataclass(value):
            return self._convert_dict(asdict(value), level)  # type: ignore

        elif hasattr(value, "__dict__"):
            return self._convert_dict(value.__dict__, level)

        else:
            return f"`{str(value)}`\n\n"

    def _convert_dict(self, data: dict, level: int) -> str:
        """Convert dictionary to markdown."""
        if not data:
            return "*Empty dictionary*\n\n"

        md = ""

        # Check if this looks like tabular data
        if self._is_tabular_data(data):
            md += self._dict_to_table(data)
        else:
            # Use headers and content format
            for key, value in data.items():
                header = "#" * level
                md += f"{header} {self._format_key(key)}\n\n"
                md += self._convert_value(value, level + 1)

        return md

    def _convert_list(self, data: list, level: int) -> str:
        """Convert list to markdown."""
        if not data:
            return "*Empty list*\n\n"

        # Check if this is a list of dictionaries (table format)
        if all(isinstance(item, dict) for item in data[:3]):
            return self._list_of_dicts_to_table(data)

        # Regular list
        md = ""
        items_to_show = min(len(data), self.max_list_items)

        for i, item in enumerate(data[:items_to_show]):
            if isinstance(item, (dict | list)):
                md += f"{i + 1}. **Item {i + 1}**\n\n"
                md += self._convert_value(item, level + 1)
            else:
                md += f"- {self._convert_value(item, level).strip()}\n"

        if len(data) > self.max_list_items:
            md += f"\n*... and {len(data) - self.max_list_items} more items*\n\n"

        return md + "\n"

    def _is_tabular_data(self, data: dict) -> bool:
        """Check if dictionary represents tabular data."""
        if len(data) < 2:
            return False

        # Check if all values are simple types
        return all(
            isinstance(v, (str | int | float | bool | type(None)))
            for v in data.values()
        )

    def _dict_to_table(self, data: dict) -> str:
        """Convert dictionary to markdown table."""
        md = "| Key | Value |\n"
        md += "|-----|-------|\n"

        for key, value in data.items():
            key_str = self._format_key(key)
            value_str = self._format_table_value(value)
            md += f"| {key_str} | {value_str} |\n"

        return md + "\n"

    def _list_of_dicts_to_table(self, data: list) -> str:
        """Convert list of dictionaries to markdown table."""
        if not data:
            return "*Empty list*\n\n"

        # Get all unique keys
        all_keys: set[str] = set()
        for item in data:
            if isinstance(item, dict):
                all_keys.update(item.keys())

        if not all_keys:
            return "*No valid data*\n\n"

        # Sort keys for consistent output
        keys = sorted(all_keys)

        # Create header
        md = "| " + " | ".join(self._format_key(k) for k in keys) + " |\n"
        md += "| " + " | ".join("---" for _ in keys) + " |\n"

        # Add rows
        items_to_show = min(len(data), self.max_list_items)
        for item in data[:items_to_show]:
            if isinstance(item, dict):
                row_values = []
                for key in keys:
                    value = item.get(key, "")
                    row_values.append(self._format_table_value(value))
                md += "| " + " | ".join(row_values) + " |\n"

        if len(data) > self.max_list_items:
            md += f"\n*... and {len(data) - self.max_list_items} more rows*\n"

        return md + "\n"

    def _format_key(self, key: str) -> str:
        """Format a key for display."""
        return str(key).replace("_", " ").title()

    def _format_table_value(self, value: Any) -> str:
        """Format a value for table display."""
        if value is None:
            return "-"
        elif isinstance(value, bool):
            return "✓" if value else "✗"
        elif isinstance(value, (datetime | date)):
            return value.strftime("%Y-%m-%d")
        elif isinstance(value, str):
            if len(value) > 50:
                return value[:47] + "..."
            return value.replace("|", "\\|")  # Escape pipes in markdown tables
        elif isinstance(value, (int | float)):
            return f"{value:,}"
        else:
            return str(value)[:50].replace("|", "\\|")


def convert_api_response_to_markdown(response: dict) -> str:
    """Convert an API response to markdown format."""
    converter = MarkdownConverter()

    if not isinstance(response, dict):
        return converter.convert(response, "API Response")

    md = "# API Response\n\n"

    # Handle standard response format
    if "error" in response:
        md += "## ❌ Error\n\n"
        md += f"```\n{response['error']}\n```\n\n"

    elif "response" in response:
        md += "## ✅ Success\n\n"
        md += converter._convert_value(response["response"], level=3)

    elif "warning" in response:
        md += "## ⚠️ Warning\n\n"
        md += converter._convert_value(response["warning"], level=3)

    elif "step" in response:
        step_data = response["step"]
        if isinstance(step_data, dict) and len(step_data) == 1:
            step_name = list(step_data.keys())[0]
            md += f"## 🔄 {step_name}\n\n"
            md += converter._convert_value(step_data[step_name], level=3)
        else:
            md += "## 🔄 Step\n\n"
            md += converter._convert_value(step_data, level=3)

    else:
        # Regular response
        md += converter._convert_value(response, level=2)

    return md


def convert_object_to_markdown(obj: Any, title: str = "Object") -> str:
    """Convert any Python object to markdown."""
    converter = MarkdownConverter()
    return converter.convert(obj, title)


# Convenience functions for common use cases
def dict_to_markdown(data: dict, title: str = "Dictionary") -> str:
    """Convert dictionary to markdown."""
    return convert_object_to_markdown(data, title)


def list_to_markdown(data: list, title: str = "List") -> str:
    """Convert list to markdown."""
    return convert_object_to_markdown(data, title)


def dataclass_to_markdown(obj: Any, title: str | None = None) -> str:
    """Convert dataclass to markdown."""
    if title is None:
        title = obj.__class__.__name__
    return convert_object_to_markdown(obj, title)


# Example usage
if __name__ == "__main__":
    # Example data
    sample_data = {
        "user": {
            "id": 123,
            "name": "John Doe",
            "email": "john@example.com",
            "active": True,
            "roles": ["admin", "user"],
            "last_login": datetime.now(),
        },
        "projects": [
            {"name": "Project A", "status": "active", "completion": 75},
            {"name": "Project B", "status": "completed", "completion": 100},
            {"name": "Project C", "status": "pending", "completion": 0},
        ],
        "metadata": {"total_projects": 3, "api_version": "v2.1", "cache_enabled": True},
    }

    markdown = convert_object_to_markdown(sample_data, "Sample API Response")
    print(markdown)
