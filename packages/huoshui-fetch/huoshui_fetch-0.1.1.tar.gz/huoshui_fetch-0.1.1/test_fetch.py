#!/usr/bin/env python
"""Test script to verify fetch_url works correctly."""

import subprocess
import json
import sys

def test_mcp_fetch():
    """Test the fetch_url tool through MCP protocol."""
    # Start the server and send a test request
    proc = subprocess.Popen(
        ["uvx", "--from", ".", "huoshui-fetch"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Send initialize request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "1.0.0",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    proc.stdin.write(json.dumps(init_request) + '\n')
    proc.stdin.flush()
    
    # Read response
    response = proc.stdout.readline()
    print("Initialize response:", response)
    
    # Send tool call
    tool_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "fetch_url",
            "arguments": {
                "url": "https://example.com",
                "timeout": 10.0
            }
        }
    }
    
    proc.stdin.write(json.dumps(tool_request) + '\n')
    proc.stdin.flush()
    
    # Read tool response
    tool_response = proc.stdout.readline()
    print("Tool response:", tool_response)
    
    # Check stderr
    proc.terminate()
    proc.wait()
    stderr = proc.stderr.read()
    if stderr:
        print("Stderr:", stderr)

if __name__ == "__main__":
    test_mcp_fetch()