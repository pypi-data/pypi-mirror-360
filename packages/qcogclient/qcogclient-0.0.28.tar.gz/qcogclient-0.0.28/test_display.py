#!/usr/bin/env python3
"""
Test script for the enhanced display decorator.
"""

import logging
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cli.pretty import display, display_as_markdown, display_as_json

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


@display_as_json(logger)
def test_json_display():
    """Test JSON-style display."""
    return {
        "response": {
            "user": {
                "id": 123,
                "name": "Alice Johnson",
                "email": "alice@example.com",
                "active": True,
                "roles": ["admin", "user"]
            },
            "metadata": {
                "request_id": "req_123456",
                "timestamp": "2024-01-15T10:30:00Z",
                "api_version": "v2.1"
            }
        }
    }


@display_as_json(logger)
def test_recursive_display():
    """Test recursive display with deeply nested structures."""
    return {
        "response": {
            "user_profile": {
                "basic_info": {
                    "id": "user_123",
                    "name": "John Doe",
                    "email": "john@example.com",
                    "roles": ["admin", "user", "developer"]
                },
                "preferences": {
                    "theme": "dark",
                    "language": "en",
                    "notifications": {
                        "email": True,
                        "push": False,
                        "sms": True
                    }
                },
                "recent_activity": [
                    {
                        "action": "login",
                        "timestamp": "2024-01-15T10:30:00Z",
                        "details": {
                            "ip_address": "192.168.1.100",
                            "user_agent": "Mozilla/5.0...",
                            "location": "New York, NY"
                        }
                    },
                    {
                        "action": "file_upload",
                        "timestamp": "2024-01-15T11:15:00Z",
                        "details": {
                            "filename": "report.pdf",
                            "size_mb": 2.5,
                            "status": "completed"
                        }
                    }
                ]
            },
            "system_info": {
                "api_version": "v2.1",
                "response_time_ms": 45,
                "server_location": "us-east-1"
            }
        }
    }


@display_as_markdown(logger)
def test_markdown_display():
    """Test markdown-style display."""
    return {
        "response": {
            "projects": [
                {"name": "Project Alpha", "status": "active", "completion": 75, "team_size": 5},
                {"name": "Project Beta", "status": "completed", "completion": 100, "team_size": 3},
                {"name": "Project Gamma", "status": "planning", "completion": 0, "team_size": 8}
            ],
            "summary": {
                "total_projects": 3,
                "active_projects": 1,
                "completed_projects": 1,
                "average_completion": 58.33
            }
        }
    }


@display(logger, render_as_markdown=True)
def test_error_display():
    """Test error display."""
    return {
        "error": "Authentication failed: Invalid API key provided. Please check your credentials and try again."
    }


@display(logger, render_as_markdown=True)
def test_warning_display():
    """Test warning display."""
    return {
        "warning": "Rate limit approaching: You have made 950 out of 1000 allowed requests this hour. Consider implementing request throttling."
    }


@display(logger, render_as_markdown=True)
def test_step_display():
    """Test step display."""
    return {
        "step": {
            "Processing Data": {
                "status": "in_progress",
                "records_processed": 2500,
                "total_records": 10000,
                "estimated_completion": "2 minutes",
                "current_phase": "validation"
            }
        }
    }


@display_as_json(logger)
def test_simple_lists():
    """Test simple list display."""
    return {
        "response": {
            "simple_list": ["item1", "item2", "item3"],
            "numbers": [1, 2, 3, 4, 5],
            "mixed": ["text", 123, True, None],
            "empty": [],
            "nested_dict": {
                "roles": ["admin", "user"],
                "permissions": ["read", "write", "delete"]
            }
        }
    }


def main():
    """Run all display tests."""
    print("🎨 Testing Enhanced CLI Display Decorator\n")
    print("=" * 60)

    print("\n🔍 Simple Lists Test:")
    print("-" * 30)
    test_simple_lists()

    print("\n📊 JSON Display Test:")
    print("-" * 30)
    test_json_display()

    print("\n🔄 Recursive Display Test:")
    print("-" * 30)
    test_recursive_display()

    print("\n📝 Markdown Display Test:")
    print("-" * 30)
    test_markdown_display()

    print("\n❌ Error Display Test:")
    print("-" * 30)
    test_error_display()

    print("\n⚠️ Warning Display Test:")
    print("-" * 30)
    test_warning_display()

    print("\n🔄 Step Display Test:")
    print("-" * 30)
    test_step_display()

    print("\n✅ All tests completed!")


if __name__ == "__main__":
    main()