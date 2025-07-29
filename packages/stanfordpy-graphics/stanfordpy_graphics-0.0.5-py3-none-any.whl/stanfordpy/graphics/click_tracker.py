import tkinter as tk


class ClickTracker:
    """
    Tracks clicks on a canvas and lets you block until the next click.
    """

    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.click_history: list[tuple[float, float]] = []
        # a Tk variable to block/wake on click
        self._click_var = tk.BooleanVar(value=False)

        # bind clicks
        self.canvas.bind("<Button-1>", self._on_click)

    def _on_click(self, event: tk.Event):
        # record the click
        coords = (event.x, event.y)
        self.click_history.append(coords)
        # wake up any waiters
        self._click_var.set(True)

    def get_last_click(self) -> tuple[float, float] | None:
        """Return the most recent click, or None if none yet."""
        return self.click_history[-1] if self.click_history else None

    def get_new_clicks(self) -> list[tuple[float, float]]:
        """
        Return all clicks since the last call, but keep the very last
        one in history so get_last_click() still works.
        """
        new = self.click_history.copy()
        if new:
            # preserve only the last click
            self.click_history = [new[-1]]
        return new

    def wait_for_click(self) -> None:
        """
        Block until the user clicks the canvas, then return the click coords.
        Can be called repeatedly.
        """
        # reset the flag
        self._click_var.set(False)
        # this blocks here but still processes events until the click happens
        self.canvas.wait_variable(self._click_var)
