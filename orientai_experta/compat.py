# -*- coding: utf-8 -*-
"""
Shims de compatibilidad para correr Experta (último release 2018) en Python
3.10+ / 3.14. IMPORTAR ESTE MÓDULO ANTES QUE experta.

  - collections.Mapping y cía  -> movidos a collections.abc en 3.10
  - inspect.getargspec         -> removido en 3.11
"""
import collections
import collections.abc
import inspect

for _name in ("Mapping", "MutableMapping", "Sequence", "MutableSequence",
              "Set", "MutableSet", "Hashable", "Iterable", "Callable"):
    if not hasattr(collections, _name):
        setattr(collections, _name, getattr(collections.abc, _name))

if not hasattr(inspect, "getargspec"):
    def getargspec(func):  # type: ignore
        s = inspect.getfullargspec(func)
        return (s.args, s.varargs, s.varkw, s.defaults)
    inspect.getargspec = getargspec  # type: ignore
