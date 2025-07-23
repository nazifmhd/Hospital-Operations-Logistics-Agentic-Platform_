"""
Multi-Agent Hospital Operations System
Advanced LangGraph-based multi-agent coordination for hospital operations
"""

__version__ = "2.0.0"
__author__ = "Hospital Operations Team"
__description__ = "Multi-Agent System for Hospital Bed Management, Equipment Tracking, Staff Allocation, and Supply Inventory"

from .core.coordinator import coordinator
from .database.config import db_manager
from .database.models import *

__all__ = [
    "coordinator",
    "db_manager"
]
