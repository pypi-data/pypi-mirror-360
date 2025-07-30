# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2023-12-06 16:09:59
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Inject DLL file methods.
"""


__all__ = (
    'inject_dll',
)


def inject_dll(
    id_: int,
    path: str
) -> None:
    """
    Inject DLL file.

    Parameters
    ----------
    id_ : Process ID.
    path : DLL file path.
    """


    from ctypes import create_string_buffer

    from .rdll_inject_core import InjectDLL


    # Get parameter.
    path_bytes = path.encode()
    buffer = create_string_buffer(path_bytes)

    # Inject.
    InjectDLL(id_, buffer)
