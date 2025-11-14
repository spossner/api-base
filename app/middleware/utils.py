class Colors:
    Black = "\u001b[90m"
    Red = "\u001b[91m"
    Green = "\u001b[92m"
    Yellow = "\u001b[93m"
    Blue = "\u001b[94m"
    Magenta = "\u001b[95m"
    Cyan = "\u001b[96m"
    White = "\u001b[97m"
    Reset = "\u001b[0m"


def get_status_color(status_code: int) -> str:
    status_class = status_code // 100
    return {
        2: Colors.Green,
        3: Colors.Blue,
        4: Colors.Yellow,
        5: Colors.Red,
    }.get(status_class, Colors.White)


def get_method_color(method: str) -> str:
    return {
        "GET": Colors.Cyan,
        "POST": Colors.Green,
        "PUT": Colors.Yellow,
        "PATCH": Colors.White,
        "DELETE": Colors.Red,
        "OPTIONS": Colors.Black,
        "HEAD": Colors.Magenta,
    }.get(method.upper(), Colors.White)
