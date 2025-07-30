"""Argument parser."""

import argparse

import yaml

__all__ = [
    "ConfigFileAction",
    "ConfigArgumentParser",
]


class ConfigFileAction(argparse.Action):
    """Action for an argument to load values from YAML config file.

    The config file consists of key-value pairs for arguments.
    Explicitly passed argument overloads the config file value.
    """

    def __call__(self, parser, namespace, values, option_string=None):
        if isinstance(parser, ConfigArgumentParser):
            config_args = [arg.dest for arg in parser.config_arguments()]
        else:
            config_args = []
        if values is None:
            return
        with values as f:
            data = {
                key.replace("-", "_"): val for (key, val) in yaml.full_load(f).items()
            }
        for k, v in vars(namespace).items():
            if v is None and k in config_args and k in data:
                setattr(namespace, k, data[k])


class ConfigArgumentParser(argparse.ArgumentParser):
    """Argument parser which can read config file.

    Use :meth:`add_config_argument` to add an argument which can be read from the
    config file. When the first config argument is added, the ``--config`` option is
    automatically added.

    Examples
    --------
    >>> from heavyedge.cli import ConfigArgumentParser
    >>> parser = ConfigArgumentParser("foo")
    >>> _ = parser.add_config_argument("--bar")
    >>> parser.print_help()
    usage: foo [-h] [--config CONFIG] [--bar BAR]
    <BLANKLINE>
    options:
    -h, --help       show this help message and exit
    --config CONFIG  YAML file specifying config options.
    <BLANKLINE>
    config options:
    --bar BAR
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._config_argument_group = self.add_argument_group("config options")
        self._config_argument = []

    def config_arguments(self):
        return self._config_argument

    def add_config_argument(self, name, **kwargs):
        """Add argument which can be read from the config file.

        Parameters
        ----------
        name : str
            Name of the argument.
        kwargs : dict
            Additional arguments passed to :meth:`argparse.ArgumentParser.add_argument`.
        """
        kwargs.update(required=False, default=None)
        if len(self.config_arguments()) == 0:
            # First config argument: add config parser first
            self.add_argument(
                "--config",
                type=open,
                action=ConfigFileAction,
                help="YAML file specifying config options.",
            )
        ret = self._config_argument_group.add_argument(name, **kwargs)
        self._config_argument.append(ret)
        return ret
