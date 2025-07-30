from genericpath import exists

from haplohub_cli.config.config import Config

from .. import settings
from .environments import ENVIRONMENTS

defaults = Config(
    redirect_port=8088,
    **ENVIRONMENTS["prod"],
)


class ConfigManager:
    def __init__(self, config_file: str):
        self.config_file = config_file
        self._config = None
        self.read_config()

    def init_config(self):
        if exists(self.config_file):
            return

        self._config = defaults
        self.save()

    def read_config(self):
        if not exists(self.config_file):
            self.init_config()

        self._config = Config.parse_file(self.config_file)

    def switch_environment(self, environment: str):
        if environment not in ENVIRONMENTS:
            raise ValueError(f"Invalid environment: {environment}")

        for key, value in ENVIRONMENTS[environment].items():
            setattr(self._config, key, value)

        self.save()

    def save(self):
        with open(self.config_file, "wt") as f:
            f.write(self._config.json(indent=4))

    def reset(self):
        self._config = defaults
        self.save()

    @property
    def config(self):
        if self._config is None:
            self.read_config()
        return self._config


config_manager = ConfigManager(config_file=settings.CONFIG_FILE)
