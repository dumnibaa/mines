## Mines Predictor 2025

A minimal CustomTkinter desktop GUI that shows a 5x5 grid and predicts tiles as mine or gem.

### Requirements
- Python 3.8+
- `customtkinter`

Install deps:

```bash
python -m pip install -r requirements.txt
```

### Run

```bash
python mines_predictor.py
```

### Package (optional)
You can create a single-file executable using PyInstaller:

```bash
python -m pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name MinesPredictor mines_predictor.py
```

On Windows, the built artifact is at `dist/MinesPredictor.exe`. On macOS/Linux, `dist/MinesPredictor`.

### Notes
- History file `mines_history.json` is stored next to the executable/script, avoiding current working directory issues.
- If fonts or emojis do not render on your platform, reduce font sizes or remove emoji characters in `mines_predictor.py`.