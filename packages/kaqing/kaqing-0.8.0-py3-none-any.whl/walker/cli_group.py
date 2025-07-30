import logging
import click
from click_default_group import DefaultGroup

LOGGING_LEVELS = {
    0: logging.NOTSET,
    1: logging.ERROR,
    2: logging.WARN,
    3: logging.INFO,
    4: logging.DEBUG,
}

@click.group(invoke_without_command=True, cls=DefaultGroup, default='repl', default_if_no_args=True)
def cli():
    pass