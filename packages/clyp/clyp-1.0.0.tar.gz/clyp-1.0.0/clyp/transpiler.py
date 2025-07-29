# Here we do the transpilation of the Clyp code to Python code!!!!! :3
# Cool right? Well actually it is not that cool, but it's a start

import os
import sys
import pathlib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import re
import typeguard
from typing import List, Optional, Match
import inspect
import clyp.stdlib as stdlib
from clyp.ErrorHandling import ClypSyntaxError


def _process_pipeline_chain(chain: str) -> str:
    parts = [p.strip() for p in chain.split("|>") if p.strip()]
    if len(parts) < 2:
        return chain

    result = parts[0]
    for part in parts[1:]:
        if not part:
            continue
        if "(" in part and part.endswith(")"):
            open_paren_index = part.find("(")
            func_name = part[:open_paren_index].strip()
            args = part[open_paren_index + 1 : -1].strip()
            if args:
                result = f"{func_name}({result}, {args})"
            else:
                result = f"{func_name}({result})"
        else:
            func_name = part.strip()
            result = f"{func_name}({result})"
    return result


def _process_pipeline_operator(line: str) -> str:
    if "|>" not in line:
        return line

    # This does not handle strings with '|>' correctly, but is consistent with the rest of the transpiler.
    assignment_match = re.match(r"(.*\s*=\s*)(.*)", line)
    if assignment_match:
        lhs = assignment_match.group(1)
        rhs = assignment_match.group(2)
        transformed_rhs = _process_pipeline_chain(rhs)
        return lhs + transformed_rhs
    else:
        return _process_pipeline_chain(line)


def _replace_keywords_outside_strings(line: str) -> str:
    """
    Replaces specific Clyp keywords with Python equivalents outside of string literals in a line of code.

    Replaces 'unless' with 'if not', 'is not' with '!=', and 'is' with '==' only in code segments, leaving string literals unchanged.

    Parameters:
        line (str): The input line of code to process.

    Returns:
        str: The line with Clyp keywords replaced outside of strings.
    """
    parts = re.split(r'(".*?"|\'.*?\')', line)
    for i in range(0, len(parts), 2):
        part = parts[i]
        part = re.sub(r"\bunless\b", "if not", part)
        part = re.sub(r"\bis not\b", "!=", part)
        part = re.sub(r"\bis\b", "==", part)
        parts[i] = part
    return "".join(parts)


def _resolve_clyp_module_path(
    module_name: str, base_dir: pathlib.Path, script_path: Optional[str] = None
) -> Optional[pathlib.Path]:
    """
    Resolves a dotted Clyp module name to a valid `.clyp` file or package `__init__.clyp` within the specified base directory or clypPackages folder.

    Attempts to locate the module as either a single `.clyp` file or as a package directory containing an `__init__.clyp` file, verifying that all parent directories up to the base directory are valid Clyp packages.
    Also supports a `clypPackages` folder next to the script or wheel install location.

    Parameters:
        module_name (str): The dotted name of the Clyp module to resolve.
        base_dir (pathlib.Path): The base directory from which to resolve the module path.
        script_path (Optional[str]): The path to the current script (for clypPackages lookup).

    Returns:
        Optional[pathlib.Path]: The resolved path to the `.clyp` file or package `__init__.clyp` if found and valid, otherwise `None`.
    """
    search_dirs = [base_dir]
    # Add clypPackages next to the script, if available
    if script_path:
        script_dir = pathlib.Path(script_path).parent
        clyp_packages_dir = script_dir / "clypPackages"
        if clyp_packages_dir.exists() and clyp_packages_dir.is_dir():
            search_dirs.insert(0, clyp_packages_dir)
    # Add clypPackages next to the installed wheel, if available
    try:
        import clyp

        wheel_dir = pathlib.Path(clyp.__file__).parent.parent
        wheel_clyp_packages = wheel_dir / "clypPackages"
        if wheel_clyp_packages.exists() and wheel_clyp_packages.is_dir():
            search_dirs.append(wheel_clyp_packages)
    except Exception:
        pass
    for search_dir in search_dirs:
        # Try as a single file
        candidate = search_dir / (module_name.replace(".", os.sep) + ".clyp")
        if candidate.exists():
            return candidate
        # Try as a package (__init__.clyp)
        pkg_dir = search_dir / module_name.replace(".", os.sep)
        init_file = pkg_dir / "__init__.clyp"
        if init_file.exists():
            # Check all parent folders up to search_dir have __init__.clyp
            parts = module_name.split(".")
            check_dir = search_dir
            for part in parts:
                check_dir = check_dir / part
                if not (check_dir / "__init__.clyp").exists():
                    break
            else:
                return init_file
    return None


@typeguard.typechecked
def parse_clyp(clyp_code: str, file_path: Optional[str] = None, return_line_map: bool = False):
    """
    Transpiles Clyp source code into equivalent Python code.

    This function parses Clyp language syntax, handling constructs such as imports, type annotations, function definitions, pipeline operators, control flow, and indentation. It validates Clyp import statements, enforces correct usage of reserved Python keywords, and ensures syntactic correctness by transforming Clyp-specific features into valid Python code. Errors are raised for invalid imports, reserved keyword assignments, or malformed function definitions.

    Parameters:
        clyp_code (str): The source code written in the Clyp language to be transpiled.
        file_path (Optional[str]): The file path of the Clyp source, used for resolving relative imports.

    Returns:
        str: The transpiled Python code as a string.
    """
    python_keywords = set(
        [
            "False",
            "None",
            "True",
            "and",
            "as",
            "assert",
            "async",
            "await",
            "break",
            "class",
            "continue",
            "def",
            "del",
            "elif",
            "else",
            "except",
            "finally",
            "for",
            "from",
            "global",
            "if",
            "import",
            "in",
            "is",
            "lambda",
            "nonlocal",
            "not",
            "or",
            "pass",
            "raise",
            "return",
            "try",
            "while",
            "with",
            "yield",
            # Built-in types
            "int",
            "float",
            "str",
            "list",
            "dict",
            "set",
            "tuple",
            "bool",
            "object",
            "bytes",
            "complex",
            "type",
            # Other built-ins
            "print",
            "input",
            "len",
            "open",
            "range",
            "map",
            "filter",
            "zip",
            "min",
            "max",
            "sum",
            "any",
            "all",
            "abs",
        ]
    )
    indentation_level: int = 0
    indentation_sign: str = "    "
    stdlib_names = [
        name
        for name, member in inspect.getmembers(stdlib)
        if not name.startswith("_")
        and (inspect.isfunction(member) or inspect.isclass(member))
        and member.__module__ == stdlib.__name__
    ]
    python_code: str = (
        "from typeguard import install_import_hook; install_import_hook()\n"
        "import clyp\n"
        "from clyp.importer import clyp_import, clyp_include\n"
        f"from clyp.stdlib import {', '.join(stdlib_names)}\n"
        "del clyp\n"
        "true = True; false = False; null = None\n"
    )

    processed_code: List[str] = []
    in_string: bool = False
    string_char: Optional[str] = None
    in_comment: bool = False
    escape_next: bool = False

    char: str
    for char in clyp_code:
        if escape_next:
            processed_code.append(char)
            escape_next = False
            continue

        if char == "\\":
            processed_code.append(char)
            escape_next = True
            continue

        if in_comment:
            processed_code.append(char)
            if char == "\n":
                in_comment = False
            continue

        if in_string:
            processed_code.append(char)
            if char == string_char:
                in_string = False
            continue

        # Not in string, not in comment
        if char in ('"', "'''"):
            in_string = True
            string_char = char
            processed_code.append(char)
        elif char == "#":
            in_comment = True
            processed_code.append(char)
        elif char == ";":
            processed_code.append("\n")
        elif char == "{":
            processed_code.append("{\n")
        elif char == "}":
            processed_code.append("}\n")
        else:
            processed_code.append(char)

    infile_str_raw: str = "".join(processed_code)

    # Handle clyp imports
    processed_import_lines = []
    for line in infile_str_raw.split("\n"):
        stripped_line = line.strip()
        if stripped_line.startswith("clyp import "):
            parts = stripped_line.split()
            if len(parts) == 3:
                module_name = parts[2]
                module_path = None
                if file_path:
                    base_dir = pathlib.Path(file_path).parent
                    module_path = _resolve_clyp_module_path(module_name, base_dir, file_path)
                if module_path is not None:
                    processed_import_lines.append(
                        f"{module_name} = clyp_import('{module_name}', {repr(file_path)})"
                    )
                else:
                    raise ClypSyntaxError(
                        f"Cannot import module '{module_name}': not a Clyp package or single-file script."
                    )
            else:
                raise ClypSyntaxError(f"Invalid clyp import statement: {stripped_line}")
        elif stripped_line.startswith("clyp from "):
            match = re.match(r"clyp from\s+([\w\.]+)\s+import\s+(.*)", stripped_line)
            if match:
                module_name, imports_str = match.groups()
                imported_names = [name.strip() for name in imports_str.split(",")]
                module_path = None
                if file_path:
                    base_dir = pathlib.Path(file_path).parent
                    module_path = _resolve_clyp_module_path(module_name, base_dir, file_path)
                if module_path is not None:
                    processed_import_lines.append(
                        f"_temp_module = clyp_import('{module_name}', {repr(file_path)})"
                    )
                    for name in imported_names:
                        processed_import_lines.append(f"{name} = _temp_module.{name}")
                    processed_import_lines.append("del _temp_module")
                else:
                    raise ClypSyntaxError(
                        f"Cannot import module '{module_name}': not a Clyp package or single-file script."
                    )
            else:
                raise ClypSyntaxError(
                    f"Invalid clyp from import statement: {stripped_line}"
                )
        elif stripped_line.startswith("include "):
            match = re.match(r'include\s+"([^"]+\.clb)"', stripped_line)
            if match:
                clb_path = match.group(1)
                processed_import_lines.append(f'clyp_include(r"{clb_path}", r"{file_path}")')
            else:
                raise ClypSyntaxError(f"Invalid include statement: {stripped_line}")
        else:
            processed_import_lines.append(line)
    infile_str_raw = "\n".join(processed_import_lines)

    # Automatically insert 'pass' into empty blocks
    infile_str_raw = re.sub(r"{(\s|#[^\n]*)*}", "{\n    pass\n}", infile_str_raw)

    infile_str_indented: str = ""
    line_map = {}  # python line number (1-based) -> clyp line number (1-based)
    clyp_lines = clyp_code.splitlines()
    # Check for missing semicolons at the end of statements
    # for idx, line in enumerate(clyp_lines):
    #     stripped = line.strip()
    #     # Ignore empty lines, comments, block starts/ends, and import lines
    #     # Skip empty lines, comments, block delimiters, and import statements
    #     is_empty_or_comment = not stripped or stripped.startswith('#')
    #     is_block_delimiter = stripped.endswith('{') or stripped == '}'
    #     is_import_statement = stripped.startswith('clyp import') or stripped.startswith('clyp from')
    #     
    #     if is_empty_or_comment or is_block_delimiter or is_import_statement:
    #         continue
    #     # Ignore lines that are only whitespace or block headers
    #     if re.match(r'^(def |function |if |elif |for |while |class |try|except|finally|with|repeat )', stripped) or stripped in ('else:', 'finally:'):
    #         continue
    #     # If the line is not a block header and does not end with a semicolon, raise error
    #     if not stripped.endswith(';'):
    #         raise ClypSyntaxError(f"Missing semicolon at end of statement on line {idx+1}: {line}")
    py_line_num = python_code.count('\n') + 1  # start after header
    for idx, line in enumerate(infile_str_raw.split("\n")):
        clyp_line_num = idx + 1

        line = _process_pipeline_operator(line)
        m: Optional[Match[str]] = re.search(r"[ \t]*(#.*$)", line)

        if m is not None:
            m2: Optional[Match[str]] = re.search(r'["\'].*#.*["\']', m.group(0))
            if m2 is not None:
                m = None

        if m is not None:
            add_comment: str = m.group(0)
            line = re.sub(r"[ \t]*(#.*$)", "", line)
        else:
            add_comment: str = ""

        if not line.strip():
            infile_str_indented += (
                indentation_level * indentation_sign + add_comment.lstrip() + "\n"
            )
            continue

        stripped_line = line.strip()

        if stripped_line.startswith("let "):
            line = re.sub(r"^\s*let\s+", "", line)
            stripped_line = line.strip()

        keywords = (
            "def ",
            "function ",
            "if ",
            "for ",
            "while ",
            "class ",
            "return ",
            "elif ",
            "else",
            "{",
            "}",
            "print",
            "repeat ",
        )
        if stripped_line.startswith("except"):
            match = re.match(r"except\s*\((.*)\)", stripped_line)
            if match:
                content = match.group(1).strip()
                parts = content.split()
                if len(parts) == 2:
                    exc_type, exc_var = parts
                    line = re.sub(
                        r"except\s*\(.*\)", f"except {exc_type} as {exc_var}", line
                    )
                elif len(parts) == 1:
                    exc_type = parts[0]
                    line = re.sub(r"except\s*\(.*\)", f"except {exc_type}", line)
                stripped_line = line.strip()
        elif not stripped_line.startswith(keywords):
            # Use a regex that captures an optional type, a name, and the rest of the line
            match = re.match(
                r"^\s*(?:([a-zA-Z_][\w\.\[\]]*)\s+)?([a-zA-Z_]\w*)\s*=(.*)", line
            )
            if match:
                var_type, var_name, rest_of_line = match.groups()
                # Check for reserved keyword assignment
                if var_name in python_keywords:
                    raise ClypSyntaxError(
                        f"Cannot assign to reserved keyword or built-in name: '{var_name}'"
                    )
                if var_type:
                    # Reconstruct the line in Python's type-hint format
                    line = f"{var_name.strip()}: {var_type.strip()} = {rest_of_line.strip()}"
                else:
                    # It's a regular variable assignment
                    line = f"{var_name.strip()} = {rest_of_line.strip()}"
                stripped_line = line
            else:
                # Handle declarations without assignment (e.g., in classes)
                match_decl = re.match(
                    r"^\s*([a-zA-Z_][\w\.\[\]]*)\s+([a-zA-Z_]\w*)\s*$", line
                )
                if match_decl:
                    var_type, var_name = match_decl.groups()
                    line = f"{var_name.strip()}: {var_type.strip()}"
                    stripped_line = line

        if stripped_line.startswith("def ") or stripped_line.startswith("function "):
            if stripped_line.startswith("function "):
                line = line.replace("function", "def", 1)
                stripped_line = line.strip()

            return_type_match = re.search(
                r"returns\s+([a-zA-Z_][\w\.\[\]]*)", stripped_line
            )
            if not return_type_match:
                raise ClypSyntaxError(
                    f"Function definition requires a 'returns' clause. Found in line: {stripped_line}"
                )

            return_type = return_type_match.group(1)
            line = re.sub(r"\s*returns\s+([a-zA-Z_][\w\.\[\]]*)", "", line)
            stripped_line = line.strip()

            args_match = re.search(r"\(([^)]*)\)", stripped_line)
            if args_match:
                original_args_str = args_match.group(1)
                args_str = original_args_str.strip()

                if args_str:
                    args = [arg.strip() for arg in args_str.split(",")]
                    new_args = []
                    for arg in args:
                        if not arg:
                            continue
                        if arg == "self" or arg.startswith("*"):
                            new_args.append(arg)
                            continue

                        parts = arg.strip().split()
                        if len(parts) >= 2:
                            arg_type = parts[0]
                            arg_name = parts[1]
                            default_value = " ".join(parts[2:])
                            new_arg_str = f"{arg_name}: {arg_type}"
                            if default_value:
                                new_arg_str += f" {default_value}"
                            new_args.append(new_arg_str)
                        else:
                            raise ClypSyntaxError(
                                f"Argument '{arg}' in function definition must be in 'type name' format. Found in line: {stripped_line}"
                            )

                    new_args_str = ", ".join(new_args)
                    line = line.replace(original_args_str, new_args_str)
                    stripped_line = line.strip()

            if "{" in line:
                line_before_brace, line_after_brace = line.rsplit("{", 1)
                line = f"{line_before_brace.rstrip()} -> {return_type} {{{line_after_brace}"
            else:
                line = line.strip() + f" -> {return_type}"
                stripped_line = line.strip()

        if stripped_line.startswith("repeat "):
            line = re.sub(r"repeat\s+\[(.*)\]\s+times", r"for _ in range(\1)", line)
            stripped_line = line.strip()

        line = re.sub(r"\brange\s+(\S+)\s+to\s+(\S+)", r"range(\1, \2 + 1)", line)

        line = _replace_keywords_outside_strings(line)

        line = line.lstrip()

        line_to_indent = line
        if line.startswith("}"):
            indentation_level -= 1
            line_to_indent = line.lstrip("}").lstrip()

        indented_line = (indentation_level * indentation_sign) + line_to_indent

        if indented_line.rstrip().endswith("{"):
            indentation_level += 1
            line = indented_line.rsplit("{", 1)[0].rstrip() + ":"
        else:
            line = indented_line

        infile_str_indented += line + add_comment + "\n"
        line_map[py_line_num] = clyp_line_num
        py_line_num += 1

    infile_str_indented = re.sub(r"else\s+if", "elif", infile_str_indented)
    infile_str_indented = re.sub(r";\n", "\n", infile_str_indented)

    python_code += infile_str_indented
    if return_line_map:
        return python_code, line_map, clyp_lines
    return python_code
