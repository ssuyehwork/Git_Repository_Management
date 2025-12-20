# -*- coding: utf-8 -*-
# app/core/process_runner.py
import os
import sys
import subprocess

class ProcessRunner:
    @staticmethod
    def prepare_command(program_path):
        """根据文件类型准备启动命令"""
        if not os.path.exists(program_path):
            raise FileNotFoundError(f"主程序不存在: {program_path}")

        work_dir = os.path.dirname(program_path)
        _, ext = os.path.splitext(program_path)
        ext = ext.lower()

        cmd = []
        
        if ext == '.py':
            cmd = [sys.executable, '-u', program_path]
        elif ext == '.pyw':
            pyw_exe = sys.executable.replace("python.exe", "pythonw.exe")
            if os.path.exists(pyw_exe):
                cmd = [pyw_exe, '-u', program_path]
            else:
                cmd = [sys.executable, '-u', program_path]
        else:
            # .exe, .bat, .cmd 等
            cmd = [program_path]
            
        return cmd, work_dir

    @staticmethod
    def create_process(cmd, work_dir):
        """创建子进程对象（带管道重定向）"""
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

        process = subprocess.Popen(
            cmd,
            cwd=work_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            text=True,
            bufsize=1,
            encoding='utf-8',
            errors='replace',
            startupinfo=startupinfo
        )
        return process
