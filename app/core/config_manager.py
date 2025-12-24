import json
from pathlib import Path

class ConfigManager:
    """负责应用程序的配置管理"""

    def __init__(self, config_file=None):
        if config_file:
            self.config_file = Path(config_file)
        else:
            self.config_file = Path.home() / ".github_manager_config.json"

    def load_config(self):
        """
        加载配置. 如果配置文件不存在, 返回一个包含默认值的字典.
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 确保所有键都存在
                    config.setdefault('local_path', '')
                    config.setdefault('remote_url', '')
                    config.setdefault('username', '')
                    config.setdefault('email', '')
                    return config
            except (json.JSONDecodeError, IOError) as e:
                print(f"警告: 无法加载配置文件 {self.config_file}. 错误: {e}")
                # 如果文件损坏，返回默认值
                return self.get_default_config()
        else:
            return self.get_default_config()

    def save_config(self, config_data):
        """
        将配置保存到文件.
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            return True, "配置已成功保存"
        except IOError as e:
            error_message = f"保存配置失败: {e}"
            print(f"错误: {error_message}")
            return False, error_message

    @staticmethod
    def get_default_config():
        """
        返回默认配置.
        """
        return {
            'local_path': "",
            'remote_url': "https://github.com/ssuyehwork/Syn_Github_Upload.git",
            'username': '',
            'email': ''
        }
