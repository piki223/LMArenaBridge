"""
Configuration management for LMArenaBridge.
Handles loading, saving, and managing configuration.
"""

import json
import os
from typing import Optional, Dict, Any
from collections import defaultdict

from . import constants


# Global state
_current_config_file: str = constants.CONFIG_FILE
_current_token_index: int = 0


def get_config_file() -> str:
    """Get the current config file path."""
    return _current_config_file


def set_config_file(path: str) -> None:
    """Set the config file path (useful for tests)."""
    global _current_config_file, _current_token_index
    if _current_config_file != path:
        _current_config_file = path
        _current_token_index = 0


def get_config() -> dict:
    """
    Load configuration from file with defaults.
    Returns a dictionary with all configuration values.
    """
    global _current_token_index
    
    # Reset token index if config file changed
    if _current_token_index != 0:
        global_state = _get_global_state()
        if global_state.get("_last_config_file") != _current_config_file:
            _current_token_index = 0
    
    try:
        with open(_current_config_file, "r") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config = {}
    except Exception:
        config = {}

    # Ensure default keys exist
    _apply_config_defaults(config)
    
    return config


def _apply_config_defaults(config: dict) -> None:
    """Apply default values to config dictionary."""
    config.setdefault("password", "admin")
    config.setdefault("auth_token", "base64-eyJhY2Nlc3NfdG9rZW4iOiJleUpoYkdjaU9pSkZVekkxTmlJc0ltdHBaQ0k2SWpBNVlUSTNPVFl6TFRjek5tWXROR00wWmkwNU5HSXlMV0ptWXpSaU1XSTJNV1k0T0NJc0luUjVjQ0k2SWtwWFZDSjkuZXlKcGMzTWlPaUpvZEhSd2N6b3ZMMmgxYjJkNmIyVnhlbU55WkhacmQzUjJiMlJwTG5OMWNHRmlZWE5sTG1OdkwyRjFkR2d2ZGpFaUxDSnpkV0lpT2lKak56bGpPREJpTkMxbE5tTXhMVFJrTmpndE9HUTBaUzFqWVRJMlpXSm1ZMlkxTmpNaUxDSmhkV1FpT2lKaGRYUm9aVzUwYVdOaGRHVmtJaXdpWlhod0lqb3hOemN6T0RJNU1UazVMQ0pwWVhRaU9qRTNOek00TWpVMU9Ua3NJbVZ0WVdsc0lqb2liV0ZuZVdGeVltRnliblZ6UUdkdFlXbHNMbU52YlNJc0luQm9iMjVsSWpvaUlpd2lZWEJ3WDIxbGRHRmtZWFJoSWpwN0luQnliM1pwWkdWeUlqb2laMjl2WjJ4bElpd2ljSEp2ZG1sa1pYSnpJanBiSW1kdmIyZHNaU0pkZlN3aWRYTmxjbDl0WlhSaFpHRjBZU0k2ZXlKaGRtRjBZWEpmZFhKc0lqb2lhSFIwY0hNNkx5OXNhRE11WjI5dloyeGxkWE5sY21OdmJuUmxiblF1WTI5dEwyRXZRVU5uT0c5alNtWkRWRmRWUWxwSVNHSlRZMHMwVmtjM1NrbERVM0p4Umw5bGJuWlhSelJFTjFkamNWaFBiREZyT1Zsc2NUZDJjVGc5Y3prMkxXTWlMQ0psYldGcGJDSTZJbTFoWjNsaGNtSmhjbTUxYzBCbmJXRnBiQzVqYjIwaUxDSmxiV0ZwYkY5MlpYSnBabWxsWkNJNmRISjFaU3dpWm5Wc2JGOXVZVzFsSWpvaVFtRnlibWtpTENKcFpDSTZJakF4T1dKaU5UTmtMVE5sT1dRdE4yTmtPQzA1TVRnNExUVmtZbUV4WXpnMk1tVTJOaUlzSW1semN5STZJbWgwZEhCek9pOHZZV05qYjNWdWRITXVaMjl2WjJ4bExtTnZiU0lzSW14aGMzUmZiR2x1YTJWa1gzTjFjR0ZpWVhObFgzVnpaWEpmYVdRaU9pSTVPR1V4WkRZd09TMWxObVF3TFRReFpESXRPV1ZrWXkxbVltUTJZMlEyTkRoaFpqQWlMQ0p1WVcxbElqb2lRbUZ5Ym1raUxDSndhRzl1WlY5MlpYSnBabWxsWkNJNlptRnNjMlVzSW5CcFkzUjFjbVVpT2lKb2RIUndjem92TDJ4b015NW5iMjluYkdWMWMyVnlZMjl1ZEdWdWRDNWpiMjB2WVM5QlEyYzRiMk5LWmtOVVYxVkNXa2hJWWxOalN6UldSemRLU1VOVGNuRkdYMlZ1ZGxkSE5FUTNWMk54V0U5c01XczVXV3h4TjNaeE9EMXpPVFl0WXlJc0luQnliM1pwWkdWeVgybGtJam9pTVRBNU5UWTVOamMzTVRRek5EWXdORGt6TURZNUlpd2ljM1ZpSWpvaU1UQTVOVFk1TmpjM01UUXpORFl3TkRrek1EWTVJbjBzSW5KdmJHVWlPaUpoZFhSb1pXNTBhV05oZEdWa0lpd2lZV0ZzSWpvaVlXRnNNU0lzSW1GdGNpSTZXM3NpYldWMGFHOWtJam9pYjJGMWRHZ2lMQ0owYVcxbGMzUmhiWEFpT2pFM056TTRNalUxT1RoOVhTd2ljMlZ6YzJsdmJsOXBaQ0k2SWpObE1HVTBOVGt6TFdOaVlqTXRORFl4TWkwNVlUYzBMVE5oWVRNNU5ESmhOV1UzWWlJc0ltbHpYMkZ1YjI1NWJXOTFjeUk2Wm1Gc2MyVjkuRklXby10QzQyenBubDAyLTBBQktjU1lpOEw5VFBwXzJmdm9MRmY5RnlMSVVKcDgxLWFjd045dV82YWVMTUx6Z1Ezb1lYYnB4Mnk4YVlXQ1h1dWhXM1EiLCJ0b2tlbl90eXBlIjoiYmVhcmVyIiwiZXhwaXJlc19pbiI6MzYwMCwiZXhwaXJlc19hdCI6MTc3MzgyOTE5OSwicmVmcmVzaF90b2tlbiI6IjRpb2R0ZHBwaXN6diIsInVzZXIiOnsiaWQiOiJjNzljODBiNC1lNmMxLTRkNjgtOGQ0ZS1jYTI2ZWJmY2Y1NjMiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwicm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJlbWFpbCI6Im1hZ3lhcmJhcm51c0BnbWFpbC5jb20iLCJlbWFpbF9jb25maXJtZWRfYXQiOiIyMDI2LTAxLTEzVDAyOjQ0OjI4LjA3NTA4NVoiLCJwaG9uZSI6IiIsImNvbmZpcm1lZF9hdCI6IjIwMjYtMDEtMTNUMDI6NDQ6MjguMDc1MDg1WiIsImxhc3Rfc2lnbl9pbl9hdCI6IjIwMjYtMDMtMThUMDk6MTk6NTguNjQwMjE5WiIsImFwcF9tZXRhZGF0YSI6eyJwcm92aWRlciI6Imdvb2dsZSIsInByb3ZpZGVycyI6WyJnb29nbGUiXX0sInVzZXJfbWV0YWRhdGEiOnsiYXZhdGFyX3VybCI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FDZzhvY0pmQ1RXVUJaSEhiU2NLNFZHN0pJQ1NycUZfZW52V0c0RDdXY3FYT2wxazlZbHE3dnE4PXM5Ni1jIiwiZW1haWwiOiJtYWd5YXJiYXJudXNAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImZ1bGxfbmFtZSI6IkJhcm5pIiwiaWQiOiIwMTliYjUzZC0zZTlkLTdjZDgtOTE4OC01ZGJhMWM4NjJlNjYiLCJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJsYXN0X2xpbmtlZF9zdXBhYmFzZV91c2VyX2lkIjoiOThlMWQ2MDktZTZkMC00MWQyLTllZGMtZmJkNmNkNjQ4YWYwIiwibmFtZSI6IkJhcm5pIiwicGhvbmVfdmVyaWZpZWQiOmZhbHNlLCJwaWN0dXJlIjoiaHR0c")
    config.setdefault("auth_tokens", [])
    config.setdefault("cf_clearance", "")
    config.setdefault("api_keys", [])
    config.setdefault("usage_stats", {})
    config.setdefault("prune_invalid_tokens", False)
    config.setdefault("persist_arena_auth_cookie", False)
    config.setdefault("camoufox_proxy_window_mode", constants.DEFAULT_CAMOUFOX_PROXY_WINDOW_MODE)
    config.setdefault("camoufox_fetch_window_mode", constants.DEFAULT_CAMOUFOX_FETCH_WINDOW_MODE)
    config.setdefault("chrome_fetch_window_mode", constants.DEFAULT_CHROME_FETCH_WINDOW_MODE)
    
    # Normalize api_keys
    if isinstance(config.get("api_keys"), list):
        normalized_keys = []
        for key_entry in config["api_keys"]:
            if isinstance(key_entry, dict):
                if "key" not in key_entry:
                    continue
                if "name" not in key_entry:
                    key_entry["name"] = "Unnamed Key"
                if "created" not in key_entry:
                    key_entry["created"] = 1704236400  # Default timestamp
                if "rpm" not in key_entry:
                    key_entry["rpm"] = constants.DEFAULT_RATE_LIMIT_RPM
                normalized_keys.append(key_entry)
        config["api_keys"] = normalized_keys


def save_config(config: dict, *, preserve_auth_tokens: bool = True) -> None:
    """
    Save configuration to file.
    
    Args:
        config: Configuration dictionary to save
        preserve_auth_tokens: If True, don't overwrite auth tokens from disk
    """
    try:
        if preserve_auth_tokens:
            try:
                with open(_current_config_file, "r") as f:
                    on_disk = json.load(f)
            except Exception:
                on_disk = None

            if isinstance(on_disk, dict):
                if "auth_tokens" in on_disk and isinstance(on_disk.get("auth_tokens"), list):
                    config["auth_tokens"] = list(on_disk.get("auth_tokens") or [])
                if "auth_token" in on_disk:
                    config["auth_token"] = str(on_disk.get("auth_token") or "")

        # usage_stats will be set by the caller
        
        tmp_path = f"{_current_config_file}.tmp"
        with open(tmp_path, "w") as f:
            json.dump(config, f, indent=4)
        os.replace(tmp_path, _current_config_file)
    except Exception as e:
        print(f"Error saving config: {e}")


# Global state storage (for cross-module state)
_global_state: Dict[str, Any] = {}


def _get_global_state() -> Dict[str, Any]:
    """Get the global state dictionary."""
    return _global_state


def set_global_state(key: str, value: Any) -> None:
    """Set a global state value."""
    _global_state[key] = value


def get_global_state(key: str, default: Any = None) -> Any:
    """Get a global state value."""
    return _global_state.get(key, default)


# === Model management ===

def get_models() -> list:
    """Load models from file."""
    try:
        with open(constants.MODELS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_models(models: list) -> None:
    """Save models to file."""
    try:
        tmp_path = f"{constants.MODELS_FILE}.tmp"
        with open(tmp_path, "w") as f:
            json.dump(models, f, indent=2)
        os.replace(tmp_path, constants.MODELS_FILE)
    except Exception as e:
        print(f"Error saving models: {e}")


# === Default config for startup ===

def get_default_config() -> dict:
    """Get default configuration values."""
    return {
        "password": "admin",
        "auth_token": "",
        "auth_tokens": [],
        "cf_clearance": "",
        "api_keys": [
            {
                "name": "Default Key",
                "key": "",  # Will be generated
                "rpm": constants.DEFAULT_RATE_LIMIT_RPM,
                "created": 0,
            }
        ],
        "usage_stats": {},
        "prune_invalid_tokens": False,
        "persist_arena_auth_cookie": False,
        "camoufox_proxy_window_mode": constants.DEFAULT_CAMOUFOX_PROXY_WINDOW_MODE,
        "camoufox_fetch_window_mode": constants.DEFAULT_CAMOUFOX_FETCH_WINDOW_MODE,
        "chrome_fetch_window_mode": constants.DEFAULT_CHROME_FETCH_WINDOW_MODE,
    }
