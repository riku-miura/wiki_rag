from typing import Dict, Any

class AppError(Exception):
    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)

def format_error_response(error: Exception) -> Dict[str, Any]:
    """
    Formats an exception into a standard API error response.
    """
    if isinstance(error, AppError):
        return {
            "error": error.message,
            "code": error.code
        }
    return {
        "error": str(error),
        "code": "UNKNOWN_ERROR"
    }
