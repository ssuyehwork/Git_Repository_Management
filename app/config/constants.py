# -*- coding: utf-8 -*-
# app/config/constants.py
import os

# --- Core App Settings ---
APP_NAME = "智能开发工具套件"
APP_VERSION = "v3.1"

# --- Network Settings ---
SINGLE_INSTANCE_HOST = "127.0.0.1"
SINGLE_INSTANCE_PORT = 54321

# --- File Paths ---
# The main file for all user-configurable settings
SETTINGS_FILE = "app_settings.json"
# A separate file to track processed zip files for the sync feature
HISTORY_FILE = "processed_files.json"

# --- Default Paths (Windows specific) ---
USER_HOME = os.path.expanduser("~")
DOWNLOAD_FOLDER = os.path.join(USER_HOME, "Downloads")

# --- UI Colors ---
COLOR_ERROR_BG = "#8b0000"
COLOR_ERROR_FG = "#ffffff"
