import os
import subprocess
import sys
import abstract_parallels

def _run_script(script_path, args=None):
    """Execute a shell script from the package directory with optional arguments."""
    package_dir = os.path.dirname(abstract_parallels.__file__)
    full_path = os.path.join(package_dir, script_path)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Script not found: {full_path}")
    cmd = ['bash', full_path]
    if args:
        cmd.extend(args)
    subprocess.run(cmd, check=True)

def run_dashboard():
    _run_script('parallels_dashboard.sh', sys.argv[1:])

def run_setup():
    _run_script('parallels_setup.sh', sys.argv[1:])

def run_service_manager():
    _run_script('services_mgr/run_service_manager.sh', sys.argv[1:])

def run_clipit_gui():
    _run_script('clipit/run_clipit_gui.sh', sys.argv[1:])

def run_api_gui():
    _run_script('apis/run_api_gui.sh', sys.argv[1:])

def run_window_mgr():
    _run_script('window_mgr/run_clipit_window_mgr.sh', sys.argv[1:])

if __name__ == '__main__':
    print("This module is not meant to be run directly.")
