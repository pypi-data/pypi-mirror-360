import os

from haplohub_cli import settings


def ensure_config_dir():
    os.makedirs(settings.CONFIG_DIR, exist_ok=True)
