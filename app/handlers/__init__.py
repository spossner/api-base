"""Job handlers package.

Each handler module contains:
- Request schema (Pydantic model inheriting from BaseJobRequest)
- Handler function decorated with @register_handler

Import all handler modules to auto-register them.
"""

from app.handlers import data_processing, echo, long_running

__all__ = ["data_processing", "echo", "long_running"]
