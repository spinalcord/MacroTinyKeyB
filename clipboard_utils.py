import pyperclip

def get_clipboard_content():
    """
    Retrieves the current content of the clipboard.
    """
    try:
        return pyperclip.paste()
    except pyperclip.PyperclipException as e:
        return f"Error getting clipboard content: {e}"

def set_clipboard_content(text: str):
    """
    Sets the content of the clipboard to the given text.
    """
    try:
        pyperclip.copy(text)
        return "Clipboard content set successfully."
    except pyperclip.PyperclipException as e:
        return f"Error setting clipboard content: {e}"

if __name__ == '__main__':
    # Example usage:
    print("Current clipboard content:", get_clipboard_content())
    set_clipboard_content("Hello from Python!")
    print("New clipboard content:", get_clipboard_content())