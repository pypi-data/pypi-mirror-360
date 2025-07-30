#!/usr/bin/env python3
"""Test script to verify wheel installation includes rules properly."""

import subprocess
import sys
import tempfile
import shutil
from pathlib import Path

def test_wheel_installation():
    """Test that installing from wheel includes the rules."""
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create a test virtual environment
        venv_path = temp_path / "test_venv"
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        
        # Get the venv python executable
        if sys.platform == "win32":
            python_exe = venv_path / "Scripts" / "python.exe"
        else:
            python_exe = venv_path / "bin" / "python"
        
        # Install the wheel
        wheel_path = Path("dist") / "adversary_mcp_server-0.6.2-py3-none-any.whl"
        subprocess.run([str(python_exe), "-m", "pip", "install", str(wheel_path)], check=True)
        
        # Test that rules are accessible
        test_code = """
import sys
from pathlib import Path
from adversary_mcp_server.threat_engine import ThreatEngine, get_user_rules_directory

# Create a ThreatEngine instance
engine = ThreatEngine()

# Check that rules were loaded
print(f"Total rules loaded: {len(engine.rules)}")
print(f"Built-in rules directory: {get_user_rules_directory() / 'built-in'}")

# Check if built-in rules directory exists and has files
builtin_dir = get_user_rules_directory() / 'built-in'
if builtin_dir.exists():
    yaml_files = list(builtin_dir.glob('*.yaml'))
    print(f"Built-in rule files found: {len(yaml_files)}")
    for rule_file in yaml_files:
        print(f"  - {rule_file.name}")
else:
    print("ERROR: Built-in rules directory not found!")
    sys.exit(1)

# Verify we have a good number of rules
if len(engine.rules) < 50:
    print(f"ERROR: Expected at least 50 rules, got {len(engine.rules)}")
    sys.exit(1)

print("SUCCESS: Rules are properly installed and accessible!")
"""
        
        # Run the test code
        result = subprocess.run([str(python_exe), "-c", test_code], 
                              capture_output=True, text=True)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode != 0:
            print(f"Test failed with return code {result.returncode}")
            return False
        
        print("Test passed!")
        return True

if __name__ == "__main__":
    success = test_wheel_installation()
    sys.exit(0 if success else 1) 