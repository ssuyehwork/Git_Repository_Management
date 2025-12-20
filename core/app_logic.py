# core/app_logic.py
import os
import sys
import subprocess
import difflib
from PyQt5.QtCore import QObject, pyqtSignal

from core.script_runner import ScriptRunner

class AppLogic(QObject):
    """
    处理应用程序核心业务逻辑，独立于UI。
    负责脚本管理、搜索、分组和执行。
    """
    # Signals to notify the UI of changes
    scripts_updated = pyqtSignal(list)
    groups_updated = pyqtSignal(dict, list) # dict for tree, list for expansion state
    log_message = pyqtSignal(str)
    script_finished = pyqtSignal()

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.runner = None
        self.current_group_id = None
        
    def load_initial_data(self):
        """加载并发送初始数据到UI。"""
        self.refresh_groups()
        # 默认加载所有脚本
        all_scripts = self.db_manager.get_all_scripts()
        self.scripts_updated.emit(all_scripts)

    def filter_scripts_by_group(self, group_id):
        """根据选择的分组ID筛选脚本。"""
        self.current_group_id = group_id
        if group_id == "FIXED_RECENT":
            scripts = self.db_manager.get_recent_scripts()
        else:
            scripts = self.db_manager.get_scripts_in_group(group_id)
        
        group_details = self.db_manager.get_group_details(group_id) if group_id != "FIXED_RECENT" else ("最近使用",)
        group_name = group_details[0] if group_details else "未知分组"
        
        self.log_message.emit(f"[过滤] 显示分组 '{group_name}' 中的 {len(scripts)} 个脚本\n")
        self.scripts_updated.emit(scripts)

    def search_scripts(self, text):
        """根据输入文本搜索脚本。"""
        text = text.strip().lower()
        if not text:
            # 如果搜索文本为空，则重新加载当前分组的脚本
            if self.current_group_id:
                self.filter_scripts_by_group(self.current_group_id)
            else: # Fallback to all scripts
                all_scripts = self.db_manager.get_all_scripts()
                self.scripts_updated.emit(all_scripts)
            return

        # 1. 尝试直接的 LIKE 匹配
        results = self.db_manager.search_scripts(text)
        
        # 2. 如果 LIKE 匹配结果为空，则在所有脚本上进行模糊匹配
        all_rows = results if results else self.db_manager.get_all_scripts()
        
        # 3. 计算得分并排序
        scored_results = []
        for r_id, name, path, rating in all_rows:
            score = self._calculate_fuzzy_score(text, name, path, rating)
            if score > 0.3: # 仅包括有一定相关性的结果
                scored_results.append((score, (r_id, name, path, rating)))
        
        scored_results.sort(key=lambda x: x[0], reverse=True)
        final_results = [item for score, item in scored_results]
        self.scripts_updated.emit(final_results)

    def _calculate_fuzzy_score(self, text, name, path, rating):
        """计算单个脚本的模糊匹配得分。"""
        name_lower = (name or "").lower()
        path_lower = (path or "").lower()
        score = 0.0

        if text in name_lower:
            score += 2.0
        if text in path_lower:
            score += 1.5
        
        # 相似度得分
        name_ratio = difflib.SequenceMatcher(None, text, name_lower).ratio()
        path_ratio = difflib.SequenceMatcher(None, text, path_lower).ratio()
        score += max(name_ratio, path_ratio)

        # 评级加分
        score += (rating or 0) * 0.1
        return score

    def run_script(self, path, launcher_path):
        """运行指定的脚本。"""
        if not path:
            return

        if self.runner and self.runner.isRunning():
            self.log_message.emit("[警告] 已有脚本正在运行\n")
            return

        # 检查路径是否存在
        if not os.path.exists(path):
            self.log_message.emit(f"[系统日志] 警告：路径无效，正在从数据库删除该条目: {path}\n")
            self.db_manager.delete_script_by_path(path)
            self.refresh_groups() # 刷新分组计数
            self.filter_scripts_by_group(self.current_group_id) # 刷新当前视图
            return

        # 防止运行启动器自身
        if os.path.abspath(launcher_path) == os.path.abspath(path):
            self.log_message.emit("[安全] 检测到尝试运行启动器自身，已阻止以避免嵌套实例。\n")
            return
            
        # 更新运行时间
        base_name = os.path.basename(path)
        self.db_manager.update_script_last_run(path, base_name)

        # 启动脚本
        self.runner = ScriptRunner(path)
        self.runner.output_signal.connect(self.log_message.emit)
        self.runner.finished_signal.connect(self._on_script_finished)
        self.runner.start()

    def _on_script_finished(self):
        """脚本运行完成后的清理工作。"""
        self.script_finished.emit()
        self.runner = None
        self.refresh_groups()
        # 如果当前在“最近使用”视图，则刷新
        if self.current_group_id == "FIXED_RECENT":
            self.filter_scripts_by_group("FIXED_RECENT")
            
    def refresh_groups(self):
        """重新加载分组并通知UI。"""
        groups = self.db_manager.get_all_groups()
        group_tree = self._build_group_tree(groups)
        
        # 获取“最近使用”的数量
        recent_count = self.db_manager.get_recent_script_count()
        
        # 准备一个包含数量的字典发给UI
        group_data = {
            "tree": group_tree,
            "recent_count": recent_count,
            "counts": {g_id: self.db_manager.get_group_script_count(g_id) for g_id, _, _, _ in groups}
        }
        self.groups_updated.emit(group_data, []) # 第二个参数是展开状态，暂时为空

    def _build_group_tree(self, groups):
        """从扁平的组列表构建层级树。"""
        tree = {}
        # 创建节点映射
        nodes = {g_id: {'id': g_id, 'name': name, 'color': color, 'children': []} for g_id, name, _, color in groups}
        
        for g_id, name, parent_id, color in groups:
            if parent_id is None:
                tree[g_id] = nodes[g_id]
            elif parent_id in nodes:
                nodes[parent_id]['children'].append(nodes[g_id])
        return tree

    def add_group(self, name, parent_id=None):
        self.db_manager.add_group(name, parent_id)
        self.log_message.emit(f"[分组] 创建成功: {name}\n")
        self.refresh_groups()
    
    def delete_group(self, group_id, group_name):
        self.db_manager.delete_group(group_id)
        self.log_message.emit(f"[分组] 删除成功: {group_name}\n")
        self.refresh_groups()
        # 重新加载所有脚本
        self.current_group_id = None
        self.scripts_updated.emit(self.db_manager.get_all_scripts())

    def bind_script_to_group(self, script_id, group_id):
        if self.db_manager.bind_script_to_group(script_id, group_id):
            script_name = self.db_manager.get_script_details(script_id)[0] or f"ID {script_id}"
            group_name = self.db_manager.get_group_details(group_id)[0] or f"ID {group_id}"
            self.log_message.emit(f"[绑定] 成功: '{script_name}' -> '{group_name}'\n")
            self.refresh_groups()
        else:
            self.log_message.emit("[绑定] 失败或已存在\n")

    def unbind_script_from_group(self, script_id, group_id):
        self.db_manager.unbind_script_from_group(script_id, group_id)
        self.log_message.emit(f"[解绑] 脚本 {script_id} 已从分组 {group_id} 解绑\n")
        self.refresh_groups()
        self.filter_scripts_by_group(group_id)

    def delete_script(self, script_id):
        self.db_manager.delete_script(script_id)
        self.log_message.emit(f"[删除] 已从数据库删除脚本 ID: {script_id}\n")
        self.refresh_groups()
        if self.current_group_id:
            self.filter_scripts_by_group(self.current_group_id)
        else:
            self.scripts_updated.emit(self.db_manager.get_all_scripts())
            
    def update_script_name(self, script_id, new_name):
        self.db_manager.update_script_name(script_id, new_name)
        self.log_message.emit(f"[编辑] 已更新名称为: {new_name}\n")
        if self.current_group_id:
            self.filter_scripts_by_group(self.current_group_id)
        else:
            self.scripts_updated.emit(self.db_manager.get_all_scripts())
            
    def set_script_rating(self, script_id, rating):
        self.db_manager.update_script_rating(script_id, rating)
        self.log_message.emit(f"[标记] 成功：已设为 {rating} 星\n")
        if self.current_group_id:
            self.filter_scripts_by_group(self.current_group_id)
        else:
            self.scripts_updated.emit(self.db_manager.get_all_scripts())

    def open_containing_folder(self, path):
        folder = os.path.dirname(path)
        if os.path.exists(folder):
            try:
                if sys.platform.startswith('win'):
                    os.startfile(folder)
                elif sys.platform == 'darwin':
                    subprocess.Popen(['open', folder])
                else:
                    subprocess.Popen(['xdg-open', folder])
                self.log_message.emit(f"[交互] 打开文件夹: {folder}\n")
            except Exception as e:
                self.log_message.emit(f"[交互] 无法打开文件夹: {e}\n")
        else:
            self.log_message.emit("[交互] 文件夹不存在\n")
            
    def is_runner_active(self):
        return self.runner and self.runner.isRunning()

