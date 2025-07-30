import traceback


class ModemPayError(Exception):
    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.name = "ModemPayError"
        self.status_code = status_code
        # Capture the stack trace at the point where the error is raised
        self.stacktrace = traceback.format_stack()

    def __str__(self):
        return f"{self.name}: {self.args[0]} (status_code={self.status_code})"
