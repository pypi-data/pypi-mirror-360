# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2025-06-13 02:05:46
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Type methods.
"""


from typing import Any, Self, TypeVar
from collections.abc import Callable


__all__ = (
    'T',
    'KT',
    'VT',
    'RStaticMeta',
    'RConfigMeta',
    'RNull',
    'RSingleton'
)


# Generic.
T = TypeVar('T') # Any.
KT = TypeVar('KT') # Any dictionary key.
VT = TypeVar('VT') # Any dictionary value.


class RStaticMeta(type):
    """
    Rey's `static meta` type.
    """


    def __call__(cls):
        """
        Call method.
        """

        # Throw exception.
        raise TypeError('static class, no instances allowed.')


class RConfigMeta(RStaticMeta):
    """
    Rey's `config meta` type.
    """


    def __getitem__(cls, name: str):
        """
        Get item.

        Parameters
        ----------
        name : Item name.

        Returns
        -------
        Item value.
        """

        # Get.
        item = getattr(cls, name)

        return item


    def __setitem__(cls, name: str, value: Any) -> None:
        """
        Set item.

        Parameters
        ----------
        name : Item name.
        """

        # Set.
        setattr(cls, name, value)


class RNull(object, metaclass=RStaticMeta):
    """
    Rey's `null` type.
    """


class RSingleton(object):
    """
    Rey's `singleton` type.
    When instantiated, method `__singleton__` will be called only once, and will accept arguments.

    Attributes
    ----------
    _instance : Global singleton instance.
    """

    _instance: Self | None = None


    def __new__(self, *arg: Any, **kwargs: Any) -> Self:
        """
        Build `singleton` instance.
        """

        # Build.
        if self._instance is None:
            self._instance = super().__new__(self)

            ## Singleton method.
            if hasattr(self, "__singleton__"):
                __singleton__: Callable = getattr(self, "__singleton__")
                __singleton__(self, *arg, **kwargs)

        return self._instance
