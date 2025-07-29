class Color:
    """
    Allows for tracking color properties of text stored as an array.
    The code property stores the ANSI escape codes color code for the color.
    code=None indicates that the color should be reset
    """

    def __init__(self, code):
        self.code = code

    def ansi_escape_code(self):
        """Gets the ANSI escape code sequence for this color object"""
        if self.code is None:
            return "\x1b[m"
        else:
            return f"\x1b[38;5;{self.code}m"


def log(*message, use_color=True):
    """
    Log the specified messages to the console output.
    Resolves colors specified as Color objects.
    """

    def process_message_chunk(chunk):
        if isinstance(chunk, Color):
            if not use_color: return ""
            return chunk.ansi_escape_code()
        return chunk

    message = ("[", Color(2), "pycopy", Color(None), "] ", *message, Color(None))

    print(*(process_message_chunk(chunk) for chunk in message), sep="")
