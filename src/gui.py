"""Present an interactive Tkinter window for the shell."""

import tkinter as tk
from tkinter.scrolledtext import ScrolledText

from src.shell import CommandError, Shell


VFS_NAME = "demo-vfs.zip"


class ShellWindow:
    """Display a command input and a read-only interaction log."""

    def __init__(self, root: tk.Tk):
        """Build the first-stage GUI with a temporary VFS name."""
        self.root = root
        self.shell = Shell()
        root.title(f"Эмулятор оболочки | VFS: {VFS_NAME}")
        root.geometry("850x520")
        self.output = ScrolledText(root, wrap="word", font=("Consolas", 11))
        self.output.pack(fill="both", expand=True, padx=12, pady=12)
        self.output.configure(state="disabled")
        row = tk.Frame(root)
        row.pack(fill="x", padx=12, pady=(0, 12))
        tk.Label(row, text="shell> ").pack(side="left")
        self.entry = tk.Entry(row, font=("Consolas", 11))
        self.entry.pack(side="left", fill="x", expand=True)
        tk.Button(row, text="Выполнить", command=self.submit).pack(side="right")
        self.entry.bind("<Return>", self.submit)
        self.entry.focus_set()
        self.write("Вариант 13. Этап 1. Команды: ls [путь], cd [путь], exit.")
        self.write("VFS пока не загружена. ls и cd работают как заглушки.")
        self.write("Пример подстановки переменной Windows: ls $USERPROFILE")

    def write(self, text: str) -> None:
        """Append text while keeping the transcript protected from editing."""
        self.output.configure(state="normal")
        self.output.insert("end", text + "\n")
        self.output.configure(state="disabled")
        self.output.see("end")

    def submit(self, _event: tk.Event | None = None) -> None:
        """Echo input, execute it, and report command errors in the window."""
        line = self.entry.get()
        self.entry.delete(0, "end")
        self.write(f"shell> {line}")
        try:
            result = self.shell.execute(line)
        except CommandError as error:
            self.write(f"Ошибка: {error}")
            return
        if result.output:
            self.write(result.output)
        if result.should_exit:
            self.root.destroy()


def main() -> None:
    """Start the graphical command loop."""
    root = tk.Tk()
    ShellWindow(root)
    root.mainloop()
