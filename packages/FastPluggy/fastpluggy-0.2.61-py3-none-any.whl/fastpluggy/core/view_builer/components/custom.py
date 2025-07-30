import logging

from fastpluggy.core.global_registry import GlobalRegistry
from fastpluggy.core.widgets.categories.display.custom import CustomTemplateWidget


class CustomTemplateView(CustomTemplateWidget):
    logging.error('[deprecated] <code>CustomTemplateView</code> is deprecated; use <code>CustomTemplateWidget</code>!')
    GlobalRegistry.extend_globals(
        'migration_alert',
        ['Update your <code>CustomTemplateView</code> calls to use <code>CustomTemplateWidget</code> instead for the new widget system benefits.']
    )
    ...
