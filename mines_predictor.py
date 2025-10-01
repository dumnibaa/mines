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

        # Control buttons
        self.control_frame = ctk.CTkFrame(self, corner_radius=15)
        self.control_frame.pack(pady=20)

        self.predict_btn = ctk.CTkButton(
            self.control_frame,
            text="🔮 Predict Next Board",
            font=("Arial Rounded MT Bold", 18),
            fg_color=("#00adb5", "#007f88"),
            hover_color=("#00ced1", "#0097a7"),
            corner_radius=12,
            command=self.reset_board,
        )
        self.predict_btn.pack(side="left", padx=20, pady=10)

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
        # Simple random guess placeholder
        return "mine" if random.random() < 0.12 else "gem"

    # -------------------------------
    # Reset Board
    # -------------------------------
    def reset_board(self) -> None:
        for row_buttons in self.buttons:
            for btn in row_buttons:
                btn.configure(text="🟦", fg_color=("#222831", "#1a1a1a"), text_color="white")

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

