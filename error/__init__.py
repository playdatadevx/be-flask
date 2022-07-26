
def error_message(code):
    message = {
        "400": "Bad Request",
        "401": "Unauthorized",
        "404": "Page not found",
        "405": "Validation exception"
    }.get(code, "Unexpected Error")
    return message


class Error:
    def __init__(self, code):
        self.code = code
        self.message = error_message(code)
