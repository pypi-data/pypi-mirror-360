import logging

from fastpluggy.core.global_registry import GlobalRegistry
from fastpluggy.core.widgets.categories.input.form import FormWidget


class FormView(FormWidget):
    logging.error('[deprecated] <code>FormView</code> is deprecated; use <code>FormWidget</code>!')
    GlobalRegistry.extend_globals(
        'migration_alert',
        ['Update your <code>FormView</code> calls to use <code>FormWidget</code> instead for the new widget system benefits.']
    )
    ...
