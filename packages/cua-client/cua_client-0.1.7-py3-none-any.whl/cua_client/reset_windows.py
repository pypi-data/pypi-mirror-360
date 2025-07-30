"""
CUA Client Reset Command

This module provides the reset functionality for the CUA client,
which runs the PowerShell reset script on Windows systems.
"""

import platform
import subprocess
import sys

try:
    from importlib import resources
except ImportError:
    # Fallback for Python < 3.9
    import importlib_resources as resources


def reset_cli():
    """CLI entry point for the cua-client-reset command"""
    try:
        # Check if we're on Windows
        if platform.system() != "Windows":
            print("❌ The reset script is only available on Windows systems.")
            print("💡 This command runs PowerShell scripts designed for Windows environments.")
            sys.exit(1)
        
        # Find the PowerShell script using importlib.resources
        try:
            script_files = resources.files('cua_client.windows')
            script_path = script_files / 'reset_cua_client.ps1'
            
            # Convert to actual file path and execute
            with resources.as_file(script_path) as script_file:
                print(f"🔄 Running CUA Client Reset Script...")
                print(f"📂 Script location: {script_file}")
                
                # Execute PowerShell script
                cmd = [
                    "PowerShell.exe",
                    "-ExecutionPolicy", "Bypass",
                    "-File", str(script_file)
                ]
                
                print(f"🚀 Executing: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=False, text=True)
                
                if result.returncode == 0:
                    print("✅ Reset script completed successfully!")
                else:
                    print(f"❌ Reset script failed with exit code: {result.returncode}")
                    sys.exit(result.returncode)
                    
        except Exception as e:
            print(f"❌ Error locating or running reset script: {e}")
            print("💡 Make sure the cua-client package is properly installed.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Reset script interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    reset_cli() 