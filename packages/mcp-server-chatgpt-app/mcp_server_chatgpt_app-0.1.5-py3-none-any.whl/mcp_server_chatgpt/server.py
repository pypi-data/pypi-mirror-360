import subprocess
import os
from typing import Optional, Dict, Any
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ChatGPT")

def run_applescript(script: str, wait_for_output: bool = True) -> Dict[str, Any]:
    """
    Run an AppleScript and return its output and status.
    
    Args:
        script: The AppleScript to run
        wait_for_output: Whether to wait for and capture output
    """
    try:
        if wait_for_output:
            # Run synchronously and capture output
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                check=True
            )
            return {
                "success": True,
                "output": result.stdout.strip()
            }
        else:
            # Use Popen for non-blocking execution
            subprocess.Popen(
                ['osascript', '-e', script], 
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            return {
                "success": True,
                "output": ""
            }
    except Exception as e:
        error_msg = str(e)
        return {
            "success": False,
            "error": error_msg,
        }

@mcp.tool()
def ask_chatgpt(prompt: str, wait_for_output: bool = False) -> Dict[str, Any]:
    """
    Send a prompt to ChatGPT macOS app using Shortcuts.
    
    Args:
        prompt: The text to send to ChatGPT
        wait_for_output: Whether to wait for ChatGPT to respond
    Returns:
        Dict containing operation status and response
    """
    try:
        if wait_for_output:
            # Use shortcuts command directly to capture output
            result = subprocess.run(
                ['shortcuts', 'run', 'Ask ChatGPT on Mac', '-i', prompt],
                capture_output=True,
                text=True,
                check=True
            )
            return {
                "operation": "ask_chatgpt",
                "status": "success",
                "message": result.stdout.strip()
            }
        else:
            # Run without waiting for output
            subprocess.Popen(
                ['shortcuts', 'run', 'Ask ChatGPT on Mac', '-i', prompt],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            return {
                "operation": "ask_chatgpt",
                "status": "success",
                "message": "Sent to ChatGPT (not waiting for response)"
            }
    except subprocess.CalledProcessError as e:
        return {
            "operation": "ask_chatgpt",
            "status": "error",
            "message": f"Shortcuts command failed: {e.stderr.strip() if e.stderr else str(e)}"
        }
    except Exception as e:
        return {
            "operation": "ask_chatgpt",
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }

def main():
    """Entry point for the MCP server."""
    mcp.run()

if __name__ == "__main__":
    main() 