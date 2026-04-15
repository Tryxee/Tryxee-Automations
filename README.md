# Tryxee Automations

Tryxee Automations is a **PyQt5** desktop application that provides a visual, node-based editor to design and run automation “flows”.

## Project layout

- **`blueprint_app.py`**
  - Main application (UI + node editor + flow execution)
  - Entry point: `main()`
- **`functions.py`**
  - Backend node implementations (a registry of Python callables)
  - Loaded dynamically at runtime by the app
- **`tryxee.ico`**
  - Application icon
- **`Tryxee Automations.bat`**
  - Convenience launcher for a local `venv` (runs `blueprint_app.py`)

## Architecture overview

### 1) UI layer (PyQt5)

The application is a classic Qt application:

- **`QApplication`** is created in `main()`.
- **`MainWindow`** (`QMainWindow`) builds the overall layout:
  - Top toolbar (run/save/import/clear/custom node)
  - Node library panel
  - Blueprint canvas (graphics view)
  - Properties panel
  - Log panel

The app uses a theme manager (`ThemeManager`) to drive a dark/light palette and update styling live.

### 2) Node model and editor

Nodes are described by a catalog (in `blueprint_app.py`) and rendered in a `QGraphicsScene`/`QGraphicsView`-based editor.

Key concepts:

- **Node definition**
  - Each node has an `id`, category, title, inputs/outputs, and parameters.
- **Canvas**
  - Nodes are visual items in the scene.
  - Connections represent data/exec links between ports.
- **Properties editing**
  - Selecting a node shows its editable parameters.

### 3) Backend execution

Flow execution is handled by `BackendRunner` in `blueprint_app.py`.

Responsibilities:

- **Dynamic loading of `functions.py`**
  - Uses `importlib.util.spec_from_file_location(..., functions.py)` to load/reload the backend.
- **Function registry**
  - Backend functions are exposed through a mapping of node `id` -> callable.
  - In `functions.py`, the `register()` decorator fills the `functions` dict.
- **Input collection**
  - During execution, inputs are collected from connected ports and/or node parameters.

### 4) Persistence / customization

- **Custom nodes**
  - Custom node definitions are saved to:
    - `~/.tryxee_automations_custom.json`
  - These are loaded on startup and appended to the node catalog.

## Development setup

### Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

### Run locally

```bash
python blueprint_app.py
```

Or use:

```bat
Tryxee Automations.bat
```

## Building with PyInstaller

This repo includes a ready-to-use PyInstaller spec:

- **`Tryxee Automations.spec`**

### Why a spec file?

This app:

- Uses a **relative icon path** (`QIcon("tryxee.ico")`).
- Loads `functions.py` **dynamically from disk** (via `importlib.util.spec_from_file_location`).

Both are typical reasons to use a `.spec` that explicitly bundles required files.

### Runtime hook

The build uses a small runtime hook:

- **`pyi_rth_tryxee_setcwd.py`**

When running from a frozen build, it sets the working directory to the PyInstaller extraction folder (`sys._MEIPASS`) so that relative file lookups (like `tryxee.ico` / `functions.py`) work.

### Build command

From the repo root:

```bash
pyinstaller "Tryxee Automations.spec" --clean --noconfirm
```

Artifacts are created under:

- `dist/Tryxee Automations/`

### Troubleshooting

- **Missing Qt plugin / platform plugin errors**
  - Ensure you are using the same Python environment you installed `PyQt5` into.
  - If the error persists, share the exact runtime error text and I can adjust the `.spec` (datas/hiddenimports) accordingly.

- **Antivirus / SmartScreen**
  - Windows may quarantine or warn on unsigned executables. This is expected for locally-built apps.
