# @Time  : 2025/06/16
# @Author: DriftCloud
# @File  : config.py

import json
import os
import builtins
from typing import Any, Dict, Optional

__all__ = ['Config']

class Config:
    _config_file_path: str
    _configs: Dict[str, Any]

    def __init__(self, config_file_path: str = 'config.json'):
        self._config_file_path = os.path.abspath(config_file_path)
        if os.path.exists(self._config_file_path):
            with builtins.open(self._config_file_path, 'r', encoding='utf-8') as f:
                self._configs = json.load(f)
        else:
            self._configs = {}

    def get(self, key: str, default: Any = None) -> Any:
        return self._configs.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._configs[key] = value

    def save(self) -> None:
        with builtins.open(self._config_file_path, 'w', encoding='utf-8') as f:
            json.dump(self._configs, f, ensure_ascii=False, indent=4)

    def __del__(self) -> None:
        self.save()