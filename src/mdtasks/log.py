from rich.console import Console

console = Console()

def error(msg: str):
    console.print(f"[ERROR] {msg}", style="red")

def warning(msg: str):
    console.print(f"[ WARN ] {msg}", style="yello")

message = console.print
