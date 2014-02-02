#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""description"""

from command.base_command import Command
import shell


class HelpCommand(Command):
    """Print help message"""

    def alias(self):
        return ['HELP', '?', 'H']

    def run(self, command=None, *args):
        buf = ['']

        def f(shell):
            # Print overview help.
            buf.append('{:20s}: brief description'.format('command (alias)'))
            buf.append('')

            for name, cmd in sorted((c.name(), c) for c in set(shell.commands.values())):
                alias = ', '.join(filter(lambda x: x != name, cmd.alias()))
                alias = '({})'.format(alias) if alias else ''
                buf.append('{:20s}: {}'.format('{} {}'.format(name, alias), cmd.__doc__))

            buf.append('')
            buf.append("see more messages to type 'help <command>'\n\n")
            shell.output.write('\n'.join(('  ' + x if x else '' for x in buf)))

        def g(shell):
            # Print specific help.
            c = shell.commands.get(command.upper())
            if not c:
                super(HelpCommand, self).run(command, *args)(shell)
            else:
                buf.append('{} - {}'.format(c.name(), c.__doc__))
                buf.append('')
                buf.append('{}'.format(c.help()))
                buf.append('\n')
            shell.output.write('\n'.join(('  ' + x if x else '' for x in buf)))

        return f if command is None else g
