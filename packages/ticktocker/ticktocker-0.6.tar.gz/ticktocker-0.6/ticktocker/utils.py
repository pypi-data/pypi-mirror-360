from time import time


class TextStyle:
    @staticmethod
    def bold(text: str) -> str:
        return f'\033[1m{text}\033[0m'

    @staticmethod
    def red(text: str) -> str:
        return f'\033[91m{text}\033[0m'

    @staticmethod
    def green(text: str) -> str:
        return f'\033[92m{text}\033[0m'

    @staticmethod
    def yellow(text: str) -> str:
        return f'\033[93m{text}\033[0m'

    @staticmethod
    def blue(text: str) -> str:
        return f'\033[94m{text}\033[0m'

    @staticmethod
    def gray(text: str) -> str:
        return f'\033[90m{text}\033[0m'


def _millis() -> float:
    """
    Returns the current time in milliseconds.
    """
    return time() * 1000
