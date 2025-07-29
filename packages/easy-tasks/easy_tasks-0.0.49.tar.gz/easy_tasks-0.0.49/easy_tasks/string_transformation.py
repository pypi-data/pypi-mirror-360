from typing import Iterable, List, Union
import inspect
import shutil
import tempfile


def upper_case_first_letter_of_word(String: str, lower_case_words: list = []):
    """Get a string with your string transformed to have the firts letter in upper case.

    Args:
        String (str): Your string to transform. (not in place)
        lower_case_words (list, optional): List of words which should allways be in lower case. Defaults to [].

    Returns:
        string: AThe transformed string.
    """
    wörter = String.split(" ")
    _ws = []
    for w in wörter:
        dw = ""
        for iw, cw in enumerate(w):
            if iw == 0:
                dw += cw.upper()
            else:
                dw += cw
        if w.lower() in [w.lower() for w in lower_case_words]:
            dw = w.lower()
        _ws.append(dw)
    dn = " ".join(_ws)
    return dn


def upper_case_first_letter_of_words(List: list[str], lower_case_words: list = []):
    """Get a list with the strings transformed to have the firts letter in upper case in your list.

    Args:
        Liste (list[str]): Your list of strings to transform. (not in place)
        lower_case_words (list, optional): List of words which should allways be in lower case. Defaults to [].

    Returns:
        list: A list containing the transformed strings.
    """
    result = []
    for n in List:
        dn = upper_case_first_letter_of_word(n, lower_case_words)
        result.append(dn)
    return result


def find_chained_markers(text, markers):
    current_index = -1
    for marker in markers:
        # Search for the marker after the previous one
        current_index = text.find(marker, current_index + 1)
        if current_index == -1:
            return -1  # Chain is broken
    return current_index  # Index of the last marker


def insert_into_string(
    content: str,
    markers: str | list[str],
    insert,
    insert_after: bool = True,
    align_to_line: bool = False,
    offset: int = 0,
    min_lineno: int = 0,
    max_lineno: int = -1,
) -> str | None:
    """
    Inserts string into the content at the position of a chained marker sequence.

    Searches for a sequence of one or more markers appearing in order within the specified
    line range of the file. Once the full chain is found, inserts the provided content either
    before or after the final marker in the chain, with optional adjustments.

    Parameters:
        filepath (str): Path to the file to modify.
        markers (str or list[str]): A single string or list of strings representing the marker
            sequence to match. All markers must be found in order.
        insert (str): The text to insert into the file.
        insert_after (bool): If True, insert after the final marker. If False, insert before it.
        align_to_line (bool): If True, aligns the insertion to the beginning or end of the line containing
            the marker, rather than a character-level offset.
        offset (int): Number of characters to shift the insertion point from the target position.
        min_lineno (int): Minimum line number (0-based, inclusive) to consider when searching for the marker.
        max_lineno (int): Maximum line number (exclusive). Use -1 to search to the end of the file.

    Returns:
        str|None. The new content is returned if successful.
    """

    def get_surrounding_linebreaks(text, index):
        prev_break = text.rfind("\n", 0, index)
        next_break = text.find("\n", index)
        if prev_break == -1:
            prev_break = 0
        if next_break == -1:
            next_break = len(text)
        return prev_break, next_break

    def _insert_before(text, index, insert_text):
        return text[:index] + insert_text + text[index:]

    def _insert_after(text, index, insert_text):
        return text[: index + 1] + insert_text + text[index + 1 :]

    lines = content.splitlines()
    max_lineno = max_lineno if max_lineno != -1 else len(lines)
    relevant = "\n".join(lines[min_lineno:max_lineno])
    pos = 0 if min_lineno == 0 else len("\n".join(lines[:min_lineno]) + "\n")

    if not isinstance(markers, Iterable) or isinstance(markers, str):
        markers = [markers]

    markers = [str(m) for m in markers]
    insert = str(insert)

    if not all(m in relevant for m in markers):
        return  # Exit silently if any marker is missing

    marker_index = find_chained_markers(relevant, markers)
    if marker_index == -1:
        return  # Chain broken

    pos += marker_index

    if align_to_line:
        prev_break, next_break = get_surrounding_linebreaks(content, pos)
        pos = (next_break - 1) if insert_after else (prev_break + 1)

    pos += offset

    new_content = (
        _insert_after(content, pos, insert)
        if insert_after
        else _insert_before(content, pos, insert)
    )

    return new_content


def insert_into_file(
    filepath: str,
    markers: str | list[str],
    insert,
    insert_after: bool = True,
    align_to_line: bool = False,
    offset: int = 0,
    min_lineno: int = 0,
    max_lineno: int = -1,
    backup: bool = True,
):
    """
    Inserts content into a file at the position of a chained marker sequence.

    Searches for a sequence of one or more markers appearing in order within the specified
    line range of the file. Once the full chain is found, inserts the provided content either
    before or after the final marker in the chain, with optional adjustments.

    Parameters:
        filepath (str): Path to the file to modify.
        markers (str or list[str]): A single string or list of strings representing the marker
            sequence to match. All markers must be found in order.
        insert (str): The text to insert into the file.
        insert_after (bool): If True, insert after the final marker. If False, insert before it.
        align_to_line (bool): If True, aligns the insertion to the beginning or end of the line containing
            the marker, rather than a character-level offset.
        offset (int): Number of characters to shift the insertion point from the target position.
        min_lineno (int): Minimum line number (0-based, inclusive) to consider when searching for the marker.
        max_lineno (int): Maximum line number (exclusive). Use -1 to search to the end of the file.
        backup (bool): If True, create a backup copy of the original file as <filename>.bak.

    Returns:
        str|None. The new content is returned if successful. The file is modified in-place if successful.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        raise RuntimeError(f"Failed to read file: {e}")

    new_content = insert_into_string(
        content,
        markers,
        insert,
        insert_after,
        align_to_line,
        offset,
        min_lineno,
        max_lineno,
    )

    if new_content:
        # Optional backup
        if backup:
            backup_path = filepath + ".bak"
            shutil.copy2(filepath, backup_path)

        # Write safely to a temp file and move it into place
        try:
            with tempfile.NamedTemporaryFile(
                "w", delete=False, encoding="utf-8"
            ) as tmp:
                tmp.write(new_content)
                temp_name = tmp.name
            shutil.move(temp_name, filepath)
        except Exception as e:
            raise RuntimeError(
                f"Failed to write safely: {e}\nTemporary file at: {temp_name}"
            )
        return new_content


def replace_in_string(
    content: str,
    markers: Union[str, List[str]],
    replacement: str,
    min_lineno: int = 0,
    max_lineno: int = -1,
    backup: bool = True,
) -> str | None:
    """
    Replaces the final marker in a matched marker chain with new content.

    Searches for a sequence of markers appearing in order (chained) within the specified
    line range. Once found, replaces only the last marker in the chain with the given
    replacement string. All other parts of the file remain unchanged.

    Parameters:
        filepath (str): Path to the file to modify.
        markers (str or list[str]): A single string or list of strings representing the marker
            sequence to match. All markers must be found in order.
        replacement (str): The text that replaces the final marker in the chain.
        min_lineno (int): Minimum line number (0-based, inclusive) to consider when searching for the marker.
        max_lineno (int): Maximum line number (exclusive). Use -1 to search to the end of the file.
        backup (bool): If True, create a backup copy of the original file as <filename>.bak.

    Returns:
        str|None. The new content is returned if successful.
    """
    lines = content.splitlines()
    max_lineno = max_lineno if max_lineno != -1 else len(lines)
    relevant = "\n".join(lines[min_lineno:max_lineno])
    pos = 0 if min_lineno == 0 else len("\n".join(lines[:min_lineno]) + "\n")

    if not isinstance(markers, Iterable) or isinstance(markers, str):
        markers = [markers]

    markers = [str(m) for m in markers]

    if not all(m in relevant for m in markers):
        return  # Exit silently if any marker is missing

    marker_index = find_chained_markers(relevant, markers)
    if marker_index == -1:
        return  # Chain broken

    pos += marker_index

    new_content = content[:pos] + replacement + content[pos + len(markers[-1]) :]

    return new_content


def replace_in_file(
    filepath: str,
    markers: Union[str, List[str]],
    replacement: str,
    min_lineno: int = 0,
    max_lineno: int = -1,
    backup: bool = True,
):
    """
    Replaces the final marker in a matched marker chain with new content.

    Searches for a sequence of markers appearing in order (chained) within the specified
    line range. Once found, replaces only the last marker in the chain with the given
    replacement string. All other parts of the file remain unchanged.

    Parameters:
        filepath (str): Path to the file to modify.
        markers (str or list[str]): A single string or list of strings representing the marker
            sequence to match. All markers must be found in order.
        replacement (str): The text that replaces the final marker in the chain.
        min_lineno (int): Minimum line number (0-based, inclusive) to consider when searching for the marker.
        max_lineno (int): Maximum line number (exclusive). Use -1 to search to the end of the file.
        backup (bool): If True, create a backup copy of the original file as <filename>.bak.

    Returns:
        str|None. The new content is returned if successful. The file is modified in-place if successful.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        raise RuntimeError(f"Failed to read file: {e}")

    new_content = replace_in_string(
        content, markers, replacement, min_lineno, max_lineno
    )

    if new_content:
        # Optional backup
        if backup:
            backup_path = filepath + ".bak"
            shutil.copy2(filepath, backup_path)

        # Write safely to a temp file and move it into place
        try:
            with tempfile.NamedTemporaryFile(
                "w", delete=False, encoding="utf-8"
            ) as tmp:
                tmp.write(new_content)
                temp_name = tmp.name
            shutil.move(temp_name, filepath)
        except Exception as e:
            raise RuntimeError(
                f"Failed to write safely: {e}\nTemporary file at: {temp_name}"
            )
        return new_content


def comment_lines_in_file(
    keyword: str,
    mode: str = "next",
    contains: bool = False,
    action: str = "comment",
    also_includes: Union[str, List[str], None] = None,
    does_not_include: Union[str, List[str], None] = None,
    filepath: str | None = None,
    backup: bool = True,
):
    """
    Adds or removes comments on lines in the current file that contain a specified keyword,
    and optionally match additional conditions (including or excluding other strings).

    Parameters:
    - keyword (str): The main text to search for in the lines.
    - mode (str): "next" to comment/uncomment the next occurrence,
                  "previous" to comment/uncomment the last occurrence before the call,
                  "all_following" to comment/uncomment all occurrences after the current line,
                  or "all" to comment/uncomment all occurrences in the document.
    - contains (bool): If True, matches lines containing the keyword;
                       if False, matches lines that equal the keyword.
    - action (str): "comment" to add comments (default) or "uncomment" to remove comments.
    - also_includes (str or list of str, optional): Additional string(s) that must also be in the line.
    - does_not_include (str or list of str, optional): String(s) that should not be present in the line.
    - filepath (str or None): Either the target filepath or None for the current file.
    - backup (bool): If True, create a backup copy of the original file as <filename>.bak.
    """
    if isinstance(also_includes, str):
        also_includes = [also_includes]
    if isinstance(does_not_include, str):
        does_not_include = [does_not_include]

    frame = inspect.currentframe()
    prev_frame = frame.f_back
    frameinfo = inspect.getframeinfo(prev_frame)
    filename = frameinfo.filename
    call_line_number = frameinfo.lineno

    if filepath:
        filename = filepath

    with open(filename, "r") as f:
        lines = f.readlines()

    modified_lines = lines.copy()

    def match_conditions(line):
        if contains:
            keyword_match = keyword in line
        else:
            keyword_match = keyword == line.strip()

        additional_match = (
            all(s in line for s in also_includes) if also_includes else True
        )
        exclusion_match = (
            all(s not in line for s in does_not_include) if does_not_include else True
        )

        return keyword_match and additional_match and exclusion_match

    if mode == "previous":
        # Search from top up to the call line
        last_match_index = None
        for i in range(call_line_number - 1):
            if match_conditions(lines[i]):
                last_match_index = i

        if last_match_index is not None:
            line = lines[last_match_index]
            leading_ws = len(line) - len(line.lstrip())
            if action == "comment" and not line.strip().startswith("#"):
                modified_lines[last_match_index] = (
                    line[:leading_ws] + "# " + line[leading_ws:]
                )
            elif action == "uncomment" and line.lstrip().startswith("#"):
                modified_lines[last_match_index] = (
                    line[:leading_ws] + line[leading_ws + 2 :]
                )

    else:
        first_match = True
        for i, line in enumerate(lines):
            if i > call_line_number - 1 or mode == "all":
                if match_conditions(line):
                    if mode == "next" and not first_match:
                        continue
                    leading_ws = len(line) - len(line.lstrip())
                    if action == "comment" and not line.strip().startswith("#"):
                        modified_lines[i] = line[:leading_ws] + "# " + line[leading_ws:]
                    elif action == "uncomment" and line.lstrip().startswith("#"):
                        modified_lines[i] = line[:leading_ws] + line[leading_ws + 2 :]
                    first_match = False

    # Optional backup
    if backup:
        backup_path = filename + ".bak"
        shutil.copy2(filename, backup_path)

    # Write safely to a temp file and move it into place
    try:
        with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as tmp:
            tmp.writelines(modified_lines)
            temp_name = tmp.name
        shutil.move(temp_name, filename)
    except Exception as e:
        raise RuntimeError(
            f"Failed to write safely: {e}\nTemporary file at: {temp_name}"
        )


def comment_lines_by_lineno(
    linenos: list,
    relative: bool = False,
    backup: bool = True,
    dry_run: bool = False,
):
    """
    Comments out specific lines in the source file of the calling script.

    This function uses stack inspection to locate the source file and line number
    of the code that called it, then comments out the specified lines in that file.
    Each commented line will retain its original indentation, with a "# " inserted
    after any leading whitespace.

    Args:
        linenos (list[int]): Line numbers to comment. These can be absolute or
            relative to the calling line, depending on the `relative` flag.
        relative (bool, optional): If True, `linenos` are interpreted as offsets
            from the line where this function is called. Defaults to False.
        backup (bool, optional): Whether to create a `.bak` backup of the original
            file before writing changes. Defaults to True.
        dry_run (bool, optional): If True, performs no actual file modification and
            instead returns a dictionary mapping line numbers to their commented versions.
            Useful for previewing changes. Defaults to False.

    Returns:
        dict[int, str] | None: If `dry_run` is True, returns a dictionary mapping
        the target line numbers to their modified (commented) versions.
        Otherwise, returns None.

    Raises:
        RuntimeError: If an error occurs while writing the updated file.

    Notes:
        - This function modifies the file in-place unless `dry_run` is True.
        - Use with caution: modifying the source file of a running script can be
          powerful but also dangerous.
    """
    frame = inspect.currentframe()
    prev_frame = frame.f_back
    frameinfo = inspect.getframeinfo(prev_frame)
    filename = frameinfo.filename
    call_line_number = frameinfo.lineno

    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    modified_lines = lines.copy()

    if relative:
        linenos = [x + call_line_number for x in linenos]

    def comment_preserving_indent(line):
        return re.sub(r"^(\s*)", r"\1# ", line)

    for x in linenos:
        modified_lines[x] = comment_preserving_indent(modified_lines[x])

    new_content = "".join(modified_lines)

    if not dry_run:
        # Optional backup
        if backup:
            backup_path = filename + ".bak"
            shutil.copy2(filename, backup_path)

        # Write safely to a temp file and move it into place
        try:
            with tempfile.NamedTemporaryFile(
                "w", delete=False, encoding="utf-8"
            ) as tmp:
                tmp.write(new_content)
                temp_name = tmp.name
            shutil.move(temp_name, filename)
        except Exception as e:
            raise RuntimeError(
                f"Failed to write safely: {e}\nTemporary file at: {temp_name}"
            )
    else:
        dry = {}
        for x in linenos:
            dry[x] = comment_preserving_indent(modified_lines[x])
        return dry
