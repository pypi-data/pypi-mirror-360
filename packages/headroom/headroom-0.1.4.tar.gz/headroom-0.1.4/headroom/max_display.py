import json
from pygments import highlight
from pygments.lexers import JsonLexer, PythonLexer, BashLexer, get_lexer_by_name
from pygments.formatters import TerminalFormatter
from pygments.util import ClassNotFound

def print_agent_response(text):
    """Formats and prints responses from the Max agent itself."""
    # Using ANSI escape codes for color. \033[96m is cyan, \033[0m resets.
    print(f"\033[96mMax: {text}\033[0m")

def format_output(text, output_type="auto"):
    """
    Formats text output based on its detected type or specified type.
    Requires 'pygments' library.
    """
    try:
        if output_type == "json":
            lexer = JsonLexer()
        elif output_type == "python":
            lexer = PythonLexer()
        elif output_type == "bash":
            lexer = BashLexer()
        elif output_type == "yaml":
            from pygments.lexers.data import YamlLexer
            lexer = YamlLexer()
        elif output_type == "ini":
            from pygments.lexers.configs import IniLexer
            lexer = IniLexer()
        elif output_type == "text":
            lexer = None
        else:
            lexer = get_lexer_by_name(output_type)
    except Exception:
        lexer = None
    if lexer:
        return highlight(text, lexer, TerminalFormatter())
    return text
