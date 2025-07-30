"""
Utility functions for LLM Chat
"""

import tiktoken
import textwrap
import time
import sys
from rich.console import Console
from rich.markdown import Markdown
from termcolor import colored


def count_tokens(text, model):
    """
    Count tokens in the given text.

    Args:
        text (str): The text to count tokens for
        model (str): The model name (currently unused, but kept for future model-specific counting)

    Returns:
        int: Number of tokens in the text
    """
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def print_wrapped_text(text, width=80, indent="  "):
    """
    Print text with proper wrapping.

    Args:
        text (str): The text to wrap and print
        width (int): Maximum line width
        indent (str): Indentation string to prepend to each line
    """
    wrapped_lines = textwrap.wrap(text, width=width)
    for line in wrapped_lines:
        print(f"{indent}{line}")


def render_markdown(text, stream_mode=False, last_chunk=""):
    """
    Render text as markdown.

    Args:
        text (str): The markdown text to render
        stream_mode (bool): Whether to render in stream mode
        last_chunk (str): The last chunk that was rendered (used in stream mode)
    """
    console = Console()
    md = Markdown(text)
    
    if stream_mode:
        # Only render the new addition to the text
        new_text = text[len(last_chunk):]
        if new_text:
            # Print without the markdown formatting for streaming
            sys.stdout.write(new_text)
            sys.stdout.flush()
    else:
        # Full render with markdown formatting
        console.print(md)
        
def stream_with_markdown_chunks(chunks, code_blocks=True):
    """
    Stream text with special handling for code blocks.
    Simple implementation: stream normally until ```, then buffer until closing ```.
    """
    full_response = ""
    in_code_block = False
    buffer = ""
    showed_generating_message = False
    console = Console()
    
    for chunk in chunks:
        if chunk is None:
            continue
            
        full_response += chunk
        buffer += chunk
        
        # Keep processing buffer while we have ``` markers
        while True:
            if not in_code_block:
                # Look for opening ```
                marker_pos = buffer.find("```")
                if marker_pos == -1:
                    break  # No more markers
                
                # Output everything before ```
                before_marker = buffer[:marker_pos]
                if before_marker:
                    sys.stdout.write(before_marker)
                    sys.stdout.flush()
                
                # Show generating message
                sys.stdout.write(colored("\n> Generating code... ", "cyan"))
                sys.stdout.flush()
                showed_generating_message = True
                
                # Switch to code block mode, keeping ``` and everything after
                in_code_block = True
                buffer = buffer[marker_pos:]
            else:
                # In code block, look for closing ``` (but not at position 0)
                # We need to find the SECOND occurrence of ```
                first_marker = buffer.find("```")
                if first_marker != 0:
                    # Something went wrong, treat as closing
                    marker_pos = first_marker
                else:
                    # Skip the opening ``` and find the next one
                    marker_pos = buffer.find("```", 3)
                
                if marker_pos == -1:
                    break  # No closing marker yet, keep buffering
                
                # Include everything up to and including the closing ```
                code_block = buffer[:marker_pos + 3]
                
                # Clear generating message
                if showed_generating_message:
                    sys.stdout.write("\r" + " " * 30 + "\r")
                    sys.stdout.flush()
                    showed_generating_message = False
                
                # Display the code block with markdown
                console.print(Markdown(code_block))
                
                # Switch out of code block mode
                in_code_block = False
                buffer = buffer[marker_pos + 3:]  # Continue with rest
        
        # If not in code block and buffer doesn't contain ```, handle it
        if not in_code_block and buffer and "```" not in buffer:
            # Check if buffer has markdown elements that need rendering
            markdown_markers = ["#", "**", "*", "_", ">", "- ", "1. ", "![", "[", "|", "`"]
            has_markdown = any(marker in buffer for marker in markdown_markers)
            
            # If it has markdown and looks complete (ends with double newline or is getting long)
            if has_markdown and (buffer.endswith("\n\n") or (buffer.endswith("\n") and len(buffer) > 200)):
                console.print(Markdown(buffer.rstrip()))
                buffer = ""
            # If no markdown, stream it directly
            elif not has_markdown:
                sys.stdout.write(buffer)
                sys.stdout.flush()
                buffer = ""
            # If single line with newline and no special markdown, stream it
            elif buffer.count("\n") == 1 and buffer.endswith("\n") and not any(m in buffer for m in ["#", "|", "-", "*", ">"]):
                sys.stdout.write(buffer)
                sys.stdout.flush()
                buffer = ""
            # Otherwise keep buffering (has markdown but not complete section yet)
    
    # Handle any remaining content
    if buffer:
        if in_code_block:
            # Unclosed code block
            if showed_generating_message:
                sys.stdout.write("\r" + " " * 30 + "\r")
                sys.stdout.flush()
            # Add closing markers and display
            if not buffer.endswith("```"):
                buffer += "\n```"
            console.print(Markdown(buffer))
        else:
            # Regular text - check if it needs markdown rendering
            markdown_markers = ["#", "**", "*", "_", ">", "- ", "1. ", "![", "[", "|", "`"]
            has_markdown = any(marker in buffer for marker in markdown_markers)
            
            if has_markdown:
                console.print(Markdown(buffer))
            else:
                sys.stdout.write(buffer)
                sys.stdout.flush()
    
    return full_response


def print_available_models(models):
    print(colored("\nAvailable models:", "cyan"))
    for p, m_list in models.items():
        print(colored(f"{p.capitalize()}:", "yellow"))
        for m in m_list:
            print(colored(f"  - {m}", "green"))


def create_typing_animation(text="Thinking", color="cyan"):
    """
    Create a typing animation effect.

    Args:
        text (str): The text to display before the animation
        color (str): The color to use for the animation
    """
    animations = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
    i = 0
    start_time = time.time()
    sys.stdout.write(colored(f"{text} ", color))
    sys.stdout.flush()

    while time.time() - start_time < 0.5:  # Reduced animation time to 0.5 seconds
        sys.stdout.write(colored(f"\r{text} {animations[i % len(animations)]}", color))
        sys.stdout.flush()
        time.sleep(0.05)  # Faster animation updates
        i += 1

    sys.stdout.write(colored(f"\r{text}   \n", color))
    sys.stdout.flush()
