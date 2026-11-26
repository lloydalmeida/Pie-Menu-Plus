# SPDX-License-Identifier: GPL-3.0-or-later
"""Multi-Level Pie Menu: nested pie menus with back navigation."""

from . import operators, menus, preferences, keymaps

_modules = (operators, menus, preferences, keymaps)


def register():
    for mod in _modules:
        mod.register()


def unregister():
    for mod in reversed(_modules):
        mod.unregister()
