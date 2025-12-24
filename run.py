import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# 在导入应用程序模块之前，先进行依赖检查
# 这确保了即使缺少PyQt6，检查逻辑也能运行
from app.utils.dependency_manager import DependencyManager

# 执行依赖检查
# 如果检查失败或需要安装，DependencyManager内部会处理或退出
# 在开始GUI之前完成所有命令行打印
if not DependencyManager.check_and_install():
    # 如果有严重的安装问题，check_and_install 内部会 sys.exit
    # 但为保险起见，这里也加上退出逻辑
    sys.exit(1)

# 依赖检查通过后，再导入其他模块
from app.ui.main_window import GitHubManager
from app.ui.splash_screen import create_splash_screen

def main():
    """
    应用程序主入口函数.
    负责初始化、创建和显示UI组件.
    """
    # 1. 创建 QApplication 实例
    app = QApplication(sys.argv)

    # 注意: 全局样式现在在 MainWindow 的构造函数中通过 setStyleSheet 设置
    # 这样可以确保样式与窗口实例绑定，而不是全局应用状态

    # 2. 创建并显示启动画面
    splash = create_splash_screen()
    splash.show()

    # 强制处理事件，以确保启动画面被正确绘制
    app.processEvents()

    # 3. 创建主窗口实例
    # 主窗口的构造函数中已经包含了样式表的设置
    window = GitHubManager()

    # 4. 设置一个定时器，在短暂延迟后关闭启动画面并显示主窗口
    # 这给用户一种“正在加载”的感觉，提升了体验
    close_splash_timer = QTimer()
    close_splash_timer.setSingleShot(True)
    # 当定时器触发时，关闭splash并显示window
    close_splash_timer.timeout.connect(splash.close)
    close_splash_timer.timeout.connect(window.show)
    close_splash_timer.start(1500) # 1.5秒后执行

    # 5. 启动应用程序的事件循环
    sys.exit(app.exec())


if __name__ == '__main__':
    # 确保 main 函数是程序执行的起点
    main()
