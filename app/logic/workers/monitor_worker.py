# -*- coding: utf-8 -*-
# app/workers/monitor_worker.py
import os
import time
from PyQt6.QtCore import QThread, pyqtSignal
from app.config import constants
from app.config.storage import JsonStorage
from app.utils.file_manager import FileManager

class MonitorThread(QThread):
    new_file_detected = pyqtSignal(list)
    log_signal = pyqtSignal(str, bool)
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.known_files = set()
    
    def stop(self):
        self.running = False
    
    def run(self):
        self.log_signal.emit("🔍 实时监控已启动，等待新文件下载...", False)
        
        history = JsonStorage.load_history()
        self.known_files = set(history)
        
        while self.running:
            try:
                current_files = FileManager.scan_zip_files(constants.DOWNLOAD_FOLDER)
                current_set = set(current_files)
                new_files = current_set - self.known_files
                
                if new_files:
                    new_list = list(new_files)
                    self.log_signal.emit(f"⚡ 检测到新下载: {os.path.basename(new_list[0])}", False)
                    self.new_file_detected.emit(new_list)
                    self.known_files.update(new_files)
                
                time.sleep(2)
            except Exception as e:
                self.log_signal.emit(f"监控异常: {str(e)}", True)
                time.sleep(5)
