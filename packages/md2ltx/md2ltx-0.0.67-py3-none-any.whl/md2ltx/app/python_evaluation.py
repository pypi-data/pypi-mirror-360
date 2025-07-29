import re
import math
import os
import pandas as pd
import numpy as np
import rgwfuncs
import typing
from datetime import datetime, timedelta


def evaluate_python_in_markdown_string(markdown_content: str) -> str:
    """
    1) Search for [START] ... [END] code blocks.
    2) Concatenate them into a single big string.
    3) Remove exactly 4 leading spaces (if present) from each line (to fix "one-level" indentation).
    4) Execute in a shared environment (so any function can appear in any block).
    5) Replace placeholders `EMBED::func_name` in the Markdown with the result of calling func_name().
    """

    # Helper: Convert a pandas.DataFrame to Markdown pipe table
    def dataframe_to_pandoc_pipe(df: pd.DataFrame) -> str:
        header = "| " + " | ".join(df.columns) + " |"
        separator = "|" + "|".join("---" for _ in df.columns) + "|"

        def row_to_pipe(row_values):
            return "| " + " | ".join(str(x) for x in row_values) + " |"

        if len(df) <= 10:
            rows = [row_to_pipe(df.iloc[i]) for i in range(len(df))]
            return "\n".join([header, separator] + rows)
        else:
            head_data = df.head(5)
            tail_data = df.tail(5)
            head_rows = [row_to_pipe(head_data.iloc[i]) for i in range(len(head_data))]
            tail_rows = [row_to_pipe(tail_data.iloc[i]) for i in range(len(tail_data))]
            ellipsis_row = "| " + " | ".join("..." for _ in df.columns) + " |"
            return "\n".join([header, separator] + head_rows + [ellipsis_row] + tail_rows)

    # Replace placeholders like `EMBED::func_name`
    def embed_replacer(match: re.Match) -> str:
        fn_name = match.group(1)
        if fn_name not in defined_functions:
            return f"[Error: No function named '{fn_name}' has been defined in the code blocks]"
        try:
            result_val = defined_functions[fn_name]()
            # If the result is a DataFrame, convert it to a Markdown pipe table
            if isinstance(result_val, pd.DataFrame):
                row_count, column_count = result_val.shape
                # column_names = list(result_val.columns)
                column_names = ", ".join(f"*{col}*" for col in result_val.columns)
                md_table = dataframe_to_pandoc_pipe(result_val)
                return (
                    f"Dataframe (dimensions: {row_count} × {column_count}), "
                    f"with columns: {column_names}\n\n{md_table}"
                )
            else:
                return str(result_val)
        except Exception as e:
            return f"[Error calling '{fn_name}': {e}]"

    # Remove exactly 4 leading spaces from each line
    def remove_4_spaces(line: str) -> str:
        if len(line) >= 4 and line[:4] == "    ":
            return line[4:]
        else:
            return line.lstrip()

    # Later used to look up and call user-defined functions
    defined_functions = {}

    # Regex: capture all blocks between [START] and [END]
    import_pattern = re.compile(r"\[START\]#{3,}\s*(.*?)\s*\[END\]#{3,}", re.DOTALL)
    found_blocks = import_pattern.findall(markdown_content)

    # Combine all code from all blocks
    combined_code = "\n".join(found_blocks)

    processed_lines = [remove_4_spaces(ln) for ln in combined_code.splitlines()]
    final_code = "\n".join(processed_lines)

    # Provide a minimal environment so all imports have to appear within the code blocks themselves
    env = {"__builtins__": __builtins__}

    # Execute the combined code in a shared environment
    try:
        exec(final_code, env, env)
    except Exception as exc:
        print("############ PRINTING CODE BLOCK TO HELP YOU DIAGNOSE LINE-SPECIFIC ERROR ###############\n\n", final_code)
        print(f"[Error executing combined code: {exc}]")

    # Gather any callable objects that were defined by the user’s code blocks
    defined_functions = {k: v for k, v in env.items() if callable(v)}

    # Remove code blocks from the final Markdown
    content_no_blocks = import_pattern.sub("", markdown_content)

    # Replace placeholders `EMBED::func_name` with the function's result
    placeholder_pattern = re.compile(r"`EMBED::(\w+)`")
    final_content = placeholder_pattern.sub(embed_replacer, content_no_blocks)

    return final_content
