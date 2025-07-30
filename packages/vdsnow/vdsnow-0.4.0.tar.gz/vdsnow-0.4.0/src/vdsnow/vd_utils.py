import time
from functools import wraps
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def with_spinner(message: str):
    """Decorator to show a spinner while a function runs, then replace with ✅."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                transient=True,  # Clears spinner line after done
                console=console,
            ) as progress:
                task = progress.add_task(description=message, start=False)

                time.sleep(1)  # Simulate delay
                progress.start_task(task)
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator
