"""Sub commands of the ``verdi`` command line interface.

The commands need to be imported here for them to be registered with the top-level command group.
"""
from aiida.plugins.entry_point import get_entry_points
from aiida_scheduler.cli import cmd_scheduler

eps = get_entry_points("aiida_scheduler.cmdline")
for ep in eps:
    ep.load()

__all__ = ["cmd_scheduler"]
