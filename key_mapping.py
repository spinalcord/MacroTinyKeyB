class KeyMapper:
    """Handles key code to character mapping and filename conversion."""
    
    # Special key mappings for filename generation
    SPECIAL_KEYS = {
        'KEY_SPACE': 'space',
        'KEY_ENTER': 'enter',
        'KEY_TAB': 'tab',
        'KEY_BACKSPACE': 'backspace',
        'KEY_DELETE': 'delete',
        'KEY_ESC': 'escape',
        'KEY_LEFTSHIFT': 'lshift',
        'KEY_RIGHTSHIFT': 'rshift',
        'KEY_LEFTCTRL': 'lctrl',
        'KEY_RIGHTCTRL': 'rctrl',
        'KEY_LEFTALT': 'lalt',
        'KEY_RIGHTALT': 'ralt',
        'KEY_UP': 'up',
        'KEY_DOWN': 'down',
        'KEY_LEFT': 'left',
        'KEY_RIGHT': 'right',
        **{f'KEY_F{i}': f'f{i}' for i in range(1, 13)}  # F1-F12
    }
    
    @classmethod
    def keycode_to_filename(cls, keycode: str) -> str:
        """Convert keycode to safe filename (alphanumeric only)."""
        if keycode in cls.SPECIAL_KEYS:
            return cls.SPECIAL_KEYS[keycode]
        
        # Normal keys: KEY_A -> a, KEY_1 -> 1, etc.
        if keycode.startswith('KEY_'):
            key_char = keycode[4:].lower()
            if key_char.isalnum():
                return key_char
        
        # Fallback: clean keycode
        return keycode.lower().replace('key_', '')