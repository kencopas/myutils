import textwrap
import os
import inspect
import json

from pathlib import Path


# Retrieves an environment variable, logs if it doesn't exist
def gotenv(varname: str):
    envvar = os.getenv(varname)
    if not envvar:
        print(f"Missing required environment variable: {varname}")
    return envvar


def gen_file_structure(output_fp: str, main_fp: str, *, ignores: set = set()) -> dict:
    """Creates a json file that holds the file structure of a project

    This function uses the pathlib python module to traverse a project's
    file structure and construct a json file containing that information,
    including each files contents, as name-contents pairs.

    Args:
        output_fp (str): Filepath to the desired output json file
        ignores (set): Set of extensions and file/folder names to be ignored

    Returns:
        dict: File structure data as a dictionary, optional to use
    """

    # Get current working directory
    cwd = Path(main_fp).resolve().parent

    # Add default ignores to the argument
    ignores = ignores | {'.env', '.pyc', '.exe', 'venv', output_fp}

    # Initialize file structure dict
    file_structure = {
        'project_directory_path': str(cwd),
        'project_directory_name': cwd.name,
        'subdirectories': {}
    }

    # Initialize current node
    node = file_structure['subdirectories']

    # Depth-First Search function for file structure traversal
    def dfs(dir: Path, node: dict):

        # Iterate through subpaths
        for subpath in dir.iterdir():

            if subpath.is_dir() and subpath.name not in ignores:
                # Append directory to deque, create dir_name-subdirs pair
                node[subpath.name] = dict()
                dfs(subpath, node[subpath.name])

            elif subpath.is_file() and subpath.name not in ignores and subpath.suffix not in ignores:
                try:
                    # Create filename-contents pair
                    node[subpath.name] = subpath.read_text()
                except UnicodeDecodeError:
                    node[subpath.name] = "File contents are not decodable."
                    print(f"Failed to decode: {subpath.name}")

    # Perform DFS on the current working directory
    dfs(cwd, node)

    # Write file structure to output json file
    with open(output_fp, 'w') as f:
        f.write('')
        json.dump(file_structure, f, indent=4, sort_keys=True)

    # Also return the file_structure dict
    return file_structure


def printy(msg: str, *encodings: int, end: str = '\n'):
    """Print a message with the specified ANSI values used in encoding"""
    encodings = ';'.join([str(enc) for enc in encodings])
    print(f"\033[{encodings}m{msg}\033[0m", end=end)


def chat_log(log_path: str = 'chat-log.txt', **messages: dict[str, str]):
    """Logs a two-person conversation to console and log-file

    Example:
        chat_log(
            User="Hello!",
            ChatGPT="Hi, how are you?",
            colors=[37, 34]  # ANSI encoding color values
        )

    Output:
        User: Hello!  # In first color
        ChatGPT: Hi, how are you?  # In second color
    """
    colors = messages.pop('colors', [34, 37])
    log_file = open('chat-log.txt', 'a')

    for (role, content), color in zip(messages.items(), colors):

        # Wrap the content for readability
        content = textwrap.fill(content, width=80)
        
        # Print to console (color-coded)
        printy(f'{role}: ', 1, color)
        printy(content, color, end='\n\n')

        # Append to log file
        log_file.write(f'{role}:\n{content}\n\n')

    log_file.close()



def path_log(message: str, err: Exception = None) -> None:
    """
    This function logs a message in the console, but prepends the function name
    as would be referenced statically. Function/method's are logged as follows:

    function_name | message
    class_name.method_name | message
    """

    frame_info = inspect.stack()[1]
    frame = frame_info.frame
    func_name = frame_info.function

    # Try to get class name if 'self' or 'cls' is in local variables
    cls_name = None
    if 'self' in frame.f_locals:
        cls_name = type(frame.f_locals['self']).__name__
    elif 'cls' in frame.f_locals:
        cls_name = frame.f_locals['cls'].__name__

    method_name = f"{cls_name}.{func_name}" if cls_name else func_name

    print(f"{method_name} | {message}")
    if err:
        print(f"{type(err).__name__}: {err}")


def debug(func):
    def wrapper(*args, **kwargs):
        read_kwargs = [f"{key}={val}" for key, val in kwargs.items()]
        print(
            f"\n{func.__name__}({', '.join([str(a) for a in args])},"
            f"{', '.join(read_kwargs)})\n"
        )
        return func(*args, **kwargs)
    return wrapper
