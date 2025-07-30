"""Function to register commands."""

import abc

__all__ = [
    "REGISTERED_COMMANDS",
    "Command",
    "register_command",
]


REGISTERED_COMMANDS = dict()


class Command(abc.ABC):
    """Sub-command for CLI interface.

    Parameters
    ----------
    name : str
        Name of the sub-command.
    logger : logging.Logger
        Logger to log the command run.

    Examples
    --------
    >>> class MyCommand(Command):
    ...     def add_parser(self, main_parser):
    ...         parser = main_parser.add_parser(self.name)
    ...         parser.add_argument("foo")
    ...     def run(self, args):
    ...         self.logger.info("Run my command")
    ...         print(args.foo)
    """

    def __init__(self, name, logger):
        self._name = name
        self._logger = logger

    @property
    def name(self):
        """Name of the command for :meth:`add_parser`."""
        return self._name

    @property
    def logger(self):
        """Logger for :meth:`run`."""
        return self._logger

    @abc.abstractmethod
    def add_parser(self, main_parser):
        """Add the command parser to main parser.

        Parameters
        ----------
        main_parser : argparse._SubParsersAction
            Subparser constructor having :class:`heavyedge.cli.ConfigArgumentParser` as
            parser class.
        """
        ...

    @abc.abstractmethod
    def run(self, args):
        """Run the command.

        Parameters
        ----------
        args : argparse.Namespace
        """
        ...


def register_command(name, desc):
    """Decorator to register the command class for the argument parser.

    Parameters
    ----------
    name : str
        The unique name of the command.
    desc : str
        A short description of the command's purpose.

    Examples
    --------
    Decorate the class definition.

    >>> from heavyedge.cli import Command, register_command
    >>> @register_command("foo", "My command")
    ... class MyCommand(Command):
    ...     ...

    See Also
    --------
    heavyedge.cli.Command
    """

    def register(cls):
        REGISTERED_COMMANDS[name] = (cls, desc)
        return cls

    return register
