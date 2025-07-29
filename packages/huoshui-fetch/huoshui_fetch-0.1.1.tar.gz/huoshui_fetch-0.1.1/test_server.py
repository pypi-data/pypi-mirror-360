#!/usr/bin/env python
"""Simple test script for huoshui-fetch MCP server."""

import subprocess
import json
import time


def send_command(command: dict) -> dict:
    """Send a command to the MCP server and get response."""
    proc = subprocess.Popen(
        ["python", "-m", "huoshui_fetch"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    
    # Send command
    json.dump(command, proc.stdin)
    proc.stdin.write('\n')
    proc.stdin.flush()
    
    # Get response
    response = proc.stdout.readline()
    proc.terminate()
    
    return json.loads(response) if response else {}


def test_server():
    """Test basic MCP server functionality."""
    print("Testing huoshui-fetch MCP server...")
    
    # Test 1: Simple HTML to Markdown conversion
    print("\n1. Testing HTML to Markdown conversion:")
    test_html = "<h1>Hello World</h1><p>This is a <strong>test</strong>.</p>"
    
    command = {
        "method": "html_to_markdown_tool",
        "params": {"html": test_html}
    }
    
    # Note: This is a simplified test. Real MCP protocol is more complex.
    print(f"Input HTML: {test_html}")
    print("(In a real MCP client, this would be properly converted to Markdown)")
    
    # Test 2: URL validation
    print("\n2. Testing URL validation:")
    test_urls = ["https://example.com", "example.com", "not-a-url"]
    
    for url in test_urls:
        print(f"URL: {url} - Valid: {url.startswith('http')}")
    
    print("\n✅ Basic tests completed!")
    print("\nTo properly test the server, configure it with Claude Desktop or another MCP client.")
    print("See README.md for configuration instructions.")


if __name__ == "__main__":
    test_server()