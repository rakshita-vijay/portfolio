import os
import sys
import time
import subprocess

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(BASE_DIR, "index.html")
SCRIPT_FILE = os.path.join(BASE_DIR, "instant-resume-maker.py")


class HTMLChangeHandler(FileSystemEventHandler):

    def __init__(self):
        self.last_run = 0

    def on_modified(self, event):
        if os.path.abspath(event.src_path) != HTML_FILE:
            return

        # Prevent multiple triggers from a single save
        now = time.time()
        if now - self.last_run < 1:
            return

        self.last_run = now

        print("index.html changed — regenerating PDF...")

        env = os.environ.copy()

        # Make pdflatex available even when launched outside the terminal
        env["PATH"] = (
            "/usr/local/texlive/2026basic/bin/universal-darwin:"
            "/Library/TeX/texbin:"
            "/opt/homebrew/bin:"
            "/usr/local/bin:"
            + env.get("PATH", "")
        )

        result = subprocess.run(
            [sys.executable, SCRIPT_FILE],
            cwd=BASE_DIR,
            env=env
        )

        if result.returncode == 0:
            print("PDF regenerated successfully.")
        else:
            print(
                f"PDF generation failed "
                f"(exit code {result.returncode})."
            )


if __name__ == "__main__":

    event_handler = HTMLChangeHandler()

    observer = Observer()
    observer.schedule(
        event_handler,
        BASE_DIR,
        recursive=False
    )

    observer.start()

    print("Watching index.html...")

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        observer.stop()

    observer.join()
