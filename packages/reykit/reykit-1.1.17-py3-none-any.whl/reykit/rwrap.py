# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2022-12-05 14:12:25
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Decorator methods.
"""


from typing import Any, Literal, overload
from collections.abc import Callable
from io import IOBase, StringIO
from inspect import getdoc
from functools import wraps as functools_wraps
from threading import Thread
from argparse import ArgumentParser
from contextlib import redirect_stdout

from .rexception import catch_exc
from .rstdout import echo
from .rsystem import get_arg_info
from .rtime import now, time_to, RTimeMark


__all__ = (
    'wrap_frame',
    'wrap_runtime',
    'wrap_thread',
    'wrap_exc',
    'wrap_retry',
    'wrap_dos_command',
    'wrap_cache_data',
    'wrap_cache',
    'wrap_redirect_stdout'
)


def wrap_frame(decorator: Callable) -> Callable:
    """
    Decorative frame.

    Parameters
    ----------
    decorator : Decorator function.

    Retuens
    -------
    Decorated decorator.

    Examples
    --------
    Decoration function method one.
    >>> @wrap_func
    >>> def func(): ...
    >>> result = func(param_a, param_b, param_c=1, param_d=2)

    Decoration function method two.
    >>> def func(): ...
    >>> result = wrap_func(func, param_a, param_b, param_c=1, param_d=2)

    Decoration function method three.
    >>> def func(): ...
    >>> result = wrap_func(func, _execute=True)
    
    Decoration function method four.
    >>> def func(): ...
    >>> func = wrap_func(func)
    >>> result = func(param_a, param_b, param_c=1, param_d=2)

    Decoration function method five.
    >>> def func(): ...
    >>> func = wrap_func(func, param_a, param_c=1, _execute=False)
    >>> result = func(param_b, param_d=2)
    """


    # Decorate Decorator.
    @overload
    def wrap(func: Callable, *args: Any, _execute: None = None, **kwargs: Any) -> Callable | Any: ...

    @overload
    def wrap(func: Callable, *args: Any, _execute: Literal[True] = None, **kwargs: Any) -> Any: ...

    @overload
    def wrap(func: Callable, *args: Any, _execute: Literal[False] = None, **kwargs: Any) -> Callable: ...

    @functools_wraps(decorator)
    def wrap(func: Callable, *args: Any, _execute: bool | None = None, **kwargs: Any) -> Callable | Any:
        """
        Decorative shell.

        Parameters
        ----------
        func : Function.
        args : Position arguments of function.
        _execute : Whether execute function, otherwise decorate function.
            - `None`, When parameter `args` or `kwargs`: have values, then True, otherwise False.
            - `bool`: Use this value.
        kwargs : Keyword arguments of function.

        Returns
        -------
        Decorated function or function return.
        """

        # Handle parameter.
        if _execute is None:
            if args != () or kwargs != {}:
                _execute = True
            else:
                _execute = False

        # Direct execution.
        if _execute:
            result = decorator(func, *args, **kwargs)
            return result


        # Decorate function.
        @functools_wraps(func)
        def wrap_sub(*_args: Any, **_kwargs: Any) -> Any:
            """
            Decorative sub shell.

            Parameters
            ----------
            args : Position arguments of function.
            kwargs : Keyword arguments of function.

            Returns
            -------
            Function return.
            """

            # Decorate function.
            result = decorator(func, *args, *_args, **kwargs, **_kwargs)

            return result


        return wrap_sub


    return wrap


@overload
def wrap_runtime(
    func: Callable,
    *args: Any,
    _return_report: Literal[False] = False,
    **kwargs: Any
) -> Any: ...

@overload
def wrap_runtime(func: Callable,
    *args: Any,
    _return_report: Literal[True] = False,
    **kwargs: Any
) -> tuple[Any, str]: ...

@wrap_frame
def wrap_runtime(
    func: Callable,
    *args: Any,
    _return_report: bool = False,
    **kwargs: Any
) -> Any | tuple[Any, str]:
    """
    Decorator, print or return runtime report of the function.

    Parameters
    ----------
    func : Function to be decorated.
    args : Position arguments of decorated function.
    _return_report : Whether return report, otherwise print report.
    kwargs : Keyword arguments of decorated function.

    Returns
    -------
    Function execution result and runtime report.
    """

    # Execute function and marking time.
    rtm = RTimeMark()
    rtm()
    result = func(*args, **kwargs)
    rtm()

    # Generate report.
    start_time = rtm.record[0]['datetime']
    spend_time = rtm.record[1]['timedelta']
    end_time = rtm.record[1]['datetime']
    start_str = time_to(start_time, True)[:-3]
    spend_str = time_to(spend_time, True)[:-3]
    end_str = time_to(end_time, True)[:-3]
    report = 'Start: %s -> Spend: %ss -> End: %s' % (
        start_str,
        spend_str,
        end_str
    )
    title = func.__name__

    # Return report.
    if _return_report:
        return result, report

    # Print report.
    echo(report, title=title)

    return result


@overload
def wrap_thread(
    func: Callable,
    *args: Any,
    _daemon: bool = True,
    **kwargs: Any
) -> Thread: ...

@wrap_frame
def wrap_thread(
    func: Callable,
    *args: Any,
    _daemon: bool = True,
    **kwargs: Any
) -> Thread:
    """
    Decorator, function start in thread.

    Parameters
    ----------
    func : Function to be decorated.
    args : Position arguments of decorated function.
    _daemon : Whether it is a daemon thread.
    kwargs : Keyword arguments of decorated function.

    Returns
    -------
    Thread object.
    """

    # Handle parameter.
    thread_name = '%s_%d' % (func.__name__, now('timestamp'))

    # Create thread.
    thread = Thread(target=func, name=thread_name, args=args, kwargs=kwargs)
    thread.daemon = _daemon

    # Start thread.
    thread.start()

    return thread


@overload
def wrap_exc(
    func: Callable,
    *args: Any,
    _exception: BaseException | tuple[BaseException, ...] = BaseException,
    _handler: Callable | None = None,
    **kwargs: Any
) -> Any | None: ...

@wrap_frame
def wrap_exc(
    func: Callable,
    *args: Any,
    _exception: BaseException | tuple[BaseException, ...] = BaseException,
    _handler: Callable | None = None,
    **kwargs: Any
) -> Any | None:
    """
    Decorator, execute function with `try` and `except` syntax.

    Parameters
    ----------
    func : Function to be decorated.
    args : Position arguments of decorated function.
    _exception : Catch exception types.
    _handler : Exception handler, will return value.
    kwargs : Keyword arguments of decorated function.

    Returns
    -------
    Execution result of function or exception handle method.
    """

    # Execute function.
    try:
        result = func(*args, **kwargs)

    # Handle exception.
    except _exception:
        if _handler is not None:
            result = _handler()
        else:
            result = None

    return result


@overload
def wrap_retry(
    func: Callable,
    *args: Any,
    _report: str | None = None,
    _exception: BaseException | tuple[BaseException, ...] = BaseException,
    _try_total: int = 1,
    _try_count: int = 0,
    **kwargs: Any
) -> Any: ...

@wrap_frame
def wrap_retry(
    func: Callable,
    *args: Any,
    _report: str | None = None,
    _exception: BaseException | tuple[BaseException, ...] = BaseException,
    _try_total: int = 1,
    _try_count: int = 0,
    **kwargs: Any
) -> Any:
    """
    Decorator, try again.

    Parameters
    ----------
    func : Function to be decorated.
    args : Position arguments of decorated function.
    _report : Print report title.
        - `None`: Not print.
        - `str`: Print and use this title.
    _exception : Catch exception types.
    _try_total : Retry total.
    _try_count : Retry count.
    kwargs : Keyword arguments of decorated function.

    Returns
    -------
    Function execution result.
    """

    # Try count not full.
    if _try_count < _try_total:

        ## Try.
        try:
            result = func(*args, **kwargs)
        except _exception:

            ## Report.
            if _report is not None:
                exc_report, *_ = catch_exc()
                echo(
                    exc_report,
                    'Retrying...',
                    title=_report,
                    frame='half'
                )

            ### Retry.
            _try_count += 1
            result = wrap_retry(
                func,
                *args,
                _report=_report,
                _exception=_exception,
                _try_total=_try_total,
                _try_count=_try_count,
                **kwargs
            )

    # Try count full.
    else:
        result = func(*args, **kwargs)

    return result


@overload
def wrap_dos_command(
    func: Callable,
    *args: Any,
    **kwargs: Any
) -> Any: ...

@wrap_frame
def wrap_dos_command(
    func: Callable,
    *args: Any,
    **kwargs: Any
) -> Any:
    """
    Decorator, use DOS command to input arguments to function.
    Use DOS command `python file --help` to view help information.

    Parameters
    ----------
    func : Function to be decorated.
    args : Position arguments of decorated function.
    kwargs : Keyword arguments of decorated function.

    Returns
    -------
    Function execution result.
    """

    # Get parameter.
    arg_info = get_arg_info(func)

    # Set DOS command.
    usage = getdoc(func)
    if usage is not None:
        usage = 'input arguments to function "%s"\n\n%s' % (func.__name__, usage)
    parser = ArgumentParser(usage=usage)
    for info in arg_info:
        annotation_text = str(info['annotation'])
        if info['annotation'] is None:
            arg_type = str
            arg_help = None
        else:
            if 'str' in annotation_text:
                arg_type = str
            elif 'float' in annotation_text:
                arg_type = float
            elif 'int' in annotation_text:
                arg_type = int
            elif 'bool' in annotation_text:
                arg_type = bool
            else:
                arg_type = str
            arg_help = annotation_text
        if info['type'] in ('var_position', 'var_position'):
            parser.add_argument(
                info['name'],
                nargs='*',
                type=arg_type,
                help=arg_help
            )
        else:
            parser.add_argument(
                info['name'],
                nargs='?',
                type=arg_type,
                help=arg_help
            )
            kw_name = '--' + info['name']
            parser.add_argument(
                kw_name,
                nargs='*',
                type=arg_type,
                help=arg_help,
                metavar='value',
                dest=kw_name
            )

    # Get argument.
    namespace = parser.parse_args()
    command_args = []
    command_kwargs = {}
    for info in arg_info:

        ## Position argument.
        value = getattr(namespace, info['name'])
        if value is not None:
            if value.__class__ == list:
                command_args.extend(value)
            else:
                command_args.append(value)

        ## Keyword argument.
        if info['type'] not in ('var_position', 'var_position'):
            kw_name = '--' + info['name']
            kw_value = getattr(namespace, kw_name)
            if kw_value.__class__ == list:
                kw_value_len = len(kw_value)
                match kw_value_len:
                    case 0:
                        kw_value = None
                    case 1:
                        kw_value = kw_value[0]
                command_kwargs[info['name']] = kw_value

    # Execute function.
    if command_args == []:
        func_args = args
    else:
        func_args = command_args
    func_kwargs = {
        **kwargs,
        **command_kwargs
    }
    result = func(
        *func_args,
        **func_kwargs
    )

    return result


# Cache decorator data.
wrap_cache_data: dict[Callable, list[tuple[Any, Any, Any]]] = {}


@overload
def wrap_cache(
    func: Callable,
    *args: Any,
    _overwrite: bool = False,
    **kwargs: Any
) -> Any: ...

@wrap_frame
def wrap_cache(
    func: Callable,
    *args: Any,
    _overwrite: bool = False,
    **kwargs: Any
) -> Any:
    """
    Decorator, Cache the return result of function input.
    if no cache, cache it.
    if cached, skip execution and return result.

    Parameters
    ----------
    func : Function to be decorated.
    args : Position arguments of decorated function.
    _overwrite : Whether to overwrite cache.
    kwargs : Keyword arguments of decorated function.

    Returns
    -------
    Function execution result.
    """

    # Index.
    wrap_cache_data_func = wrap_cache_data.setdefault(func, [])
    cache_index = None
    for index, (cache_args, cache_kwargs, cache_result) in enumerate(wrap_cache_data_func):
        if (
            cache_args == args
            and cache_kwargs == kwargs
        ):
            if _overwrite:
                cache_index = index
                break
            else:
                return cache_result

    # Execute.
    result = func(*args, **kwargs)

    # Cache.
    data = (args, kwargs, result)
    if cache_index is None:
        wrap_cache_data_func.append(data)
    else:
        wrap_cache_data_func[cache_index] = data

    return result


@overload
def wrap_redirect_stdout(
    func: Callable,
    *args: Any,
    _redirect: list | IOBase | None = None,
    **kwargs: Any
) -> Any: ...

@wrap_frame
def wrap_redirect_stdout(
    func: Callable,
    *args: Any,
    _redirect: list | IOBase | None = None,
    **kwargs: Any
) -> Any:
    """
    Redirect standard output.

    Parameters
    ----------
    func : Function to be decorated.
    args : Position arguments of decorated function.
    _redirect : Redirect output list or IO object.
    kwargs : Keyword arguments of decorated function.

    Returns
    -------
    Function execution result.
    """

    # Get parameter.
    if isinstance(_redirect, IOBase):
        str_io = _redirect
    else:
        str_io = StringIO()

    # Execute.
    with redirect_stdout(str_io):
        result = func(*args, **kwargs)

    # Save.
    if _redirect.__class__ == list:
        value = str_io.getvalue()
        _redirect.append(value)

    return result
