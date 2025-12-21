# app/services/config_service.py
"""
服务层，负责应用程序的数据持久化，例如读写配置文件。
"""
import json
from app.config import settings

class ConfigService:
    """
    负责处理 JSON 配置文件的读取和写入。
    这是一个静态类，不应被实例化。
    """

    @staticmethod
    def load_config():
        """
        从 JSON 文件加载配置。
        如果文件不存在或内容损坏，则返回默认配置。
        """
        try:
            if settings.CONFIG_FILE_PATH.exists():
                with open(settings.CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 简单验证一下格式
                    if isinstance(config, dict):
                        return config
        except (IOError, json.JSONDecodeError):
            # 如果文件读取或解析失败，则返回默认值
            pass

        # 返回默认配置
        return {
            'local_path': settings.DEFAULT_LOCAL_PATH,
            'remote_url': settings.DEFAULT_REMOTE_URL,
            'username': '',
            'email': ''
        }

    @staticmethod
    def save_config(config_data):
        """
        将配置数据保存到 JSON 文件。

        :param config_data: 包含配置的字典。
        :return: (bool, str) 元组，表示成功状态和消息。
        """
        try:
            # 确保 config_data 是字典
            if not isinstance(config_data, dict):
                raise TypeError("配置数据必须是字典")

            with open(settings.CONFIG_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            return True, "配置已成功保存"
        except (IOError, TypeError) as e:
            return False, f"保存配置失败: {str(e)}"
