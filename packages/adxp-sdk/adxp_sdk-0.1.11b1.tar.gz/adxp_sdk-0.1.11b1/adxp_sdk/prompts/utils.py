import re


def _replace_braces_to_temp(match) -> str:
    token = match.group(0)
    if token == "{{":
        # double opening brace -> escaped version
        return "<dbrace_variable>"
    elif token == "}}":
        # double closing brace -> escaped version
        return "</dbrace_variable>"
    elif token == r"\\{\\{":
        # double opening brace -> escaped version
        return "<dbrace_variable>"
    elif token == r"\\}\\}":
        # double closing brace -> escaped version
        return "</dbrace_variable>"
    elif token == r"\{\{":
        # double opening brace -> escaped version
        return "<dbrace_variable>"
    elif token == r"\}\}":
        # double closing brace -> escaped version
        return "</dbrace_variable>"
    elif token == "{":
        # single opening brace -> <sbrace>
        return "<sbrace_text>"
    elif token == "}":
        # single closing brace -> </sbrace_text>
        return "</sbrace_text>"
    return token


def _replace_temp_to_braces(match) -> str:
    token = match.group(0)
    if token == "<dbrace_variable>":
        return "{"
    elif token == "</dbrace_variable>":
        return "}"
    elif token == "<sbrace_text>":
        return "{{"
    elif token == "</sbrace_text>":
        return "}}"
    return token


def replace_braces_for_prompt(content: str) -> str:
    """Prompt 변수 인식 정책에 따라 brace를 replace 처리를 합니다.
    > Platform
      - double brace : 변수
      - single brace : 문자
    > langchain
      - double brace : 문자
      - single brace : 변수
    Platform / langchain 변수 인식 정책 차이로 인해 single brace -> double brace로, double brace -> single brace로 변경해야합니다.
    """
    first_pattern = r"(\{\{|\}\}|\{|\})"
    first_replacement = re.sub(first_pattern, _replace_braces_to_temp, content)

    second_pattern = (
        r"(<dbrace_variable>|</dbrace_variable>|<sbrace_text>|</sbrace_text>)"
    )
    return re.sub(second_pattern, _replace_temp_to_braces, first_replacement)
