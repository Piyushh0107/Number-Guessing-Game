# ============================================================
#       NUMBER GUESSING GAME — Tkinter GUI Application
#       Author  : You
#       Version : 1.0
#       Library : Tkinter (built-in, no installation needed)
# ============================================================

import tkinter as tk
from tkinter import font as tkfont
import random


# ── Constants ────────────────────────────────────────────────
NUMBER_RANGE      = (1, 100)
MAX_ATTEMPTS      = 10

# Colour palette — change these to restyle the whole app
CLR_BG            = "#1E1E2E"   # Dark navy background
CLR_CARD          = "#2A2A3E"   # Slightly lighter card surface
CLR_ACCENT        = "#7C6AF7"   # Purple accent
CLR_ACCENT_HOVER  = "#6254D4"   # Darker purple on hover
CLR_TEXT          = "#CDD6F4"   # Soft white text
CLR_MUTED         = "#6C7086"   # Greyed-out / hint text
CLR_SUCCESS       = "#A6E3A1"   # Green for correct guess
CLR_WARNING       = "#FAB387"   # Orange for Too High / Too Low
CLR_DANGER        = "#F38BA8"   # Red for Game Over
CLR_ENTRY_BG      = "#313244"   # Entry field background
CLR_ENTRY_BORDER  = "#45475A"   # Entry field border colour


# ── Game Logic Functions ──────────────────────────────────────

def generate_secret_number():
    """Return a random integer within the defined NUMBER_RANGE."""
    return random.randint(*NUMBER_RANGE)


def evaluate_guess(guess, secret):
    """
    Compare the player's guess to the secret number.
    Returns: 'low', 'high', or 'correct'
    """
    if guess < secret:
        return "low"
    elif guess > secret:
        return "high"
    return "correct"


def heart_bar(attempts_used, max_attempts):
    """Build a visual attempt bar using emoji hearts."""
    remaining = max_attempts - attempts_used
    return "❤️ " * remaining + "🖤 " * attempts_used


# ── GUI Application Class ─────────────────────────────────────

class NumberGuessingGame:
    """
    Encapsulates the entire Tkinter GUI application.
    All widgets and game-state variables live inside this class,
    keeping the global namespace clean.
    """

    def __init__(self, root):
        """
        Constructor: called once when the app starts.
        Sets up the window, fonts, state, and all widgets.
        """
        self.root = root
        self._configure_window()
        self._define_fonts()
        self._init_game_state()
        self._build_ui()
        self.new_game()   # Start the first round immediately

    # ── Window & Style Setup ──────────────────────────────────

    def _configure_window(self):
        """Configure the root Tk window."""
        self.root.title("🎯 Number Guessing Game")
        self.root.geometry("480x640")
        self.root.resizable(False, False)
        self.root.configure(bg=CLR_BG)
        # Centre the window on screen
        self.root.eval("tk::PlaceWindow . center")

    def _define_fonts(self):
        """Pre-define font objects used across multiple widgets."""
        self.font_title    = tkfont.Font(family="Segoe UI", size=22, weight="bold")
        self.font_subtitle = tkfont.Font(family="Segoe UI", size=11)
        self.font_label    = tkfont.Font(family="Segoe UI", size=12)
        self.font_entry    = tkfont.Font(family="Segoe UI", size=18)
        self.font_button   = tkfont.Font(family="Segoe UI", size=12, weight="bold")
        self.font_feedback = tkfont.Font(family="Segoe UI", size=15, weight="bold")
        self.font_hearts   = tkfont.Font(family="Segoe UI", size=11)
        self.font_history  = tkfont.Font(family="Courier New", size=10)

    # ── Game State ────────────────────────────────────────────

    def _init_game_state(self):
        """Declare all game-state variables (called once at startup)."""
        self.secret_number  = None
        self.attempts_used  = 0
        self.game_active    = False
        self.session_wins   = 0
        self.session_losses = 0
        self.guess_history  = []   # List of (guess, result) tuples

    # ── UI Construction ───────────────────────────────────────

    def _build_ui(self):
        """Create and place every widget in the window."""

        # ── Header ──
        header_frame = tk.Frame(self.root, bg=CLR_BG)
        header_frame.pack(pady=(30, 0))

        tk.Label(
            header_frame, text="🎯 Number Guessing Game",
            font=self.font_title, bg=CLR_BG, fg=CLR_TEXT
        ).pack()

        tk.Label(
            header_frame,
            text=f"Guess a number between {NUMBER_RANGE[0]} and {NUMBER_RANGE[1]}",
            font=self.font_subtitle, bg=CLR_BG, fg=CLR_MUTED
        ).pack(pady=(4, 0))

        # ── Session Score Bar ──
        self.score_var = tk.StringVar()
        tk.Label(
            self.root, textvariable=self.score_var,
            font=self.font_subtitle, bg=CLR_BG, fg=CLR_MUTED
        ).pack(pady=(6, 0))

        # ── Attempt Hearts ──
        self.hearts_var = tk.StringVar()
        tk.Label(
            self.root, textvariable=self.hearts_var,
            font=self.font_hearts, bg=CLR_BG, fg=CLR_TEXT
        ).pack(pady=(18, 0))

        # ── Attempt Counter Label ──
        self.attempt_var = tk.StringVar()
        tk.Label(
            self.root, textvariable=self.attempt_var,
            font=self.font_label, bg=CLR_BG, fg=CLR_MUTED
        ).pack(pady=(2, 0))

        # ── Feedback Message ──
        self.feedback_var = tk.StringVar()
        self.feedback_label = tk.Label(
            self.root, textvariable=self.feedback_var,
            font=self.font_feedback, bg=CLR_BG, fg=CLR_WARNING,
            wraplength=400
        )
        self.feedback_label.pack(pady=(20, 0))

        # ── Entry Field (card-style frame) ──
        entry_card = tk.Frame(
            self.root, bg=CLR_ENTRY_BORDER,
            padx=2, pady=2, relief="flat"
        )
        entry_card.pack(pady=(22, 0), ipadx=2, ipady=2)

        self.guess_entry = tk.Entry(
            entry_card,
            font=self.font_entry,
            width=8,
            justify="center",
            bg=CLR_ENTRY_BG,
            fg=CLR_TEXT,
            insertbackground=CLR_ACCENT,   # cursor colour
            relief="flat",
            bd=10
        )
        self.guess_entry.pack()
        # Pressing Enter submits the guess
        self.guess_entry.bind("<Return>", lambda e: self.submit_guess())

        # ── Error / Validation Message ──
        self.error_var = tk.StringVar()
        tk.Label(
            self.root, textvariable=self.error_var,
            font=self.font_subtitle, bg=CLR_BG, fg=CLR_DANGER
        ).pack(pady=(6, 0))

        # ── Submit Button ──
        self.submit_btn = self._make_button(
            self.root, "Submit Guess", self.submit_guess,
            CLR_ACCENT, CLR_ACCENT_HOVER
        )
        self.submit_btn.pack(pady=(16, 0), ipadx=20, ipady=8)

        # ── Restart Button ──
        self.restart_btn = self._make_button(
            self.root, "🔄  Restart Game", self.new_game,
            "#45475A", "#585B70"
        )
        self.restart_btn.pack(pady=(10, 0), ipadx=20, ipady=6)

        # ── Guess History Box ──
        history_frame = tk.Frame(self.root, bg=CLR_CARD, padx=14, pady=10)
        history_frame.pack(pady=(24, 0), padx=40, fill="x")

        tk.Label(
            history_frame, text="Guess History",
            font=self.font_subtitle, bg=CLR_CARD, fg=CLR_MUTED
        ).pack(anchor="w")

        self.history_var = tk.StringVar()
        tk.Label(
            history_frame, textvariable=self.history_var,
            font=self.font_history, bg=CLR_CARD, fg=CLR_TEXT,
            justify="left", wraplength=380
        ).pack(anchor="w", pady=(4, 0))

    def _make_button(self, parent, text, command, bg, hover_bg):
        """
        Factory helper: create a flat, styled button with hover effect.
        Returns the Button widget.
        """
        btn = tk.Button(
            parent, text=text, command=command,
            font=self.font_button,
            bg=bg, fg=CLR_TEXT,
            activebackground=hover_bg, activeforeground=CLR_TEXT,
            relief="flat", cursor="hand2", bd=0
        )
        # Hover effect: swap background colour on enter/leave
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))
        return btn

    # ── Game Flow Methods ─────────────────────────────────────

    def new_game(self):
        """Reset all state and widgets to start a fresh round."""
        self.secret_number = generate_secret_number()
        self.attempts_used = 0
        self.game_active   = True
        self.guess_history = []

        # Reset dynamic widget content
        self.guess_entry.config(state="normal")
        self.guess_entry.delete(0, tk.END)
        self.guess_entry.focus()

        self.feedback_var.set("Make your first guess!")
        self.feedback_label.config(fg=CLR_ACCENT)
        self.error_var.set("")
        self.history_var.set("No guesses yet.")

        self._refresh_status_widgets()

    def submit_guess(self):
        """
        Called when the player clicks Submit or presses Enter.
        Validates input, evaluates the guess, and updates the UI.
        """
        # Ignore clicks when the game has ended
        if not self.game_active:
            return

        raw = self.guess_entry.get().strip()

        # ── Input Validation ──
        try:
            guess = int(raw)
        except ValueError:
            self.error_var.set("⚠️  Please enter a whole number.")
            self.guess_entry.delete(0, tk.END)
            return

        lo, hi = NUMBER_RANGE
        if not (lo <= guess <= hi):
            self.error_var.set(f"⚠️  Enter a number between {lo} and {hi}.")
            self.guess_entry.delete(0, tk.END)
            return

        # Clear any previous validation error
        self.error_var.set("")

        # ── Evaluate Guess ──
        self.attempts_used += 1
        result = evaluate_guess(guess, self.secret_number)
        self._record_history(guess, result)
        self._refresh_status_widgets()

        # ── Handle Outcomes ──
        if result == "correct":
            self._handle_win()
        elif self.attempts_used >= MAX_ATTEMPTS:
            self._handle_loss()
        else:
            # Give a directional hint
            if result == "low":
                self.feedback_var.set("📉  Too Low!  Go higher.")
            else:
                self.feedback_var.set("📈  Too High!  Go lower.")
            self.feedback_label.config(fg=CLR_WARNING)

        # Clear the entry field for the next guess
        self.guess_entry.delete(0, tk.END)

    def _handle_win(self):
        """Update UI for a correct guess (player wins)."""
        self.session_wins += 1
        self.game_active  = False
        self.guess_entry.config(state="disabled")
        self.feedback_var.set(
            f"🎉  Correct!  The number was {self.secret_number}.\n"
            f"You won in {self.attempts_used} attempt"
            f"{'s' if self.attempts_used > 1 else ''}!"
        )
        self.feedback_label.config(fg=CLR_SUCCESS)
        self._refresh_status_widgets()

    def _handle_loss(self):
        """Update UI when the player exhausts all attempts."""
        self.session_losses += 1
        self.game_active    = False
        self.guess_entry.config(state="disabled")
        self.feedback_var.set(
            f"💀  GAME OVER!\n"
            f"The secret number was {self.secret_number}."
        )
        self.feedback_label.config(fg=CLR_DANGER)
        self._refresh_status_widgets()

    # ── UI Refresh Helpers ────────────────────────────────────

    def _refresh_status_widgets(self):
        """Sync the hearts bar, attempt counter, and score label with current state."""
        self.hearts_var.set(heart_bar(self.attempts_used, MAX_ATTEMPTS))
        self.attempt_var.set(
            f"Attempts used: {self.attempts_used} / {MAX_ATTEMPTS}"
        )
        self.score_var.set(
            f"🏆 Wins: {self.session_wins}   💔 Losses: {self.session_losses}"
        )

    def _record_history(self, guess, result):
        """Append a formatted entry to the guess history log."""
        icons = {"low": "📉", "high": "📈", "correct": "✅"}
        labels = {"low": "Too Low", "high": "Too High", "correct": "Correct!"}
        entry = f"#{self.attempts_used:02d}  {guess:>3}  →  {icons[result]} {labels[result]}"
        self.guess_history.append(entry)
        self.history_var.set("\n".join(self.guess_history))


# ── Entry Point ───────────────────────────────────────────────

def main():
    """Create the Tk root window and launch the application."""
    root = tk.Tk()
    app  = NumberGuessingGame(root)   # Instantiate the game
    root.mainloop()                   # Start the Tkinter event loop


if __name__ == "__main__":
    main()
