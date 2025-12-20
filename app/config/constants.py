# -*- coding: utf-8 -*-
# app/config/constants.py
import os

# 网络配置
SINGLE_INSTANCE_HOST = "127.0.0.1"
SINGLE_INSTANCE_PORT = 54321

# 文件路径配置
CONFIG_FILE = "path_groups.json"
HISTORY_FILE = "processed_files.json"
MAIN_PROGRAM_FILE = "main_program_path.json"
WINDOW_SIZE_FILE = "window_size.json"
LAST_SELECTED_GROUP_FILE = "last_selected_group.json"
LAST_SOURCE_FOLDER_FILE = "last_source_folder.json"
LAST_EXTRACT_PATH_FILE = "last_extract_path.json"

# 默认文件夹路径 (Windows 环境)
USER_HOME = os.path.expanduser("~")
DOWNLOAD_FOLDER = os.path.join(USER_HOME, "Downloads")

# 颜色配置
COLOR_ERROR_BG = "#8b0000"
COLOR_ERROR_FG = "#ffffff"
