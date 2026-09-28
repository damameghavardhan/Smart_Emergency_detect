# Sentinel Traffic Control

A desktop portfolio project with a responsively embedded in PyQt6. A Qt WebChannel connects frontend controls to Python-owned traffic-signal state, countdowns, event logging, and a local OpenCV camera preview.

## Features

- Operator-controlled ambulance-priority simulation with a configurable 5-120 second window, countdown, automatic reset, and manual release.
- HTML dashboard embedded in Qt WebEngine, with JSON state updates through Qt WebChannel.
- OpenCV camera capture on a `QThread`, resized to at most 640x360 and capped at 15 preview frames per second.
- Responsive layout, signal visualization, connection metrics, device selector, and a timestamped session activity log.
- Unit-tested signal state machine, separate from the GUI.

Camera video remains a local preview and is not saved. Emergency activation is manual; automatic vehicle detection is not implemented. This is a simulation, not a real traffic-control system, and must not connect to public-road infrastructure.

## Setup (Windows PowerShell)

```powershell
cd "C:\path\to\PROJECT1"
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python PyQt.py
```

Use the device selector if your webcam is not device `0`. Camera access depends on OS permissions and device availability. Google Fonts are optional; local system font fallbacks are provided.

## VS Code workflow

Open the `PROJECT1` folder as the workspace and complete setup above. The included `.vscode` files configure the project virtual environment, Pylance basic type checking and auto-import completions, unittest discovery, an F5 `Sentinel: Run and Debug` profile, and Run Application / Run Tests tasks. Install the Microsoft Python, Python Debugger, and Pylance extensions if VS Code prompts for them. If the virtual environment was created after opening the project, run **Python: Select Interpreter** and choose `.venv` once.

Use **F5** to launch the dashboard with breakpoints enabled. Use **Terminal: Run Task** to run the app or test suite, or run `PyQt.py` from the editor.

## Tests

```powershell
python -m unittest -v test_emergency.py
python -m py_compile PyQt.py web_dashboard.py Camera.py Emergency.py
```

## Project structure

- `Front.html` and `Front.css` - dashboard interface, responsive styles, and browser interactions.
- `PyQt.py` - desktop application entry point.
- `web_dashboard.py` - Qt WebEngine host, Python-WebChannel bridge, signal lifecycle, and camera coordination.
- `Emergency.py` - UI-independent emergency signal state machine.
- `Camera.py` - throttled OpenCV preview worker.
- `test_emergency.py` - signal controller tests.
