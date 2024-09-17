from typing import List


ANSI_COLORS = {
    'black': '\033[30m',
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'magenta': '\033[35m',
    'cyan': '\033[36m',
    'white': '\033[37m',
    'reset': '\033[0m'
}


def colorize_text(text: str, color: str) -> str:
    color_code = ANSI_COLORS.get(color, ANSI_COLORS['reset'])
    return f"{color_code}{text}{ANSI_COLORS['reset']}"


def bold_text(text):
    return f"\033[1m{text}\033[0m"


def tabulate(data: List[object], *headers: List[str]) -> str:
    assert isinstance(data, list), "Data must be a list"
    assert all(isinstance(header, str) for header in headers), (
        "Data must be a list of objects")

    table = []
    table.append(headers)
    for record in data:
        row = []
        for header in headers:
            row.append(str(getattr(record, header)))
        table.append(row)
    col_widths = [max(len(str(cell)) for cell in col) for col in zip(*table)]
    table[0] = [
        f"{header.title():^{col_widths[i]}}"
        for i, header in enumerate(table[0])
    ]
    table.insert(1, [
        f"{'-' * col_widths[i]}" for i in range(len(table[0]))])
    output = ""
    for row in table:
        output += (" | ".join(
            f"{cell:{col_widths[i]}}" for i, cell in enumerate(row)))
        output += "\n"
    return output


def ljust(value: str, width: int, fillchar: str = " ") -> str:
    return value.ljust(width, fillchar)


def rjust(value: str, width: int, fillchar: str = " ") -> str:
    return value.rjust(width, fillchar)


def center(value: str, width: int, fillchar: str = " ") -> str:
    return value.center(width, fillchar)


def uppercase(value: str) -> str: return value.upper()
def lowercase(value: str) -> str: return value.lower()


def _round(value: float, ndigits: int = None) -> int | float:
    return round(value, ndigits)
