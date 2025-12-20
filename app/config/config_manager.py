"""
配置管理
"""
import json
from pathlib import Path
from PyQt6.QtWidgets import QFileDialog, QMessageBox

class ConfigManager:
    """负责加载和保存配置文件"""
    
    def __init__(self, parent=None):
        self.parent = parent

    def load_config(self):
        """弹出文件选择框来加载配置"""
        try:
            filepath, _ = QFileDialog.getOpenFileName(
                self.parent,
                "选择配置文件",
                "",
                "JSON 文件 (*.json)"
            )

            if filepath:
                with open(filepath, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                QMessageBox.information(self.parent, "成功", "配置文件加载成功!")
                return config, Path(filepath).name
        except Exception as e:
            QMessageBox.critical(self.parent, "错误", f"加载配置失败:\n{str(e)}")
        
        return None, None

    def save_config(self, config_data):
        """弹出文件另存为框来保存配置"""
        try:
            if not config_data.get('local_path'):
                QMessageBox.warning(self.parent, "警告", "请填写本地路径!")
                return False, None
            
            if not config_data.get('remote_url'):
                QMessageBox.warning(self.parent, "警告", "请填写远程仓库URL!")
                return False, None

            filepath, _ = QFileDialog.getSaveFileName(
                self.parent,
                "保存配置文件",
                "",
                "JSON 文件 (*.json)"
            )

            if filepath:
                if not filepath.endswith('.json'):
                    filepath += '.json'
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, indent=4, ensure_ascii=False)
                
                QMessageBox.information(self.parent, "成功", "配置文件已成功保存!")
                return True, Path(filepath).name
        except Exception as e:
            QMessageBox.critical(self.parent, "错误", f"保存配置失败:\n{str(e)}")
            
        return False, None
