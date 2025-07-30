"""
Command modules for SlowCLI application.
"""

from .data_commands import DataCommands
from .network_commands import NetworkCommands
from .analysis_commands import AnalysisCommands
from .system_commands import SystemCommands

__all__ = [
    'DataCommands',
    'NetworkCommands',
    'AnalysisCommands',
    'SystemCommands'
]
