# Abstract Parallels (v0.0.1)

Abstract Parallels is a Python package that provides GUI-based tools for managing clipboard data, window information, systemd services, and APIs. It includes a dashboard for launching various components and a systemd service manager for remote service monitoring and control.

## Features
- **Clipboard Watcher**: Monitors clipboard changes and provides a GUI interface.
- **Window Info GUI**: Displays information about active windows.
- **Services Manager**: A PyQt5-based GUI for viewing and managing remote systemd services via SSH.
- **API GUI**: Interface for interacting with APIs (placeholder implementation).
- **Interactive Dashboard**: A bash-driven menu to launch different components.

## Installation

Install the package using pip:

```bash
pip install abstract_parallels
```

## Dependencies
- Python >= 3.6
- `flask`
- `paramiko`
- `PyQt5`
- Bash (for shell scripts)
- systemd (for service management)

## Usage

After installation, use the provided commands to launch components. These commands are available globally thanks to entry points.

### Launch the Dashboard
```bash
abstract-parallels-dashboard
```

This opens an interactive menu to select components like the Clipboard Watcher, Window Info GUI, or both.

### Manage Systemd Services
```bash
abstract-parallels-service-manager
```

This launches the PyQt5-based service viewer for remote systemd service management.

### Setup All Services
```bash
abstract-parallels-setup
```

This installs and starts all components as user systemd services.

### Available Commands
Run the setup script with different arguments:
```bash
abstract-parallels-setup            # Install and start all services
abstract-parallels-setup start      # Start all services
abstract-parallels-setup stop       # Stop all services
abstract-parallels-setup restart    # Restart all services
abstract-parallels-setup status     # Show service status
abstract-parallels-setup logs       # View service logs
```

## Modules
- `abstract_parallels.apis`: API GUI functionality.
- `abstract_parallels.clipit`: Clipboard monitoring tools.
- `abstract_parallels.services_mgr`: Systemd service management GUI.
- `abstract_parallels.window_mgr`: Window information GUI.

## Development
To contribute or modify the package:
1. Clone the repository (if available).
2. Install dependencies: `pip install -r requirements.txt`.
3. Build the package: `python -m build`.
4. Install locally: `pip install .`.

## License
MIT License. See [LICENSE](LICENSE) for details.