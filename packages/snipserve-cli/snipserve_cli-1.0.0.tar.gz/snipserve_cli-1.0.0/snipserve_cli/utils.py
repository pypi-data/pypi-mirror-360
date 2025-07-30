# snipserve_cli/utils.py
import sys
from typing import Optional
import subprocess

def read_from_stdin() -> str:
    """Read content from stdin"""
    if sys.stdin.isatty():
        return ""
    return sys.stdin.read()

def open_in_editor(content: str = "", editor: Optional[str] = None) -> str:
    """Open content in external editor"""
    import tempfile
    import os
    
    editor = editor or os.getenv('EDITOR', 'nano')
    
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as f:
        f.write(content)
        f.flush()
        
        try:
            subprocess.run([editor, f.name], check=True)
            
            with open(f.name, 'r') as edited_file:
                return edited_file.read()
        finally:
            os.unlink(f.name)

def format_paste_table(pastes: list) -> str:
    """Format pastes as a table"""
    if not pastes:
        return "No pastes found."
    
    # Simple table formatting
    headers = ["ID", "Title", "Created", "Hidden"]
    rows = []
    
    for paste in pastes:
        created = paste.get('created_at', '')[:10]  # Just the date part
        hidden = "Yes" if paste.get('hidden') else "No"
        rows.append([
            paste.get('id', '')[:8],  
            paste.get('title', '')[:30],
            created,
            hidden
        ])
    
    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    
    # Format table
    result = []
    
    # Header
    header_row = " | ".join(h.ljust(w) for h, w in zip(headers, widths))
    result.append(header_row)
    result.append("-" * len(header_row))
    
    # Rows
    for row in rows:
        row_str = " | ".join(str(cell).ljust(w) for cell, w in zip(row, widths))
        result.append(row_str)
    
    return "\n".join(result)