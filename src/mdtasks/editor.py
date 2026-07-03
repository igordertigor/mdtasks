import os


def get_editor() -> str:
    editor = os.getenv("EDITOR")
    if editor:
        return editor
    return "vi"
