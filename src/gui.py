"""Present an interactive Tkinter window for the shell."""

import tkinter as tk
from tkinter.scrolledtext import ScrolledText

from src.shell import CommandError, Shell
from src.config import Config, parse_config
from src.startup import run_startup
from src.vfs import VFS, VFSError


class ShellWindow:
    """Display a command input and a read-only interaction log."""

    def __init__(self, root: tk.Tk, config: Config):
        """Build the GUI and schedule the configured startup script."""
        self.root = root
        self.config = config
        self.shell = Shell()
        root.title(f"Эмулятор оболочки | VFS: {config.vfs.name}")
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
        self.write("Вариант 13. Этап 3. ls и cd остаются заглушками.")
        self.write("Команды: ls, cd, exit, vfs-info, vfs-read путь.")
        self.write(f"Параметр VFS: {config.vfs}")
        self.write(f"Стартовый скрипт: {config.startup or 'не задан'}")
        root.after_idle(self.load_vfs)

    def load_vfs(self) -> None:
        """Load memory state before executing startup commands."""
        try:
            self.shell.vfs = VFS.load(self.config.vfs)
        except VFSError as error:
            self.write(f"Ошибка VFS: {error}")
            self.write("Стартовый скрипт не запущен. Доступны заглушки и exit.")
            return
        self.write("VFS загружена в память. Исходный ZIP не изменяется.")
        self.write(self.shell.vfs.describe())
        self.start_script()

    def start_script(self) -> None:
        """Execute startup commands after the widgets have been created."""
        if self.config.startup is None:
            return
        if run_startup(self.config.startup, self.shell, self.write):
            self.root.destroy()

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
    config = parse_config()
    root = tk.Tk()
    ShellWindow(root, config)
    root.mainloop()
