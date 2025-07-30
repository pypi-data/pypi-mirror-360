"""
SlowCLI - A deliberately slow CLI application with complex argument structures.

This package is designed to simulate real-world slow startup scenarios
with heavy imports and complex argument parsing.
"""

import time
import sys
import logging
from pathlib import Path

# Heavy imports to simulate slow startup
print("Loading SlowCLI... This may take a moment...", file=sys.stderr)

# Simulate heavy imports with delays
time.sleep(0.5)  # Simulate import time

try:
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import cross_val_score
    import requests
    import aiohttp
    import asyncio
    import yaml
    import toml
    import json
    from jinja2 import Template
    import psutil
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress
    import argcomplete
    import argparse
    from typing import Dict, List, Optional, Union, Any
    from dataclasses import dataclass
    from enum import Enum
    import hashlib
    import base64
    import gzip
    import bz2
    import lzma
    from datetime import datetime, timedelta
    import threading
    import multiprocessing
    from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

    print("✓ Heavy libraries loaded successfully", file=sys.stderr)

    # Global console for rich output
    console = Console()

except ImportError as e:
    print(f"⚠ Warning: Some optional dependencies not available: {e}", file=sys.stderr)
    # Fallback console without rich
    console = None

# Additional delay to simulate processing
time.sleep(0.3)

# Version information
__version__ = "0.1.5"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Performance tracking
startup_time = time.time()

def get_startup_time():
    """Return the time taken to import the package."""
    return time.time() - startup_time

# Export main components
from .main import main
from .cli import SlowCLI
from .utils import PerformanceTracker, ConfigManager

__all__ = [
    'main',
    'SlowCLI',
    'PerformanceTracker',
    'ConfigManager',
    'get_startup_time',
    '__version__',
    '__author__',
    '__email__'
]

print(f"✓ SlowCLI v{__version__} loaded in {get_startup_time():.2f}s", file=sys.stderr)
