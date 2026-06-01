import os
import sys
import subprocess

def main():
    print("=== TESS Lightcurve Studio (.exe) Packaging Script ===")
    
    # 1. Verify we are on Windows
    if not sys.platform.startswith('win'):
        print("Warning: This script is intended to be run on Windows to generate a Windows .exe file.")
        print("If you run it on Linux/macOS, it will compile a binary for that platform instead.")
        ans = input("Do you want to continue anyway? (y/N): ").strip().lower()
        if ans != 'y':
            sys.exit(0)
            
    # 2. Check if pyinstaller is installed
    try:
        import PyInstaller
        print("PyInstaller is installed.")
    except ImportError:
        print("PyInstaller not found. Installing PyInstaller via pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # 3. Resolve directory and run pyinstaller
    script_dir = os.path.dirname(os.path.abspath(__file__))
    spec_file = os.path.join(script_dir, "tess_manager.spec")
    
    print(f"Running PyInstaller on spec file: {spec_file}")
    
    cmd = [
        "pyinstaller",
        "--clean",
        spec_file
    ]
    
    try:
        subprocess.check_call(cmd, cwd=script_dir)
        print("\n==============================================")
        print("🎉 Windows executable successfully created:")
        print(f"   {os.path.join(script_dir, 'dist', 'TESS_Lightcurve_Studio.exe')}")
        print("==============================================")
    except subprocess.CalledProcessError as e:
        print(f"Error during compilation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
