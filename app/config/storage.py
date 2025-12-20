# -*- coding: utf-8 -*-
# app/config/storage.py
import json
import os
from app.config import constants

class JsonStorage:
    """
    通用 JSON 存取类.
    - 应用设置集中在 app_settings.json
    - 处理历史独立于 processed_files.json
    """

    @staticmethod
    def _load(filepath, default_value):
        """私有加载帮助程序"""
        if not os.path.exists(filepath):
            return default_value
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return default_value

    @staticmethod
    def _save(filepath, data):
        """私有保存帮助程序"""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except IOError:
            return False

    # --- Application Settings ---

    @classmethod
    def load_settings(cls):
        """加载所有应用设置从一个统一的文件"""
        default_settings = {
            "git_settings": {
                "local_path": "",
                "remote_url": "",
                "username": "",
                "email": ""
            },
            "sync_settings": {
                "extract_path": constants.DOWNLOAD_FOLDER,
                "source_path": "",
                "target_path": "",
                "main_program_path": "",
                "path_groups": {},
                "last_selected_group": ""
            },
            "window_size": {
                "width": 1100,
                "height": 800
            }
        }
        return cls._load(constants.SETTINGS_FILE, default_settings)

    @classmethod
    def save_settings(cls, settings):
        """保存所有应用设置到一个统一的文件"""
        return cls._save(constants.SETTINGS_FILE, settings)

    # --- Sync History (Separate concern) ---

    @classmethod
    def load_history(cls):
        """加载已处理的文件历史"""
        return cls._load(constants.HISTORY_FILE, [])

    @classmethod
    def save_history(cls, history):
        """保存已处理的文件历史"""
        return cls._save(constants.HISTORY_FILE, history)
