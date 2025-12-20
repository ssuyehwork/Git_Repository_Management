# -*- coding: utf-8 -*-
# app/core/instance_lock.py
import socket
import threading
from app.config import constants

class SingleInstanceManager:
    def __init__(self, on_exit_callback=None):
        self.host = constants.SINGLE_INSTANCE_HOST
        self.port = constants.SINGLE_INSTANCE_PORT
        self.on_exit_callback = on_exit_callback
        self.server_socket = None
        self.thread = None

    def try_start_server(self):
        """尝试绑定端口，成功则为主实例"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((self.host, self.port))
            s.listen(1)
        except OSError:
            s.close()
            return False

        self.server_socket = s
        self.thread = threading.Thread(target=self._server_loop, daemon=True)
        self.thread.start()
        return True

    def _server_loop(self):
        """监听退出指令"""
        while True:
            try:
                conn, _ = self.server_socket.accept()
            except OSError:
                break
            try:
                data = conn.recv(1024)
                if not data:
                    conn.close()
                    continue
                cmd = data.decode("utf-8", errors="ignore").strip()
                if cmd == "EXIT":
                    if self.on_exit_callback:
                        self.on_exit_callback()
                    conn.close()
                    break
            except Exception:
                conn.close()
                break
        try:
            self.server_socket.close()
        except Exception:
            pass

    @classmethod
    def notify_existing_instance_to_exit(cls, timeout=1.0):
        """通知旧实例退出"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            s.connect((constants.SINGLE_INSTANCE_HOST, constants.SINGLE_INSTANCE_PORT))
            s.sendall(b"EXIT")
            s.close()
        except Exception:
            pass
