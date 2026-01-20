"""
Vintage Framework - Configuration Module
=========================================

This module contains all configuration settings for the vintage curve pipeline.

Structure:
- base_config.py: Universal standards (aggregation level, date filters, test groups)
- paths.py: Data source paths (Hive, parquet, EDW)
- campaigns/: Campaign-specific configurations (one file per product)
"""

from .base_config import *
from .paths import *
