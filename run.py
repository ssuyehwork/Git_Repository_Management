# run.py
"""
项目根目录的启动脚本。
提供一个简单的方式来运行应用程序。
"""
import sys
from app.app_instance import AppInstance

def main():
    """主函数"""
    app_instance = AppInstance()
    sys.exit(app_instance.run())

if __name__ == "__main__":
    main()
