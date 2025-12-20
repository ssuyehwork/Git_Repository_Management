# -*- coding: utf-8 -*-
# app/data/storage.py
import json
import os
from app.config import constants

class JsonStorage:
    """通用 JSON 存取类"""

    @staticmethod
    def _load(filepath, default_value):
        if not os.path.exists(filepath):
            return default_value
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default_value

    @staticmethod
    def _save(filepath, data):
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

    # --- 具体业务存储 ---

    @classmethod
    def load_groups(cls):
        return cls._load(constants.CONFIG_FILE, {})

    @classmethod
    def save_groups(cls, groups):
        cls._save(constants.CONFIG_FILE, groups)

    @classmethod
    def load_history(cls):
        return cls._load(constants.HISTORY_FILE, [])

    @classmethod
    def save_history(cls, history):
        cls._save(constants.HISTORY_FILE, history)

    @classmethod
    def load_main_program_path(cls):
        data = cls._load(constants.MAIN_PROGRAM_FILE, {})
        return data.get("path", "")

    @classmethod
    def save_main_program_path(cls, path):
        cls._save(constants.MAIN_PROGRAM_FILE, {"path": path})

    @classmethod
    def load_window_size(cls):
        return cls._load(constants.WINDOW_SIZE_FILE, None)

    @classmethod
    def save_window_size(cls, width, height):
        cls._save(constants.WINDOW_SIZE_FILE, {"width": width, "height": height})

    @classmethod
    def load_last_selected_group(cls):
        data = cls._load(constants.LAST_SELECTED_GROUP_FILE, {})
        return data.get("last_selected", "")

    @classmethod
    def save_last_selected_group(cls, group_name):
        cls._save(constants.LAST_SELECTED_GROUP_FILE, {"last_selected": group_name})

    @classmethod
    def load_last_source_folder(cls):
        data = cls._load(constants.LAST_SOURCE_FOLDER_FILE, {})
        return data.get("path", "")

    @classmethod
    def save_last_source_folder(cls, path):
        cls._save(constants.LAST_SOURCE_FOLDER_FILE, {"path": path})

    @classmethod
    def load_last_extract_path(cls):
        data = cls._load(constants.LAST_EXTRACT_PATH_FILE, {})
        return data.get("path", "")

    @classmethod
    def save_last_extract_path(cls, path):
        cls._save(constants.LAST_EXTRACT_PATH_FILE, {"path": path})
