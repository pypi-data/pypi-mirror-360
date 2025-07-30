import logging

from fastpluggy.core.global_registry import GlobalRegistry
from fastpluggy.core.widgets.categories.input.button_list import ButtonListWidget


class ListButtonView(ButtonListWidget):
    logging.error('[deprecated] <code>ListButtonView</code> is deprecated; use <code>ButtonListWidget</code>!')
    GlobalRegistry.extend_globals(
        'migration_alert',
        ['Update your <code>ListButtonView</code> calls to use <code>ButtonListWidget</code> instead for the new widget system benefits.']
    )
    ...
