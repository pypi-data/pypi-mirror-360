# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2023-10-01 14:47:47
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Standard output methods.
"""


from typing import Any, Literal, Final, Self
from collections.abc import Callable
import sys
from io import TextIOWrapper
from os import devnull as os_devnull
from os.path import abspath as os_abspath

from .rsystem import get_first_notnull, get_name, get_stack_param
from .rtext import to_text, add_text_frame
from .rtype import RConfigMeta


__all__ = (
    'RConfigStdout',
    'beautify_text',
    'echo',
    'rinput',
    'stop_print',
    'start_print',
    'modify_print',
    'reset_print',
    'add_print_position'
)


class RConfigStdout(object, metaclass=RConfigMeta):
    """
    Rey's `config standard output` type.

    Attributes
    ----------
        is_frame_plain : Whehter global use plain text frame type.
            - `Literal[True]`: 'full' to 'half_plain', 'half' to 'half_plain', 'top' to 'top_plain', Other unchanged.
        default_width : Global default text width.
    """

    # Module path.
    _path_rstdout: Final[str] = os_abspath(__file__)

    # Status.
    _stoped: bool = False
    _modified: bool = False

    # IO.
    _io_null: TextIOWrapper = open(os_devnull, 'w')
    _io_stdout: TextIOWrapper = sys.stdout
    _io_stdout_write: Callable[[str], int] = sys.stdout.write

    # Is the print frame plain.
    is_frame_plain: bool = False

    # print default width.
    default_width: int = 100


def beautify_text(
    data: tuple[Any],
    title: bool | str = True,
    width: int | None = None,
    frame: Literal['full', 'half', 'top', 'half_plain', 'top_plain'] | None = 'full'
) -> str:
    """
    Beautify data to text.

    Parameters
    ----------
    data : Text data.
    title : Text title.
        - `Literal[True]`: Automatic get data variable name.
        - `Literal[False]`: No title.
        - `str`: Use this value as the title.
    width : Text width.
        - `None`: Use attribute `RConfigStdout.default_width`.
        - `int`: Use this value.
    frame : Text frame type.
        - `Literal['full']`: Add beautiful four side frame and limit length.
            When attribute `RConfigStdout.is_frame_plain` is True, then frame is `half_plain` type.
            When throw `exception`, then frame is `half` type.
        - `Literal['half']`: Add beautiful top and bottom side frame.
            When attribute `RConfigStdout.is_frame_plain` is True, then frame is `half_plain` type.
        - `Literal['top']`: Add beautiful top side frame.
            When attribute `RConfigStdout.is_frame_plain` is True, then frame is `top_plain` type.
        - `Literal['half_plain']`: Add plain top and bottom side frame.
        - `Literal['top_plain']`: Add plain top side frame.

    Returns
    -------
    Beautify text.
    """

    # Get parameter.

    ## Title.
    if title is True:
        titles = get_name(data, 3)
        if titles is not None:
            titles = [title if not title.startswith('`') else '' for title in titles]
            if set(titles) != {''}:
                title = ' │ '.join(titles)
    if title.__class__ != str:
        title = None

    ## Width.
    width = get_first_notnull(width, RConfigStdout.default_width, default='exception')

    ## Frame.
    if RConfigStdout.is_frame_plain:
        match frame:
            case 'full':
                frame = 'half_plain'
            case 'half':
                frame = 'half_plain'
            case 'top':
                frame = 'top_plain'

    # To text.
    text_list = [
        to_text(content, width=width)
        for content in data
    ]

    # Add frame.
    text = add_text_frame(*text_list, title=title, width=width, frame=frame)

    return text


def echo(
    *data: Any,
    title: bool | str = True,
    width: int | None = None,
    frame: Literal['full', 'half', 'top', 'half_plain', 'top_plain'] | None = 'full'
) -> str:
    """
    Beautify data to text, and print.

    Parameters
    ----------
    data : Text data.
    title : Text title.
        - `Literal[True]`: Automatic get data variable name.
        - `Literal[False]`: No title.
        - `str`: Use this value as the title.
    width : Text width.
        - `None`: Use attribute `RConfigStdout.default_width`.
        - `int`: Use this value.
    frame : Text frame type.
        - `Literal['full']`: Add beautiful four side frame and limit length.
            When attribute `RConfigStdout.is_frame_plain` is True, then frame is `half_plain` type.
            When throw `exception`, then frame is `half` type.
        - `Literal['half']`: Add beautiful top and bottom side frame.
            When attribute `RConfigStdout.is_frame_plain` is True, then frame is `half_plain` type.
        - `Literal['top']`: Add beautiful top side frame.
            When attribute `RConfigStdout.is_frame_plain` is True, then frame is `top_plain` type.
        - `Literal['half_plain']`: Add plain top and bottom side frame.
        - `Literal['top_plain']`: Add plain top side frame.

    Returns
    -------
    Beautify text.
    """

    # Beautify.
    text = beautify_text(data, title=title, width=width, frame=frame)

    # Print.
    print(text)

    return text


def rinput(
    *data: Any,
    title: bool | str = True,
    width: int | None = None,
    frame: Literal['full', 'half', 'top', 'half_plain', 'top_plain'] | None = 'full',
    extra: str | None = None
) -> str:
    """
    Beautify data to text, and print data, and read string from standard input.

    Parameters
    ----------
    data : Text data.
    title : Text title.
        - `Literal[True]`: Automatic get data variable name.
        - `Literal[False]`: No title.
        - `str`: Use this value as the title.
    width : Text width.
        - `None`: Use attribute `RConfigStdout.default_width`.
        - `int`: Use this value.
    frame : Text frame type.
        - `Literal['full']`: Add beautiful four side frame and limit length.
            When attribute `RConfigStdout.is_frame_plain` is True, then frame is `half_plain` type.
            When throw `exception`, then frame is `half` type.
        - `Literal['half']`: Add beautiful top and bottom side frame.
            When attribute `RConfigStdout.is_frame_plain` is True, then frame is `half_plain` type.
        - `Literal['top']`: Add beautiful top side frame.
            When attribute `RConfigStdout.is_frame_plain` is True, then frame is `top_plain` type.
        - `Literal['half_plain']`: Add plain top and bottom side frame.
        - `Literal['top_plain']`: Add plain top side frame.
    extra : Extra print text at the end.

    Returns
    -------
    Standard input string.
    """

    # Beautify.
    text = beautify_text(data, title=title, width=width, frame=frame)

    # Extra.
    if extra is not None:
        text += extra

    # Print.
    stdin = input(text)

    return stdin


def stop_print() -> None:
    """
    Stop standard output print.
    """

    # Stop.
    sys.stdout = RConfigStdout._io_null

    # Update status.
    RConfigStdout._stoped = True


def start_print() -> None:
    """
    Start standard output print.
    """

    # Check.
    if not RConfigStdout._stoped: return

    # Start.
    sys.stdout = RConfigStdout._io_stdout

    # Update status.
    RConfigStdout._stoped = False


def modify_print(preprocess: Callable[[str], str] | None) -> None:
    """
    Modify standard output print write method.

    Parameters
    ----------
    preprocess : Preprocess function.
        - `Callable[[str], str]`: Input old text, output new text, will trigger printing.
        - `Callable[[str], None]`: Input old text, no output, will not trigger printing.
    """


    # Define.
    def write(__s: str) -> int | None:
        """
        Modified standard output write method.

        Parameters
        ----------
        __s : Write text.

        Returns
        -------
        Number of text characters.
        """

        # Preprocess.
        __s = preprocess(__s)

        # Write.
        if __s.__class__ == str:
            write_len = RConfigStdout._io_stdout_write(__s)
            return write_len


    # Modify.
    RConfigStdout._io_stdout.write = write

    # Update status.
    RConfigStdout._modified = True


def reset_print() -> None:
    """
    Reset standard output print write method.
    """

    # Check.
    if not RConfigStdout._modified: return

    # Reset.
    RConfigStdout._io_stdout.write = RConfigStdout._io_stdout_write

    # Update status.
    RConfigStdout._modified = False


def add_print_position() -> None:
    """
    Add position text to standard output.
    """


    # Define.
    def preprocess(__s: str) -> str:
        """
        Preprocess function.

        Parameters
        ----------
        __s : Standard ouput text.

        Returns
        -------
        Preprocessed text.
        """

        # Break.
        if __s in ('\n', ' ', '[0m'): return __s

        # Get parameter.
        stack_params = get_stack_param('full', 3)
        stack_floor = stack_params[-1]

        ## Compatible 'echo'.
        if (
            stack_floor['filename'] == RConfigStdout._path_rstdout
            and stack_floor['name'] == 'echo'
        ):
            stack_floor = stack_params[-2]

        # Add.
        __s = 'File "%s", line %s\n%s' % (
            stack_floor['filename'],
            stack_floor['lineno'],
            __s
        )

        return __s


    # Modify.
    modify_print(preprocess)
