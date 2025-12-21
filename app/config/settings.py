# app/config/settings.py
"""
集中管理应用程序的所有配置和常量。
"""

import sys
from pathlib import Path

# ================================
# 应用程序元数据
# ================================
APP_NAME = "GitHub 仓库智能管理器"
APP_VERSION = "v2.0 Professional"
WINDOW_TITLE = f"{APP_NAME} {APP_VERSION}"

# ================================
# 路径配置
# ================================
# 主配置文件路径，存储在用户主目录下
CONFIG_FILE_PATH = Path.home() / ".github_manager_config.json"

# 默认仓库路径 (如果配置文件不存在)
DEFAULT_LOCAL_PATH = r"G:\PYthon\GitHub 仓库管理\GitHub 仓库管理"
DEFAULT_REMOTE_URL = "https://github.com/ssuyehwork/Syn_Github_Upload.git"

# ================================
# 依赖项配置
# ================================
# 需要检查和安装的PyPI包
REQUIRED_PACKAGES = {
    'PyQt6': 'PyQt6',
    'PyQt6.QtWidgets': 'PyQt6',
    'PyQt6.QtCore': 'PyQt6',
    'PyQt6.QtGui': 'PyQt6'
}

# ================================
# UI 尺寸与几何
# ================================
WINDOW_DEFAULT_WIDTH = 1100
WINDOW_DEFAULT_HEIGHT = 750
WINDOW_MIN_WIDTH_LEFT_PANEL = 550

SPLASH_WIDTH = 600
SPLASH_HEIGHT = 400

# ================================
# 颜色与样式
# ================================
class Colors:
    """定义UI中使用的所有颜色"""
    # 背景色
    PRIMARY_BACKGROUND = "#0f172a"
    SECONDARY_BACKGROUND = "#1e293b"
    TERTIARY_BACKGROUND = "#334155"
    INPUT_BACKGROUND = "#334155"
    INPUT_FOCUS_BACKGROUND = "#3f4d63"
    LOG_BACKGROUND = "#0f172a"
    PROGRESS_BAR_BACKGROUND = "#1f2937"

    # 文本颜色
    PRIMARY_TEXT = "#f1f5f9"
    SECONDARY_TEXT = "#cbd5e1"
    PLACEHOLDER_TEXT = "#64748b"
    STATUS_BAR_TEXT = "#10b981"
    LOG_TIMESTAMP_TEXT = "#64748b"

    # 边框与分隔线
    BORDER_PRIMARY = "#334155"
    BORDER_SECONDARY = "#475569"
    BORDER_FOCUS = "#6366f1"

    # 品牌与高亮色
    BRAND_PRIMARY_START = "#6366f1"
    BRAND_PRIMARY_END = "#8b5cf6"
    HIGHLIGHT = "#6366f1"

    # 按钮颜色
    BUTTON_NORMAL = "#475569"
    BUTTON_HOVER = "#64748b"
    BUTTON_PRESSED = "#334155"
    BUTTON_DISABLED_BG = "#334155"
    BUTTON_DISABLED_TEXT = "#64748b"

    # 功能性颜色
    SUCCESS = "#10b981"
    SUCCESS_DARK = "#059669"
    INFO = "#3b82f6"
    WARNING = "#f59e0b"
    ERROR = "#ef4444"
    SPECIAL = "#06b6d4"

# 日志消息类型对应的颜色
LOG_COLORS = {
    "info": Colors.INFO,
    "success": Colors.SUCCESS,
    "warning": Colors.WARNING,
    "error": Colors.ERROR
}

# ================================
# UI 字符串常量
# ================================
# --- 标题栏 ---
TITLE_VIEW_TEXT = f"🚀 {APP_NAME}"

# --- 配置区 ---
CONFIG_GROUP_TITLE = "⚙ 仓库配置"
CONFIG_LABELS = {
    "local_path": "📁 本地路径:",
    "remote_url": "🌐 远程仓库:",
    "username": "👤 用户名:",
    "email": "📧 邮箱:",
}
CONFIG_PLACEHOLDERS = {
    "local_path": "例如: G:\\PYthon\\GitHub 仓库管理",
    "remote_url": "https://github.com/username/repo.git",
    "username": "Git用户名 (可选)",
    "email": "Git邮箱 (可选)",
}
CONFIG_BUTTONS = {
    "browse": "📂 浏览",
    "save": "💾 保存配置",
    "refresh": "🔄 刷新状态",
}

# --- 状态区 ---
STATUS_GROUP_TITLE = "📊 仓库状态"
STATUS_ITEMS = {
    "branch": {"title": "🌿 分支", "color": Colors.SUCCESS},
    "uncommitted": {"title": "📝 未提交", "color": Colors.WARNING},
    "unpushed": {"title": "📤 未推送", "color": Colors.INFO},
    "sync": {"title": "🔗 状态", "color": Colors.BRAND_PRIMARY_END},
}
STATUS_DEFAULT_VALUE = "--"
STATUS_STATE_CONNECTED = "✓ 已连接"
STATUS_STATE_LOCAL = "本地仓库"
STATUS_STATE_UNCONFIGURED = "未配置"
STATUS_STATE_UNINITIALIZED = "未初始化"
STATUS_STATE_ERROR = "检查失败"

# --- 操作区 ---
OPERATIONS_GROUP_TITLE = "🎯 智能操作"
OPERATIONS_BUTTONS = [
    {"id": "upload", "text": "📤 智能上传", "tooltip": "自动检测并上传更改", "color": Colors.SUCCESS},
    {"id": "download", "text": "📥 智能下载", "tooltip": "拉取远程最新更新", "color": Colors.INFO},
    {"id": "sync", "text": "🔄 智能同步", "tooltip": "双向同步本地与远程", "color": Colors.BRAND_PRIMARY_END},
    {"id": "overwrite", "text": "⚡ 强制覆盖", "tooltip": "用本地强制覆盖远程", "color": Colors.WARNING},
    {"id": "delete", "text": "🗑 清理远程", "tooltip": "删除远程所有文件", "color": Colors.ERROR},
    {"id": "init", "text": "🔧 初始化", "tooltip": "初始化Git仓库", "color": Colors.SPECIAL},
]

# --- 日志区 ---
LOG_GROUP_TITLE = "📋 操作日志"
LOG_CLEAR_BUTTON_TEXT = "🧹 清空日志"

# --- 状态栏 ---
STATUS_BAR_READY = "就绪"

# --- 弹窗消息 ---
MSG_GIT_NOT_FOUND_TITLE = "Git未安装"
MSG_GIT_NOT_FOUND_TEXT = "未检测到Git!\\n\\n请先安装Git:\\nhttps://git-scm.com/downloads"
MSG_SAVE_CONFIG_SUCCESS = "配置已保存!"
MSG_CONFIG_WARN_TITLE = "警告"
MSG_CONFIG_WARN_NO_LOCAL_PATH = "请填写本地路径!"
MSG_CONFIG_WARN_NO_REMOTE_URL = "请填写远程仓库URL!"

# --- 危险操作确认 ---
CONFIRM_SYNC_TITLE = "确认操作"
CONFIRM_SYNC_TEXT = ("将执行双向同步操作:\\n\\n"
                   "1. 保存本地更改\\n"
                   "2. 拉取远程更新\\n"
                   "3. 推送到远程\\n\\n"
                   "确定继续吗?")
CONFIRM_OVERWRITE_TITLE = "⚠ 警告: 强制覆盖操作"
CONFIRM_OVERWRITE_TEXT = ("这将用本地版本强制覆盖远程仓库!\\n"
                        "远程的更改将永久丢失!\\n\\n"
                        "确定要继续吗?")
CONFIRM_DELETE_TITLE = "⚠ 危险操作"
CONFIRM_DELETE_TEXT = "这将删除远程仓库的所有文件!\\n此操作不可恢复!\\n\\n请输入 'DELETE' 确认:"
CONFIRM_DELETE_INPUT_PROMPT = "请输入 'DELETE' 确认删除:"
CONFIRM_DELETE_INPUT_KEYWORD = "DELETE"
