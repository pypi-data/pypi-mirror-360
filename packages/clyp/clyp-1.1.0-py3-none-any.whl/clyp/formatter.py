import black
from .transpiler import parse_clyp, transpile_to_clyp


def format_clyp_code(clyp_code: str) -> str:
    """
    Formats Clyp code by transpiling to Python, formatting, and transpiling back.

    Args:
        clyp_code: The Clyp code to format.

    Returns:
        The formatted Clyp code.
    """
    # Transpile Clyp to Python
    python_code = parse_clyp(clyp_code)

    # Format the Python code using black
    try:
        formatted_python_code = black.format_str(python_code, mode=black.FileMode())
    except black.NothingChanged:
        formatted_python_code = python_code

    # Transpile the formatted Python back to Clyp
    formatted_clyp_code = transpile_to_clyp(formatted_python_code)

    return formatted_clyp_code
