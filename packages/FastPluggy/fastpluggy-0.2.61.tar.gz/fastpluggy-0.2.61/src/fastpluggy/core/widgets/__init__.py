"""
FastPluggy Widget System

Clean, extensible widget architecture with auto-registration.
"""

from .base import AbstractWidget
from .fastpluggy_integration import FastPluggyWidgets

# Import all core widgets to trigger auto-registration

# Display widgets
from .categories.display.custom import *

# Data widgets
from .categories.data.table import *

# Input widgets
from .categories.input.button import *
from .categories.input.button_list import *
from .categories.input.form import *


__all__ = [
    'AbstractWidget',
    'FastPluggyWidgets',
    # Data widgets
    'TableWidget',
    # Display widgets
    'CustomTemplateWidget',
    # Input widgets
    'FormWidget',
    'ButtonWidget',
]
