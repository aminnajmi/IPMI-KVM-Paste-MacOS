"""Application activity logging."""
from __future__ import annotations

import logging
from pathlib import Path


def create_logger() -> logging.Logger:
    logger = logging.getLogger("ipmi_paste")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    path = Path.home() / ".ipmi_paste" / "ipmi-paste.log"
    path.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(path, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    return logger
