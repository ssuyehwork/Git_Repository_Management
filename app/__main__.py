# app/__main__.py
"""
应用程序包的主入口点。
允许通过 `python -m app` 运行。
"""
import sys
from app.app_instance import AppInstance

def main():
    """主函数"""
    app_instance = AppInstance()
    sys.exit(app_instance.run())

if __name__ == "__main__":
    main()
