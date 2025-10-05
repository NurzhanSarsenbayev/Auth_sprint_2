# core/config/__init__.py
import os
from .config import Settings
from .test_config import TestSettings

if os.getenv("TESTING", "0") == "1":
    settings = TestSettings()
else:
    settings = Settings()