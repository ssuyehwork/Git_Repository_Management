# -*- coding: utf-8 -*-
# app/workers/launcher_worker.py
from PyQt6.QtCore import QThread, pyqtSignal
from app.utils.process_runner import ProcessRunner

class LauncherThread(QThread):
    output_signal = pyqtSignal(str)

    def __init__(self, program_path):
        super().__init__()
        self.program_path = program_path
        self.process = None
        self.running = True

    def run(self):
        try:
            cmd, work_dir = ProcessRunner.prepare_command(self.program_path)
            self.process = ProcessRunner.create_process(cmd, work_dir)

            if self.process.stdout:
                for line in self.process.stdout:
                    if not self.running:
                        break
                    self.output_signal.emit(line.strip())

            self.process.wait()
            self.output_signal.emit(f"🏁 主程序已退出 (代码: {self.process.returncode})")

        except Exception as e:
            self.output_signal.emit(f"❌ 启动/运行出错: {str(e)}")

    def stop(self):
        self.running = False
        if self.process:
            try:
                self.process.terminate()
            except:
                pass
