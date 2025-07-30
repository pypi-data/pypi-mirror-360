import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    DEFAULT_CONFIG = {
        'theme': {
            'selected_color': 'cyan',
            'header_color': 'green',
        },
        'git': {
            'auto_fetch': False,
            'commit_prefix': '',
        },
        'ui': {
            'show_icons': True,
            'panel_size_ratio': [1, 1, 1, 1],
        },
        'keybindings': {
            'quit': 'q',
            'refresh': 'r',
            'stage_toggle': 's',
            'stage_all': 'a',
            'unstage_all': 'u',
            'commit': 'c',
            'push': 'p',
            'pull': 'P',
            'fetch': 'f',
            'checkout_branch': 'b',
            'new_branch': 'n',
            'delete_branch': 'd',
            'stash': 'S',
            'stash_pop': 'ctrl+s',
            'merge': 'm',
            'rebase': 'R',
            'diff': 'D',
            'show_commit': 'enter',
            'help': '?',
        }
    }
    
    def __init__(self):
        self.config_path = self._get_config_path()
        self.config = self._load_config()
    
    def _get_config_path(self) -> Path:
        config_dir = Path.home() / '.config' / 'lazygit-python'
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / 'config.yml'
    
    def _load_config(self) -> Dict[str, Any]:
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    user_config = yaml.safe_load(f) or {}
                return self._merge_configs(self.DEFAULT_CONFIG, user_config)
            except Exception:
                return self.DEFAULT_CONFIG.copy()
        else:
            self._save_default_config()
            return self.DEFAULT_CONFIG.copy()
    
    def _merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def _save_default_config(self):
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(self.DEFAULT_CONFIG, f, default_flow_style=False, sort_keys=False)
        except Exception:
            pass
    
    def get(self, key_path: str, default: Any = None) -> Any:
        keys = key_path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def set(self, key_path: str, value: Any):
        keys = key_path.split('.')
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
        self.save()
    
    def save(self):
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
        except Exception:
            pass