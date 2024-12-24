#!/usr/bin/env python3
# Copyright (c) Hiroyuki Deguchi
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import sys

from nlpack import analyzer, cli, normalizer, preprocessor, tokenizer


@cli.command("main")
@cli.version_option()
@cli.pass_context
def main(ctx):
    """
    nlpack v0.0.1

    Collections of natural language processing tools.
    """


@main.command("help")
@cli.argument("command", nargs=-1)
@cli.pass_context
def help(ctx, command):
    """
    Show the manual of a command.
    """

    command_module = main
    num_commands = len(command)
    for c, cmd in enumerate(command, start=1):
        command_module = command_module.get_command(ctx, cmd)
        if command_module is None or (
            getattr(command_module, "get_command", None) is None and c != num_commands
        ):
            cli.echo("Command not found.", err=True)
            sys.exit(1)

    cli.echo(command_module.get_help(ctx))
    sys.exit(0)


@main.group("analyzer")
@cli.pass_context
def _analyzer(ctx):
    """
    Analysis tools
    """
    pass


@main.group("preprocessor")
@cli.pass_context
def _preprocessor(ctx):
    """
    Preprocessing tools
    """
    pass


cli.add_subcommands(main, normalizer)
cli.add_subcommands(main, tokenizer)
cli.add_subcommands(_analyzer, analyzer)
cli.add_subcommands(_preprocessor, preprocessor)


if __name__ == "__main__":
    main()
