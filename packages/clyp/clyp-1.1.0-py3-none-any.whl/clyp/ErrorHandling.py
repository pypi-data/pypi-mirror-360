# This is a big to-do, but it can be held off for now
# Python error handling will catch it for now, but they will be really cryptic and likely unhelpful


class ClypError(Exception):
    """Base class for exceptions in Clyp."""

    def __init__(self, message: str, line: int = -1, column: int = -1):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column

    def __str__(self) -> str:
        if self.line != -1:
            return f"Error on line {self.line}: {self.message}"
        return self.message


class ClypSyntaxError(ClypError):
    """Raised for syntax errors in Clyp code."""

    pass


class ClypTypeError(ClypError):
    """Raised for type-related errors in Clyp."""

    pass


class ClypNameError(ClypError):
    """Raised when a name is not found."""

    pass


class ClypRuntimeError(ClypError):
    """Raised for errors during runtime."""

    pass
