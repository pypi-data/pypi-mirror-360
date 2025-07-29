"""
Elara Wrapper - FastAPI middleware for request validation
"""

from .middleware import ElaraMiddleware, add_elara_middleware

__version__ = "0.1.0"
__all__ = ["ElaraMiddleware", "add_elara_middleware"]