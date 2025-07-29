"""
RAGTrace Lite - Lightweight RAG Evaluation Framework

Original work Copyright 2024 RAGTrace Contributors
Modified work Copyright 2025 RAGTrace Lite Contributors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

This file has been modified from the original version in the RAGTrace project.
"""

__version__ = "1.0.0"
__author__ = "RAGTrace Lite Contributors"
__email__ = "contact@ragtrace-lite.com"
__license__ = "MIT OR Apache-2.0"

# Package exports
from .main import RAGTraceLite
from .config_loader import Config, load_config

__all__ = [
    "RAGTraceLite",
    "Config", 
    "load_config",
    "__version__",
    "__author__",
    "__email__",
    "__license__",
]