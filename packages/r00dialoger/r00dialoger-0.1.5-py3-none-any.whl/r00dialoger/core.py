from .helpers.input import input
from .helpers.options import options

POSITION = '+1595+400'


def ask(title: str,
        question: str,
        answer_type: str,
        answer_default: str = None,
        pattern: str = None,
        allow_empty: bool = True,
        allow_cancel: bool = True,
        position=POSITION) -> str:
    return input(title=title, question=question, answer_type=answer_type, answer_default=answer_default,
                 pattern=pattern, allow_empty=allow_empty, allow_cancel=allow_cancel, icon="question",
                 position=position).get_answer()

def askwithanswers(title: str, question: str, choices: list, position=POSITION) -> str:
    return options(title=title, message=question, choices=choices, icon="question", position=position).choice

# noinspection PyDefaultArgument
def confirm(message: str, title: str = '', choices: list = ["Yes", "No"], position=POSITION) -> bool:
    assert len(choices) == 2, "The list of options must contain exactly two options."
    assert isinstance(choices[0], str) and isinstance(choices[1], str), "Options must be strings."
    choice = askwithanswers(title=title, question=message, choices=choices, position=position)
    return choice == choices[0]

def alert(message: str, title: str = '', position=POSITION) -> str:
    return options(title=title, message=message, choices=["OK"], icon="alert", position=position).choice

def info(message: str, title: str = '', position=POSITION) -> str:
    return options(title=title, message=message, choices=["OK"], icon="info", position=position).choice

def error(message: str, title: str = '', position=POSITION) -> str:
    return options(title=title, message=message, choices=["OK"], icon="error", position=position).choice

def success(message: str, title: str = '', position=POSITION) -> str:
    return options(title=title, message=message, choices=["OK"], icon="success", position=position).choice

def msg(message: str, title: str = '', position=POSITION) -> str:
    return options(title=title, message=message, choices=["OK"], icon="info", position=position).choice