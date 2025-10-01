import os
import sys
import json
import random

try:
    import customtkinter as ctk
except ImportError as exc:
    raise SystemExit(
        "customtkinter is required. Install with: pip install customtkinter"
    ) from exc


class MinesPredictorApp(ctk.CTk):
    def __init__(self, history_filename: str = "mines_history.json"):
        super().__init__()

        # Window setup
        self.title("Mines Predictor 2025")
        self.geometry("600x700")
        self.resizable(False, False)

        # History file path (store next to executable/script to avoid CWD issues)
        self.app_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        self.history_file = os.path.join(self.app_dir, history_filename)
        self.history = self.load_history()

        # Title
        self.label = ctk.CTkLabel(
            self,
            text="💎 Mines Predictor 💣",
            font=("Arial Rounded MT Bold", 28),
            text_color="#00ffcc",
        )
        self.label.pack(pady=20)

        # Input / Controls area
        self.top_frame = ctk.CTkFrame(self, corner_radius=16)
        self.top_frame.pack(padx=16, pady=8, fill="x")

        self.input_label = ctk.CTkLabel(
            self.top_frame,
            text="Enter last match bombs (e.g. r2 t3, r4 t2, r1 t5):",
            anchor="w",
        )
        self.input_label.pack(padx=12, pady=(12, 4), fill="x")

        self.input_entry = ctk.CTkEntry(self.top_frame, placeholder_text="r2 t3, r4 t2, r1 t5")
        self.input_entry.pack(padx=12, pady=(0, 12), fill="x")

        self.controls_row = ctk.CTkFrame(self.top_frame)
        self.controls_row.pack(padx=12, pady=(0, 12), fill="x")

        self.add_btn = ctk.CTkButton(
            self.controls_row,
            text="➕ Add Match",
            fg_color=("#2ecc71", "#1e7e34"),
            hover_color=("#27ae60", "#155d27"),
            command=self.add_match_from_input,
            corner_radius=10,
        )
        self.add_btn.pack(side="left", padx=6)

        self.undo_btn = ctk.CTkButton(
            self.controls_row,
            text="↩ Undo",
            fg_color=("#f39c12", "#a96800"),
            hover_color=("#d68910", "#7a4d00"),
            command=self.undo_last_match,
            corner_radius=10,
        )
        self.undo_btn.pack(side="left", padx=6)

        self.predict_btn2 = ctk.CTkButton(
            self.controls_row,
            text="🔮 Predict",
            fg_color=("#00adb5", "#007f88"),
            hover_color=("#00ced1", "#0097a7"),
            corner_radius=10,
            command=self.update_heatmap,
        )
        self.predict_btn2.pack(side="left", padx=6)

        self.reset_btn = ctk.CTkButton(
            self.controls_row,
            text="🧼 Reset Board",
            fg_color=("#95a5a6", "#5f6a6a"),
            hover_color=("#7f8c8d", "#4d5656"),
            command=self.reset_board,
            corner_radius=10,
        )
        self.reset_btn.pack(side="left", padx=6)

        self.status_label = ctk.CTkLabel(self.top_frame, text="", text_color="#d0d3d4")
        self.status_label.pack(padx=12, pady=(0, 8), fill="x")

        # Frame for grid
        self.grid_frame = ctk.CTkFrame(self, corner_radius=20)
        self.grid_frame.pack(pady=10)

        # Buttons grid
        self.buttons = []
        for row in range(5):
            row_buttons = []
            for col in range(5):
                btn = ctk.CTkButton(
                    self.grid_frame,
                    width=90,
                    height=90,
                    text="🟦",
                    font=("Arial", 36, "bold"),
                    fg_color=("#222831", "#1a1a1a"),
                    hover_color=("#393e46", "#2b2b2b"),
                    corner_radius=15,
                    command=lambda r=row, c=col: self.reveal_tile(r, c),
                )
                btn.grid(row=row, column=col, padx=6, pady=6)
                row_buttons.append(btn)
            self.buttons.append(row_buttons)

        # Footer controls
        self.control_frame = ctk.CTkFrame(self, corner_radius=15)
        self.control_frame.pack(pady=12)

        self.quit_btn = ctk.CTkButton(
            self.control_frame,
            text="❌ Exit",
            font=("Arial Rounded MT Bold", 18),
            fg_color=("#ff4444", "#cc0000"),
            hover_color=("#ff6666", "#e60000"),
            corner_radius=12,
            command=self.on_exit,
        )
        self.quit_btn.pack(side="left", padx=20, pady=10)

        # Bind window close to graceful exit
        self.protocol("WM_DELETE_WINDOW", self.on_exit)

    # -------------------------------
    # Reveal Prediction
    # -------------------------------
    def reveal_tile(self, row: int, col: int) -> None:
        pred = self.predict_tile(row, col)
        btn = self.buttons[row][col]

        if pred == "mine":
            btn.configure(text="💣", fg_color=("#ff1e56", "#a7002e"), text_color="white")
        else:
            btn.configure(text="💎", fg_color=("#00ffcc", "#008f77"), text_color="black")

    # -------------------------------
    # Prediction Logic (basic)
    # -------------------------------
    def predict_tile(self, row: int, col: int) -> str:
        # Use risk_map if available; fallback to simple random
        if hasattr(self, "risk_map") and self.risk_map:
            risk = self.risk_map.get((row, col), 0.0)
            # Threshold tuned for 3 mines (rough heuristic)
            return "mine" if risk >= 0.5 else "gem"
        return "mine" if random.random() < 0.12 else "gem"

    # -------------------------------
    # Reset Board
    # -------------------------------
    def reset_board(self) -> None:
        for row_buttons in self.buttons:
            for btn in row_buttons:
                btn.configure(text="🟦", fg_color=("#222831", "#1a1a1a"), text_color="white")
        self.status_label.configure(text="")
        self.risk_map = {}
        self.highlight_top_mines([])

    # -------------------------------
    # Input parsing and history
    # -------------------------------
    def parse_bombs(self, text: str):
        # Expected like: r2 t3, r4 t2, r1 t5
        bombs = []
        if not text.strip():
            return bombs
        chunks = [c.strip() for c in text.split(",") if c.strip()]
        for chunk in chunks:
            parts = chunk.lower().replace(";", ",").split()
            row_val = None
            col_val = None
            for p in parts:
                if p.startswith("r") and p[1:].isdigit():
                    row_val = int(p[1:])
                if p.startswith("t") and p[1:].isdigit():
                    col_val = int(p[1:])
            if row_val is not None and col_val is not None:
                if 1 <= row_val <= 5 and 1 <= col_val <= 5:
                    bombs.append((row_val - 1, col_val - 1))
        # Deduplicate
        return list(dict.fromkeys(bombs))

    def add_match_from_input(self) -> None:
        raw = self.input_entry.get()
        bombs = self.parse_bombs(raw)
        if len(bombs) != 3:
            self.status_label.configure(text="Please enter exactly 3 bombs like: r2 t3, r4 t2, r1 t5")
            return
        self.history.append({"bombs": bombs})
        self.save_history()
        self.status_label.configure(text=f"Added match with bombs: {[(r+1, c+1) for r,c in bombs]}")
        self.input_entry.delete(0, "end")
        self.update_heatmap()

    def undo_last_match(self) -> None:
        if self.history:
            self.history.pop()
            self.save_history()
            self.status_label.configure(text="Undid last match")
        else:
            self.status_label.configure(text="No history to undo")
        self.update_heatmap()

    # -------------------------------
    # Risk model and heatmap
    # -------------------------------
    def build_risk_map(self):
        # Simple frequency model: risk proportional to how often a cell was a bomb
        counts = {(r, c): 0 for r in range(5) for c in range(5)}
        total_matches = 0
        for match in self.history:
            bombs = match.get("bombs", [])
            if not isinstance(bombs, list):
                continue
            total_matches += 1
            for (r, c) in bombs:
                if (r, c) in counts:
                    counts[(r, c)] += 1
        # Normalize to [0,1]
        risk_map = {}
        if total_matches > 0:
            max_count = max(counts.values()) or 1
            for key, val in counts.items():
                # weight by total_matches to avoid tiny sample noise
                normalized = val / max_count
                risk_map[key] = normalized
        else:
            risk_map = {k: 0.0 for k in counts}
        return risk_map

    def color_for_risk(self, risk: float):
        # Map risk [0..1] to color from safe (teal) to danger (red)
        # Choose two palette stops
        safe = (0, 255, 204)    # #00ffcc
        danger = (255, 30, 86)  # #ff1e56
        r = int(safe[0] + (danger[0] - safe[0]) * risk)
        g = int(safe[1] + (danger[1] - safe[1]) * risk)
        b = int(safe[2] + (danger[2] - safe[2]) * risk)
        return f"#{r:02x}{g:02x}{b:02x}"

    def highlight_top_mines(self, coords):
        # Reset texts/colors to base, then highlight top coordinates with bomb icon
        for r in range(5):
            for c in range(5):
                self.buttons[r][c].configure(text="🟦", text_color="white")
        for (r, c) in coords:
            self.buttons[r][c].configure(text="💣", text_color="white")

    def update_heatmap(self) -> None:
        self.risk_map = self.build_risk_map()
        # Compute top-3 by risk
        sorted_cells = sorted(self.risk_map.items(), key=lambda kv: kv[1], reverse=True)
        top3 = [cell for cell, score in sorted_cells[:3] if score > 0]
        self.highlight_top_mines(top3)
        # Apply background colors by risk
        for r in range(5):
            for c in range(5):
                risk = self.risk_map.get((r, c), 0.0)
                color = self.color_for_risk(risk)
                # Darken for dark mode second color
                self.buttons[r][c].configure(fg_color=(color, color))
        if top3:
            pretty_top = [(r + 1, c + 1) for (r, c) in top3]
            self.status_label.configure(text=f"Predicted bomb tiles: {pretty_top}")
        else:
            self.status_label.configure(text="Not enough history yet. Add matches to improve predictions.")

    # -------------------------------
    # History Handling
    # -------------------------------
    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as file_handle:
                    return json.load(file_handle)
            except (json.JSONDecodeError, OSError):
                return []
        return []

    def save_history(self) -> None:
        try:
            with open(self.history_file, "w", encoding="utf-8") as file_handle:
                json.dump(self.history, file_handle)
        except OSError:
            # Ignore save errors silently to avoid crashing on exit
            pass

    # -------------------------------
    # Exit handling
    # -------------------------------
    def on_exit(self) -> None:
        self.save_history()
        self.destroy()


def main() -> None:
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = MinesPredictorApp()
    app.mainloop()


if __name__ == "__main__":
    main()

