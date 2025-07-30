# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2024-07-17 09:46:40
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Exception methods.
"""


# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2022-12-05 14:09:42
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Interpreter system methods.
"""


from typing import Any, NoReturn, overload
from types import TracebackType
from collections.abc import Iterable
from sys import exc_info as sys_exc_info
from os.path import exists as os_exists
from traceback import format_exc
from warnings import warn as warnings_warn

from .rtype import Null


__all__ = (
    'RError',
    'RActiveError',
    'throw',
    'warn',
    'catch_exc',
    'check_least_one',
    'check_most_one',
    'check_file_found',
    'check_file_exist',
    'check_response_code'
)


class RError(Exception):
    """
    Rey `error` type.
    """


class RActiveError(RError):
    """
    Rey's `active error` type.
    """


def throw(
    exception: type[BaseException] = AssertionError,
    value: Any = Null,
    *values: Any,
    text: str | None = None,
    frame: int = 2
) -> NoReturn:
    """
    Throw exception.

    Parameters
    ----------
    exception : Exception Type.
    value : Exception value.
    values : Exception values.
    text : Exception text.
    frame : Number of code to upper level.
    """

    # Text.
    if text is None:
        if exception.__doc__ is not None:
            text = exception.__doc__.strip()
        if (
            text is None
            or text == ''
        ):
            text = 'use error'
        else:
            text = text[0].lower() + text[1:]

    ## Value.
    if value != Null:
        values = (value,) + values

        ### Name.
        from .rsystem import get_name
        name = get_name(value, frame)
        names = (name,)
        if values != ():
            names_values = get_name(values)
            if names_values is not None:
                names += names_values

        ### Convert.
        match exception:
            case TypeError():
                values = [
                    value.__class__
                    for value in values
                    if value is not None
                ]
            case TimeoutError():
                values = [
                    int(value)
                    if value % 1 == 0
                    else round(value, 3)
                    for value in values
                    if value.__class__ == float
                ]
        values = [
            repr(value)
            for value in values
        ]

        ### Join.
        if names == ():
            values_len = len(values)
            text_value = ', '.join(values)
            if values_len == 1:
                text_value = 'value is ' + text_value
            else:
                text_value = 'values is (%s)' % text_value
        else:
            names_values = zip(names, values)
            text_value = ', '.join(
                [
                    'parameter "%s" is %s' % (name, value)
                    for name, value in names_values
                ]
            )
        text += ' %s.' % text_value

    # Throw exception.
    exception = exception(text)
    raise exception


def warn(
    *infos: Any,
    exception: type[BaseException] = UserWarning,
    stacklevel: int = 3
) -> None:
    """
    Throw warning.

    Parameters
    ----------
    infos : Warn informations.
    exception : Exception type.
    stacklevel : Warning code location, number of recursions up the code level.
    """

    # Handle parameter.
    if infos == ():
        infos = 'Warning!'
    elif len(infos) == 1:
        if infos[0].__class__ == str:
            infos = infos[0]
        else:
            infos = str(infos[0])
    else:
        infos = str(infos)

    # Throw warning.
    warnings_warn(infos, exception, stacklevel)


def catch_exc(
    title: str | None = None
) -> tuple[str, type[BaseException], BaseException, TracebackType]:
    """
    Catch exception information and print, must used in `except` syntax.

    Parameters
    ----------
    title : Print title.
        - `None`: Not print.
        - `str`: Print and use this title.

    Returns
    -------
    Exception data.
        - `str`: Exception report text.
        - `type[BaseException]`: Exception type.
        - `BaseException`: Exception instance.
        - `TracebackType`: Exception traceback instance.
    """

    # Get parameter.
    exc_report = format_exc()
    exc_report = exc_report.strip()
    exc_type, exc_instance, exc_traceback = sys_exc_info()

    # Print.
    if title is not None:

        ## Import.
        from .rstdout import echo

        ## Execute.
        echo(exc_report, title=title, frame='half')

    return exc_report, exc_type, exc_instance, exc_traceback


@overload
def check_least_one(*values: None) -> NoReturn: ...

@overload
def check_least_one(*values: Any) -> None: ...

def check_least_one(*values: Any) -> None:
    """
    Check that at least one of multiple values is not null, when check fail, then throw exception.

    Parameters
    ----------
    values : Check values.
    """

    # Check.
    for value in values:
        if value is not None:
            return

    # Throw exception.
    from .rsystem import get_name
    vars_name = get_name(values)
    if vars_name is not None:
        vars_name_de_dup = list(set(vars_name))
        vars_name_de_dup.sort(key=vars_name.index)
        vars_name_str = ' ' + ' and '.join([f'"{var_name}"' for var_name in vars_name_de_dup])
    else:
        vars_name_str = ''
    raise TypeError(f'at least one of parameters{vars_name_str} is not None')


def check_most_one(*values: Any) -> None:
    """
    Check that at most one of multiple values is not null, when check fail, then throw exception.

    Parameters
    ----------
    values : Check values.
    """

    # Check.
    exist = False
    for value in values:
        if value is not None:
            if exist is True:

                # Throw exception.
                from .rsystem import get_name
                vars_name = get_name(values)
                if vars_name is not None:
                    vars_name_de_dup = list(set(vars_name))
                    vars_name_de_dup.sort(key=vars_name.index)
                    vars_name_str = ' ' + ' and '.join([f'"{var_name}"' for var_name in vars_name_de_dup])
                else:
                    vars_name_str = ''
                raise TypeError(f'at most one of parameters{vars_name_str} is not None')

            exist = True


def check_file_found(path: str) -> None:
    """
    Check if file path found, if not, throw exception.

    Parameters
    ----------
    path : File path.
    """

    # Check.
    exist = os_exists(path)

    # Throw exception.
    if not exist:
        throw(FileNotFoundError, path)


def check_file_exist(path: str) -> None:
    """
    Check if file path exist, if exist, throw exception.

    Parameters
    ----------
    path : File path.
    """

    # Check.
    exist = os_exists(path)

    # Throw exception.
    if exist:
        throw(FileExistsError, path)


def check_response_code(
    code: int,
    range_: int | Iterable[int] | None = None
) -> bool:
    """
    Check if the response code is in range.

    Parameters
    ----------
    code : Response code.
    range_ : Pass the code range.
        - `None`: Check if is between 200 and 299.
        - `int`: Check if is this value.
        - `Iterable`: Check if is in sequence.

    Returns
    -------
    Check result.
    """

    # Check.
    match range_:
        case None:
            result = code // 100 == 2
        case int():
            result = code == range_
        case _ if hasattr(range_, '__contains__'):
            result = code in range_
        case _:
            throw(TypeError, range_)

    # Throw exception.
    if not result:
        throw(value=code)

    return result
