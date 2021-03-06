# Copyright (c) Hiroyuki Deguchi
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import sys
from typing import IO, Any, Optional

import click
from click import File, confirm, pass_context, style
from click_help_colors import HelpColorsCommand, HelpColorsGroup
import rich
from rich.bar import Bar
from rich.box import HORIZONTALS, ROUNDED, SQUARE
from rich.console import Console
from rich.table import Table
from rich.theme import Theme

from nlpack import __version__

CONTEXT = {
    "help_option_names": ["--help", "-h"],
}


def command(*args, **kwargs):
    return click.group(
        *args,
        **kwargs,
        cls=HelpColorsGroup,
        help_headers_color="green",
        help_options_color="cyan",
        context_settings=CONTEXT,
    )


def subcommand(*args, **kwargs):
    return click.command(
        *args,
        **kwargs,
        cls=HelpColorsCommand,
        help_headers_color="green",
        help_options_color="cyan",
        context_settings=CONTEXT,
    )


def option(*args, choice=None, **kwargs):
    if choice is not None:
        return click.option(
            *args,
            **kwargs,
            type=click.Choice(choice),
            show_default=True,
        )
    return click.option(
        *args,
        **kwargs,
        show_default=True,
    )


def argument(*args, **kwargs):
    return click.argument(*args, **kwargs)


def version_option(*args, **kwargs):
    return click.version_option(__version__, "--version", "-V", message="%(version)s")


def add_subcommands(parent, module):
    for member_name in dir(module):
        if member_name.startswith("__"):
            continue
        member = getattr(module, member_name)
        if isinstance(member, click.Command):
            parent.add_command(member)


def highlight(strings: str):
    return style(strings, fg="cyan")


def echo(
    msg: str,
    nl: bool = True,
    success: bool = False,
    failed: bool = False,
    err: bool = False,
    fg: str = "",
):
    if success:
        fg = "green"
    elif failed:
        fg = "red"
    return click.secho(msg, nl=nl, err=err, fg=fg)


def abort(msg: str, exit_code: int = 1):
    echo(msg, failed=True, err=True)
    sys.exit(exit_code)


def print_box(s: str):
    _box = Table(box=ROUNDED, show_header=False)
    _box.add_row(s)
    rprint(_box)


def rprint(
    *objects: Any,
    sep: str = " ",
    end: str = "\n",
    file: Optional[IO[str]] = None,
    flush: bool = False,
) -> None:
    r"""Print object(s) supplied via positional arguments.
    This function has an identical signature to the built-in print.
    For more advanced features, see the :class:`~rich.console.Console` class.

    Args:
        sep (str, optional): Separator between printed objects. Defaults to " ".
        end (str, optional): Character to write at end of output. Defaults to "\\n".
        file (IO[str], optional): File to write to, or None for stdout. Defaults to None.
        flush (bool, optional): Has no effect as Rich always flushes output. Defaults to False.

    """
    write_console = Console(theme=Theme(inherit=False)) if file is None else Console(file=file)
    return write_console.print(*objects, sep=sep, end=end)


def print_no_crop(*args, **kwargs):
    console = Console(width=sys.maxsize)
    console.print(*args, **kwargs)


def print_table(*args, **kwargs):
    console = Console()
    console.print(*args, **kwargs)


def option_num_workers(short_option: Optional[str] = None):
    argument_strs = ["--num-workers"]
    if short_option is not None:
        argument_strs.append(short_option)

    return option(
        *argument_strs, type=int, metavar="N", default=8, help="Number of workers."
    )
