import logging

from fastpluggy.core.global_registry import GlobalRegistry
from fastpluggy.core.widgets import ButtonWidget
from fastpluggy.core.widgets.categories.input.button import FunctionButtonWidget, AutoLinkWidget, BaseButtonWidget


class AutoLinkView(AutoLinkWidget):
    logging.error('[deprecated] <code>AutoLinkView</code> is deprecated; use <code>AutoLinkWidget</code>!')
    GlobalRegistry.extend_globals(
        'migration_alert',
        ['Update your <code>AutoLinkView</code> calls to use <code>AutoLinkWidget</code> for the new widget system benefits.']
    )

    ...


class FunctionButtonView(FunctionButtonWidget):
    logging.error('[deprecated] <code>FunctionButtonView</code> is deprecated; use <code>FunctionButtonWidget</code>!')
    GlobalRegistry.extend_globals(
        'migration_alert',
        ['Update your <code>FunctionButtonView</code> calls to use <code>FunctionButtonWidget</code> for the new widget system benefits.']
    )

    ...


class ButtonView(ButtonWidget):
    logging.error('[deprecated] <code>ButtonView</code> is deprecated; use <code>ButtonWidget</code>!')
    GlobalRegistry.extend_globals(
        'migration_alert',
        ['Update your <code>ButtonView</code> calls to use <code>ButtonWidget</code> instead for the new widget system benefits.']
    )

    ...


class AbstractButtonView(BaseButtonWidget):
    logging.error('[deprecated] <code>AbstractButtonView</code> is deprecated; use <code>BaseButtonWidget</code>!')
    GlobalRegistry.extend_globals(
        'migration_alert',
        ['Update your <code>AbstractButtonView</code> calls to use <code>BaseButtonWidget</code> for the new widget system benefits.']
    )

    ...
