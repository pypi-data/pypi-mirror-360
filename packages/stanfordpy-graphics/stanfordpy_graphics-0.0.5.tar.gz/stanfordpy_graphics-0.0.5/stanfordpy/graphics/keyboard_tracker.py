import tkinter as tk


class KeyboardTracker:
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.key_history: list[str] = []
        self.canvas.bind("<Key>", self.track_key)

    def track_key(self, event: tk.Event):
        self.key_history.append(event.keysym)

    def get_last_key(self) -> str | None:
        if not self.key_history:
            return None
        return self.key_history[-1]

    def get_new_keys(self) -> list[str]:
        new_keys = self.key_history
        # Remove all but the last key from the history (for use in get_last_key)
        self.key_history = [self.key_history[-1]] if len(self.key_history) >= 1 else []
        return new_keys
