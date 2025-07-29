import re


# https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
def camel_to_snake(s: str) -> str:
    pattern = re.compile(r"(?<!^)(?=[A-Z0-9])")
    return pattern.sub("_", s).lower()


def snake_to_camel(s: str) -> str:
    words = s.split("_")
    return words[0].lower() + "".join(word.title() for word in words[1:])
