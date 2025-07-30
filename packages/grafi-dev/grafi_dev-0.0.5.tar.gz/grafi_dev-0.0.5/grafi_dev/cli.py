import importlib.util
import logging
import sys
from pathlib import Path

import typer
import uvicorn

from grafi_dev.server import create_app

logger = logging.getLogger(__name__)
app = typer.Typer(add_completion=False)


def _load_assistant(path: Path, assistant_name: str):
    # Ensure we're working with an absolute path
    abs_path = path.absolute().resolve()

    # Save original sys.path
    original_sys_path = sys.path.copy()

    try:
        # current working directory is project root
        project_root = str(Path.cwd())

        script_dir = str(abs_path.parent)

        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        # Now load the module
        spec = importlib.util.spec_from_file_location("user_code", abs_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore

        if not hasattr(mod, assistant_name):
            raise typer.BadParameter(
                f"{path} must define a global variable `{assistant_name}` "
                f"that is an instance of grafi.assistants.Assistant"
            )
        return getattr(mod, assistant_name)
    finally:
        # Restore the original sys.path
        sys.path = original_sys_path


@app.command()
def run(
    script: Path,
    host: str = "127.0.0.1",
    port: int = 8080,
    assistant_name: str = "assistant",
    is_async: bool = True,
    open_browser: bool = True,
):
    """Run the assistant in *script* and launch the web UI."""
    logger.info("Starting server with %s", script)
    assistant = _load_assistant(script, assistant_name)
    logger.info("Assistant loaded: %s", getattr(assistant, "name", assistant))

    if open_browser:
        import threading
        import time
        import webbrowser

        threading.Thread(
            target=lambda: (time.sleep(1), webbrowser.open(f"http://{host}:{port}")),
            daemon=True,
        ).start()

    # Pass the assistant instance directly to create_app
    uvicorn.run(
        lambda: create_app(assistant=assistant, is_async=is_async),  # type: ignore
        factory=True,  # <─ tells Uvicorn to call it
        host=host,
        port=port,
        log_level="info",
    )


# ─── allow `python grafi_dev/cli.py …` without installing ────────────────
if __name__ == "__main__":
    app()  # delegate argv parsing to Typer
