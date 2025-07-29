"""
Tallyfy SDK - A modular Python SDK for Tallyfy API
"""

from .core import TallyfySDK, TallyfyError
from .models import *
from .user_management import UserManagement
from .task_management import TaskManagement
from .template_management import TemplateManagement
from .form_fields_management import FormFieldManagement

__version__ = "1.0.0"
__all__ = [
    "TallyfySDK",
    "TallyfyError",
    "UserManagement", 
    "TaskManagement",
    "TemplateManagement",
    "FormFieldManagement"
]