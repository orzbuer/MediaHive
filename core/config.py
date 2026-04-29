import os
import configparser
import logging

logger = logging.getLogger(__name__)

_CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.ini')


class _Section:
    """Proxy object that provides attribute-style access to a config section."""

    def __init__(self, parser: configparser.ConfigParser, section: str):
        self._parser = parser
        self._section = section

    def __getattr__(self, key: str) -> str:
        try:
            return self._parser.get(self._section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            raise AttributeError(f"Config has no option '{key}' in section [{self._section}]")

    def items(self):
        return dict(self._parser.items(self._section))


class Config:
    """Application configuration loaded from config.ini."""

    def __init__(self, config_file: str = _CONFIG_FILE):
        self._parser = configparser.ConfigParser()
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Config file not found: {config_file}")
        self._parser.read(config_file, encoding='utf-8')
        logger.debug(f"Loaded config from {config_file}")

    def __getattr__(self, section: str) -> _Section:
        if section.startswith('_'):
            raise AttributeError(section)
        if not self._parser.has_section(section):
            raise AttributeError(f"Config has no section [{section}]")
        return _Section(self._parser, section)


cfg = Config()
