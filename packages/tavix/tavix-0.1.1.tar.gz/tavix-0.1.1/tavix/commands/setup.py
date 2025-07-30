import os
import typer
import subprocess
import platform
from pathlib import Path

app = typer.Typer()

# Conditional import for Windows-specific functionality
if platform.system() == "Windows":
    import winreg

def set_env_var_cross_platform(var_name, var_value):
    """Set environment variable permanently across platforms"""
    system = platform.system()
    
    if system == "Windows":
        return set_windows_env_var(var_name, var_value)
    elif system in ["Linux", "Darwin"]:  # Darwin is macOS
        return set_unix_env_var(var_name, var_value)
    else:
        typer.echo(f"⚠️  Unsupported platform: {system}")
        return False

def set_windows_env_var(var_name, var_value):
    """Set a Windows environment variable permanently"""
    try:
        # Set for current user
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, var_name, 0, winreg.REG_EXPAND_SZ, var_value)
        winreg.CloseKey(key)
        
        # Also set for current session
        os.environ[var_name] = var_value
        
        # Notify Windows about the change
        subprocess.run(["setx", var_name, var_value], capture_output=True)
        
        return True
    except Exception as e:
        typer.echo(f"❌ Error setting environment variable: {e}")
        return False

def set_unix_env_var(var_name, var_value):
    """Set environment variable on Linux/macOS"""
    try:
        # Detect shell and profile file
        shell = os.getenv("SHELL", "")
        home = Path.home()
        
        # Common shell profiles
        profiles = [
            home / ".bashrc",
            home / ".bash_profile", 
            home / ".zshrc",
            home / ".profile"
        ]
        
        # Find which profile exists and is writable
        target_profile = None
        for profile in profiles:
            if profile.exists() and os.access(profile, os.W_OK):
                target_profile = profile
                break
        
        if not target_profile:
            # Create .bashrc if no profile exists
            target_profile = home / ".bashrc"
        
        # Check if the export already exists
        export_line = f'export {var_name}="{var_value}"'
        
        with open(target_profile, "r") as f:
            content = f.read()
        
        if export_line not in content:
            # Add the export line
            with open(target_profile, "a") as f:
                f.write(f"\n# Tavix API Key\nexport {var_name}=\"{var_value}\"\n")
        
        # Set for current session
        os.environ[var_name] = var_value
        
        typer.echo(f"✅ Added to shell profile: {target_profile}")
        typer.echo("💡 Restart your terminal or run: source ~/.bashrc")
        
        return True
        
    except Exception as e:
        typer.echo(f"❌ Error setting environment variable: {e}")
        return False

def get_shell_profile_path():
    """Get the appropriate shell profile path for the current system"""
    system = platform.system()
    home = Path.home()
    
    if system == "Windows":
        return home / "Documents" / "WindowsPowerShell" / "Microsoft.PowerShell_profile.ps1"
    else:
        # Try to detect the current shell
        shell = os.getenv("SHELL", "")
        if "zsh" in shell:
            return home / ".zshrc"
        elif "bash" in shell:
            return home / ".bashrc"
        else:
            # Default to .bashrc
            return home / ".bashrc"

def check_shell_profile():
    """Check if API key is in shell profile"""
    profile_path = get_shell_profile_path()
    
    if profile_path.exists():
        try:
            with open(profile_path, "r") as f:
                content = f.read()
                if "GEMINI_API_KEY" in content:
                    return True, f"✅ Shell profile contains API key: {profile_path}"
                else:
                    return False, f"❌ Shell profile does not contain API key: {profile_path}"
        except Exception:
            return False, f"⚠️  Could not read shell profile: {profile_path}"
    else:
        return False, f"❌ Shell profile not found: {profile_path}"

def load_env_file():
    """Load environment variables from .env file if it exists"""
    env_file = Path(".env")
    if env_file.exists():
        try:
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key] = value
            return True
        except Exception as e:
            typer.echo(f"⚠️  Warning: Could not load .env file: {e}")
    return False

@app.command()
def set_key():
    """Quickly set your API key for the current session"""
    typer.echo("🔑 Quick API Key Setup")
    typer.echo("=" * 30)
    
    api_key = typer.prompt("Enter your Gemini API key", hide_input=True)
    
    if not api_key or len(api_key) < 10:
        typer.echo("❌ Invalid API key. Please try again.")
        raise typer.Exit(1)
    
    # Set for current session
    os.environ["GEMINI_API_KEY"] = api_key
    typer.echo("✅ API key set for current session!")
    typer.echo("💡 Note: This will be lost when you close the terminal.")
    typer.echo("💡 For permanent setup, run: tavix setup")
    
    # Test the API key
    test_api_key(api_key)
    typer.echo("\n🎉 Ready to use Tavix!")

def test_api_key(api_key):
    """Test the API key with different models"""
    typer.echo("\n🧪 Testing your API key...")
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        models_to_try = [
            "gemini-2.0-flash-exp",
            "gemini-2.0-flash",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-pro",
        ]
        
        working_model = None
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Hello")
                working_model = model_name
                typer.echo(f"✅ API key works with model: {model_name}")
                break
            except Exception:
                continue
        
        if not working_model:
            typer.echo("❌ API key test failed - no compatible models found")
            raise typer.Exit(1)
            
    except Exception as e:
        typer.echo(f"❌ API key test failed: {e}")
        raise typer.Exit(1)

@app.command()
def status():
    """Check the current setup status of Tavix"""
    typer.echo("🔍 Tavix Setup Status")
    typer.echo("=" * 40)
    
    # Try to load from .env file first
    env_loaded = load_env_file()
    if env_loaded:
        typer.echo("📁 ✅ .env file found and loaded")
    else:
        typer.echo("📁 ❌ No .env file found")
    
    # Check environment variable
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        typer.echo(f"🔑 ✅ API key is set: {api_key[:10]}...")
        
        # Test the API key
        test_api_key(api_key)
    else:
        typer.echo("🔑 ❌ API key is not set")
        typer.echo("💡 Run 'tavix setup' to configure")
        typer.echo("💡 Or run 'tavix set-key' for current session only")
    
    # Check shell profile
    profile_status, profile_message = check_shell_profile()
    typer.echo(profile_message)
    
    typer.echo("\n" + "=" * 40)

@app.command()
def setup():
    """Interactive setup for Tavix - configure your Gemini API key"""
    typer.echo("🚀 Welcome to Tavix Setup!")
    typer.echo("=" * 50)
    
    # Try to load from .env file first
    if load_env_file():
        typer.echo("📁 Loaded API key from .env file")
    
    # Check if API key is already set
    current_key = os.getenv("GEMINI_API_KEY")
    if current_key:
        typer.echo(f"✅ API key is already set: {current_key[:10]}...")
        if typer.confirm("Do you want to update it?"):
            pass
        else:
            typer.echo("Setup complete! You can now use Tavix.")
            return
    
    typer.echo("📋 To use Tavix, you need a Gemini API key:")
    typer.echo("1. Go to: https://makersuite.google.com/app/apikey")
    typer.echo("2. Sign in with your Google account")
    typer.echo("3. Click 'Create API Key'")
    typer.echo("4. Copy the generated key")
    
    api_key = typer.prompt("Enter your Gemini API key", hide_input=True)
    
    if not api_key or len(api_key) < 10:
        typer.echo("❌ Invalid API key. Please try again.")
        raise typer.Exit(1)
    
    # Show setup options based on platform
    system = platform.system()
    if system == "Windows":
        show_windows_options(api_key)
    else:
        show_unix_options(api_key)
    
    # Test the API key
    test_api_key(api_key)
    
    typer.echo("\n🎉 Setup complete! You can now use Tavix commands:")
    typer.echo("• tavix generate 'your command'")
    typer.echo("• tavix explain 'your command'")
    typer.echo("• tavix fix 'your command'")
    typer.echo("• tavix ask 'your question'")

def show_windows_options(api_key):
    """Show Windows-specific setup options"""
    typer.echo("\n💡 Choose how to save your API key:")
    typer.echo("1. Set for current session only (temporary)")
    typer.echo("2. Add to PowerShell profile (permanent for PowerShell)")
    typer.echo("3. Add to system environment variables (permanent for all)")
    typer.echo("4. Create a .env file in current directory")
    
    choice = typer.prompt("Choose option (1-4)", type=int)
    
    if choice == 1:
        # Set for current session
        os.environ["GEMINI_API_KEY"] = api_key
        typer.echo("✅ API key set for current session!")
        typer.echo("💡 Note: This will be lost when you close the terminal.")
        
    elif choice == 2:
        # Add to PowerShell profile
        try:
            profile_path = Path.home() / "Documents" / "WindowsPowerShell" / "Microsoft.PowerShell_profile.ps1"
            profile_path.parent.mkdir(parents=True, exist_ok=True)
            with open(profile_path, "a") as f:
                f.write(f'\n$env:GEMINI_API_KEY = "{api_key}"\n')
            typer.echo(f"✅ Added to PowerShell profile: {profile_path}")
            typer.echo("💡 Restart PowerShell or run: . $PROFILE")
        except Exception as e:
            typer.echo(f"❌ Error: {e}")
            typer.echo("💡 You can manually add this line to your PowerShell profile:")
            typer.echo(f'$env:GEMINI_API_KEY = "{api_key}"')
        # Set for current session as well
        os.environ["GEMINI_API_KEY"] = api_key
        typer.echo("✅ API key set for current session!")
        
    elif choice == 3:
        # System environment variables
        typer.echo("🔧 Attempting to set system environment variable...")
        if set_windows_env_var("GEMINI_API_KEY", api_key):
            typer.echo("✅ Successfully set system environment variable!")
            typer.echo("💡 You may need to restart your terminal for changes to take effect.")
        else:
            typer.echo("⚠️  Could not set system environment variable automatically.")
            typer.echo("🔧 Please set it manually:")
            typer.echo("1. Press Win + R, type 'sysdm.cpl', press Enter")
            typer.echo("2. Click 'Environment Variables'")
            typer.echo("3. Under 'User variables', click 'New'")
            typer.echo("4. Variable name: GEMINI_API_KEY")
            typer.echo(f"5. Variable value: {api_key}")
            typer.echo("6. Click OK and restart your terminal")
        # Set for current session as well
        os.environ["GEMINI_API_KEY"] = api_key
        typer.echo("✅ API key set for current session!")
        
    elif choice == 4:
        # Create .env file
        env_file = Path(".env")
        with open(env_file, "w") as f:
            f.write(f"GEMINI_API_KEY={api_key}\n")
        typer.echo(f"✅ Created .env file: {env_file.absolute()}")
        typer.echo("💡 Note: You'll need to load this file in your scripts")
        # Set for current session as well
        os.environ["GEMINI_API_KEY"] = api_key
        typer.echo("✅ API key set for current session!")
    
    else:
        typer.echo("❌ Invalid choice. Setup cancelled.")
        raise typer.Exit(1)

def show_unix_options(api_key):
    """Show Unix/Linux/macOS setup options"""
    typer.echo("\n💡 Choose how to save your API key:")
    typer.echo("1. Set for current session only (temporary)")
    typer.echo("2. Add to shell profile (permanent - recommended)")
    typer.echo("3. Create a .env file in current directory")
    
    choice = typer.prompt("Choose option (1-3)", type=int)
    
    if choice == 1:
        # Set for current session
        os.environ["GEMINI_API_KEY"] = api_key
        typer.echo("✅ API key set for current session!")
        typer.echo("💡 Note: This will be lost when you close the terminal.")
        
    elif choice == 2:
        # Add to shell profile
        if set_unix_env_var("GEMINI_API_KEY", api_key):
            typer.echo("✅ Successfully added to shell profile!")
            typer.echo("💡 Restart your terminal or run: source ~/.bashrc")
        else:
            typer.echo("⚠️  Could not add to shell profile automatically.")
            typer.echo("💡 You can manually add this line to your shell profile:")
            typer.echo(f'export GEMINI_API_KEY="{api_key}"')
        # Set for current session as well
        os.environ["GEMINI_API_KEY"] = api_key
        typer.echo("✅ API key set for current session!")
        
    elif choice == 3:
        # Create .env file
        env_file = Path(".env")
        with open(env_file, "w") as f:
            f.write(f"GEMINI_API_KEY={api_key}\n")
        typer.echo(f"✅ Created .env file: {env_file.absolute()}")
        typer.echo("💡 Note: You'll need to load this file in your scripts")
        # Set for current session as well
        os.environ["GEMINI_API_KEY"] = api_key
        typer.echo("✅ API key set for current session!")
    
    else:
        typer.echo("❌ Invalid choice. Setup cancelled.")
        raise typer.Exit(1)

if __name__ == "__main__":
    app() 