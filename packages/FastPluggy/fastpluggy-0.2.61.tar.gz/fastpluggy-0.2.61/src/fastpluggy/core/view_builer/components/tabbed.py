import logging

from fastpluggy.core.global_registry import GlobalRegistry
from fastpluggy.core.widgets.categories.layout.tabbed import TabbedWidget


class TabbedView(TabbedWidget):
    logging.error('[deprecated] <code>TabbedView</code> is deprecated; use <code>TabbedWidget</code>!')
    GlobalRegistry.extend_globals(
        'migration_alert',
        ['Update your <code>TabbedView</code> calls to use <code>TabbedWidget</code> instead for the new widget system benefits.']
    )
    ...
