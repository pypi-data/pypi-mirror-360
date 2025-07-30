import click
import sys
from typing import Optional
from .api import SnipServeAPI
from .config import load_config, save_config, get_api_key, get_base_url
from .utils import read_from_stdin, open_in_editor, format_paste_table
import subprocess
import os

@click.group()
@click.version_option()
def cli():
    """SnipServe CLI - Manage your pastes from the command line"""
    pass

@cli.group()
def config():
    """Manage CLI configuration"""
    pass

@config.command('set-key')
@click.argument('api_key')
def set_api_key(api_key: str):
    """Set your SnipServe API key"""
    config_data = load_config()
    config_data['api_key'] = api_key
    save_config(config_data)
    click.echo("✅ API key saved successfully!")

@config.command('set-url')
@click.argument('url')
def set_base_url(url: str):
    """Set your SnipServe instance URL"""
    config_data = load_config()
    config_data['base_url'] = url.rstrip('/')
    save_config(config_data)
    click.echo(f"✅ Base URL set to: {url}")

@config.command('show')
def show_config():
    """Show current configuration"""
    config_data = load_config()
    click.echo("Current configuration:")
    click.echo(f"  API Key: {'*' * 8}...{get_api_key()[-4:] if get_api_key() else 'Not set'}")
    click.echo(f"  Base URL: {get_base_url()}")

@cli.command()
@click.argument('title')
@click.option('--content', '-c', help='Paste content')
@click.option('--file', '-f', type=click.File('r'), help='Read content from file')
@click.option('--editor', '-e', is_flag=True, help='Open editor for content')
@click.option('--hidden', is_flag=True, help='Make paste hidden')
def create(title: str, content: Optional[str], file, editor: bool, hidden: bool):
    """Create a new paste"""
    try:
        api = SnipServeAPI()
        
        # Determine content source
        if content:
            paste_content = content
        elif file:
            paste_content = file.read()
        elif editor:
            paste_content = open_in_editor()
        else:
            # Try reading from stdin
            paste_content = read_from_stdin()
            if not paste_content:
                paste_content = open_in_editor()
        
        if not paste_content.strip():
            click.echo("❌ Error: No content provided", err=True)
            sys.exit(1)
        
        result = api.create_paste(title, paste_content, hidden)
        
        click.echo("✅ Paste created successfully!")
        click.echo(f"   ID: {result['id']}")
        click.echo(f"   URL: {get_base_url()}/paste/{result['id']}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('paste_id')
def get(paste_id: str):
    """Get a paste by ID"""
    try:
        api = SnipServeAPI()
        paste = api.get_paste(paste_id)
        
        click.echo(f"Title: {paste['title']}")
        click.echo(f"Created: {paste['created_at'][:10]}")
        click.echo(f"Hidden: {'Yes' if paste.get('hidden') else 'No'}")
        click.echo(f"Views: {paste.get('view_count', 0)}")
        click.echo("\nContent:")
        click.echo("-" * 40)
        click.echo(paste['content'])
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@cli.command()
def list():
    """List your pastes"""
    try:
        api = SnipServeAPI()
        result = api.list_pastes()
        pastes = result
        
        if pastes:
            click.echo(format_paste_table(pastes))
        else:
            click.echo("No pastes found.")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('paste_id')
@click.option('--title', help='New title')
@click.option('--content', help='New content')
@click.option('--file', '-f', type=click.File('r'), help='Read new content from file')
@click.option('--editor', '-e', is_flag=True, help='Edit content in editor')
@click.option('--hidden/--public', default=None, help='Change visibility')
def update(paste_id: str, title: Optional[str], content: Optional[str], file, editor: bool, hidden: Optional[bool]):
    """Update an existing paste"""
    try:
        api = SnipServeAPI()
        
        # Check if at least one update option is provided
        if not any([title, content, file, editor, hidden is not None]):
            click.echo("❌ Error: At least one update option must be provided", err=True)
            click.echo("Use --title, --content, --file, --editor, or --hidden/--public")
            sys.exit(1)
        
        # Get new content if requested
        new_content = content
        if file:
            new_content = file.read()
        elif editor:
            # Get current content for editing
            current = api.get_paste(paste_id)
            new_content = open_in_editor(current['content'])
        
        result = api.update_paste(paste_id, title, new_content, hidden)
        
        click.echo("✅ Paste updated successfully!")
        click.echo(f"   URL: {get_base_url()}/paste/{paste_id}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('paste_id')
@click.confirmation_option(prompt='Are you sure you want to delete this paste?')
def delete(paste_id: str):
    """Delete a paste"""
    try:
        api = SnipServeAPI()
        api.delete_paste(paste_id)
        click.echo("✅ Paste deleted successfully!")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@cli.command()
def whoami():
    """Show current user information"""
    try:
        api = SnipServeAPI()
        user = api.get_user_info()
        
        click.echo(f"Username: {user['username']}")
        click.echo(f"Admin: {'Yes' if user.get('is_admin') else 'No'}")
        click.echo(f"Member since: {user['created_at'][:10]}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    cli()

def get_default_editor():
    """Get default editor based on platform"""
    import platform
    
    if platform.system() == 'Windows':
        # Try common Windows editors
        editors = ['notepad.exe', 'code', 'notepad++']
        for editor in editors:
            if subprocess.run(['where', editor], capture_output=True).returncode == 0:
                return editor
        return 'notepad'  # Fallback to notepad
    else:
        return os.getenv('EDITOR', 'nano')

def open_in_editor(content: str = "", editor: Optional[str] = None) -> str:
    """Open content in external editor"""
    import tempfile
    import os
    import time
    import platform
    
    editor = editor or get_default_editor()
    
    # Create temp file
    fd, temp_path = tempfile.mkstemp(suffix='.txt', text=True)
    
    try:
        # Write content to temp file
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Open editor
        if platform.system() == 'Windows':
            # On Windows, use shell=True for better editor compatibility
            result = subprocess.run([editor, temp_path], shell=True, check=True)
        else:
            result = subprocess.run([editor, temp_path], check=True)
        
        # Read the edited content
        with open(temp_path, 'r', encoding='utf-8') as f:
            return f.read()
            
    except subprocess.CalledProcessError:
        raise Exception(f"Editor '{editor}' failed or was cancelled")
    except FileNotFoundError:
        raise Exception(f"Editor '{editor}' not found")
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_path)
        except OSError:
            pass  # Ignore cleanup errors