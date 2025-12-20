# core/script_runner.py
import sys
import subprocess
from PyQt5.QtCore import QThread, pyqtSignal
from utils.decoding import decode_bytes

class ScriptRunner(QThread):
    """在单独的线程中运行Python脚本，并发出输出信号。"""
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, script_path, parent=None):
        super().__init__(parent)
        self.script_path = script_path

    def run(self):
        """执行脚本子进程并实时捕获其输出。"""
        try:
            self.output_signal.emit(f"[启动] {self.script_path}\n")
            
            process = subprocess.Popen(
                [sys.executable, self.script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1, # 行缓冲
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )

            # 实时读取标准输出
            if process.stdout:
                for line in iter(process.stdout.readline, b''):
                    decoded_line = decode_bytes(line)
                    self.output_signal.emit(decoded_line)
            
            # 等待进程结束并读取标准错误
            process.wait()
            stderr_bytes = process.stderr.read() if process.stderr else b""

            if stderr_bytes:
                decoded_err = decode_bytes(stderr_bytes)
                self.output_signal.emit(f"[错误]\n{decoded_err}\n")

            self.output_signal.emit(f"[完成] 退出码: {process.returncode}\n")

        except FileNotFoundError:
            self.output_signal.emit(f"[异常] 文件未找到: {self.script_path}\n")
        except Exception as e:
            self.output_signal.emit(f"[异常] {str(e)}\n")
        finally:
            self.finished_signal.emit()
