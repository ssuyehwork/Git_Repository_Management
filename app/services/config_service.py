import json
from pathlib import Path

class ConfigService:
    """负责所有与配置文件相关的操作"""

    def __init__(self, config_filename=".github_manager_config.json"):
        self.config_file = Path.home() / config_filename
        self.profiles = {}
        self.last_profile_name = None
        self.load_config()

    def load_config(self):
        """
        从JSON文件加载配置。
        如果文件不存在，则创建默认配置。
        如果文件是旧格式，则自动迁移。
        """
        try:
            if not self.config_file.exists():
                self._create_default_config()
                return

            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            if 'local_path' in config:  # Legacy format detection
                self._migrate_legacy_config(config)
            else:
                self.profiles = config.get('profiles', {})
                self.last_profile_name = config.get('last_profile')
        except Exception as e:
            print(f"Error loading config: {e}")
            self._create_default_config()

    def get_all_profiles(self):
        """返回所有配置方案"""
        return self.profiles

    def get_last_profile_name(self):
        """返回上次使用的配置方案名称"""
        if self.last_profile_name in self.profiles:
            return self.last_profile_name
        elif self.profiles:
            return list(self.profiles.keys())[0]
        return None

    def get_profile(self, name):
        """根据名称获取单个配置方案"""
        return self.profiles.get(name)

    def save_profile(self, name, data):
        """
        保存（新建或更新）一个配置方案。
        """
        if not data.get('local_path') or not data.get('remote_url'):
            raise ValueError("本地路径和远程URL不能为空")

        self.profiles[name] = data
        self.last_profile_name = name
        self._save_to_file()

    def delete_profile(self, name):
        """删除一个配置方案"""
        if name in self.profiles:
            if len(self.profiles) <= 1:
                raise ValueError("不能删除最后一个配置方案")
            del self.profiles[name]
            self.last_profile_name = list(self.profiles.keys())[0]
            self._save_to_file()
            return True
        return False

    def _save_to_file(self):
        """将当前配置数据写入JSON文件"""
        config_data = {
            'profiles': self.profiles,
            'last_profile': self.last_profile_name
        }
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)

    def _create_default_config(self):
        """创建一套默认配置"""
        self.profiles = {
            "默认配置": {
                'local_path': '',
                'remote_url': '',
                'username': '',
                'email': ''
            }
        }
        self.last_profile_name = "默认配置"
        self._save_to_file()

    def _migrate_legacy_config(self, legacy_config):
        """将旧的单层配置格式迁移到新的多方案格式"""
        self.profiles = {"默认配置": legacy_config}
        self.last_profile_name = "默认配置"
        self._save_to_file()
