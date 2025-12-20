# main.py
import sys
from PyQt5.QtWidgets import QApplication

from config import DATABASE_FILE
from data.database import DatabaseManager
from core.app_logic import AppLogic
from ui.main_window import PyLauncherApp

def main():
    """
    应用程序主入口。
    负责初始化和组装各个模块（数据、逻辑、UI），然后启动应用。
    """
    # 1. 创建Qt应用程序实例
    app = QApplication(sys.argv)

    # 2. 初始化数据访问层
    db_manager = DatabaseManager(DATABASE_FILE)

    # 3. 初始化核心业务逻辑层，并注入数据访问层的依赖
    app_logic = AppLogic(db_manager)

    # 4. 初始化UI层，并注入业务逻辑层的依赖
    window = PyLauncherApp(app_logic)
    
    # 5. 显示主窗口
    window.show()

    # 6. 设置程序退出时的清理工作
    app.aboutToQuit.connect(db_manager.close)
    
    # 7. 启动应用程序事件循环
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
