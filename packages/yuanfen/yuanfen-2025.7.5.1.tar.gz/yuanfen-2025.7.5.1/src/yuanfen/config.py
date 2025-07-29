import configparser
import json
import os

import yaml
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver

from .logger import Logger


class Config:
    instances = {}

    def __new__(cls, path, poll=True, logger=None):
        if path not in cls.instances:
            instance = super().__new__(cls)
            instance.file_path = os.path.abspath(path)
            instance.logger = logger or Logger()
            instance.data = {}
            instance.load()
            instance.observer = PollingObserver() if poll else Observer()
            instance.observer.schedule(ConfigChangeHandler(instance), path=instance.file_path, recursive=False)
            instance.observer.start()
            cls.instances[path] = instance
            return instance
        else:
            return cls.instances[path]

    def __getitem__(self, key):
        return self.data.get(key, None)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def load(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            if self.file_path.endswith(".json"):
                self.data = json.load(f)
            elif self.file_path.endswith(".yaml") or self.file_path.endswith(".yml"):
                self.data = yaml.safe_load(f)
            elif self.file_path.endswith(".ini"):
                parser = configparser.ConfigParser()
                parser.read_file(f)
                for section in parser.sections():
                    self.data[section] = {}
                    for key, value in parser.items(section):
                        self.data[section][key] = value
            else:
                raise ValueError("Unsupported config file format")


class ConfigChangeHandler(FileSystemEventHandler):
    def __init__(self, config: Config):
        super().__init__()
        self.config = config

    def on_modified(self, _):
        self.config.logger.info(f"{self.config.file_path} modified")
        self.config.load()

    def on_created(self, _):
        self.config.logger.info(f"{self.config.file_path} created")
        self.config.load()
