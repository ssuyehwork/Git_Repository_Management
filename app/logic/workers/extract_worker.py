# -*- coding: utf-8 -*-
# app/workers/extract_worker.py
import os
import shutil
from PyQt6.QtCore import QThread, pyqtSignal
from app.utils.file_manager import FileManager
from app.config.storage import JsonStorage

class ExtractThread(QThread):
    log_signal = pyqtSignal(str, bool)
    finished_signal = pyqtSignal(str)

    def __init__(self, new_files, extract_base_path):
        super().__init__()
        self.new_files = new_files
        self.extract_base_path = extract_base_path

    def run(self):
        if not self.new_files:
            return

        zip_path = self.new_files[0]
        zip_name = os.path.basename(zip_path)
        self.log_signal.emit(f"发现新文件: {zip_name}", False)

        try:
            os.makedirs(self.extract_base_path, exist_ok=True)
            next_num = FileManager.get_next_jules_number(self.extract_base_path)
            new_folder_name = f"jules_{next_num}"
            new_folder_path = os.path.join(self.extract_base_path, new_folder_name)
            os.makedirs(new_folder_path, exist_ok=True)

            self.log_signal.emit(f"创建文件夹: {new_folder_name}", False)

            dest_zip = os.path.join(new_folder_path, zip_name)
            shutil.copy2(zip_path, dest_zip)
            self.log_signal.emit(f"复制压缩文件到: {new_folder_path}", False)

            self.log_signal.emit("正在解压...", False)
            success, result = FileManager.extract_zip(dest_zip, new_folder_path)

            if success:
                file_list = result
                self.log_signal.emit("✅ 解压完成", False)
                if file_list:
                    self.log_signal.emit(f"解压了 {len(file_list)} 个文件:", False)
                    for filename in file_list:
                        self.log_signal.emit(f"  - {filename}", False)

                try:
                    os.remove(dest_zip)
                    self.log_signal.emit(f"✅ 已删除压缩文件: {zip_name}", False)
                except Exception as e:
                    self.log_signal.emit(f"⚠️ 删除压缩文件失败: {str(e)}", True)

                history = JsonStorage.load_history()
                if zip_path not in history:
                    history.append(zip_path)
                    JsonStorage.save_history(history)

                self.finished_signal.emit(new_folder_path)
            else:
                self.log_signal.emit(f"❌ 解压失败: {result}", True)
                self.finished_signal.emit("")

        except Exception as e:
            self.log_signal.emit(f"❌ 处理失败: {str(e)}", True)
            self.finished_signal.emit("")
