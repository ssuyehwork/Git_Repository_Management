# data/database.py
import sqlite3
from datetime import datetime
import random

class DatabaseManager:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self._initialize_database()

    def _initialize_database(self):
        """创建所有必要的表并执行任何需要的模式迁移。"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS scripts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                last_run TIMESTAMP,
                rating INTEGER DEFAULT 0
            )
        ''')
        try:
            self.cursor.execute('ALTER TABLE scripts ADD COLUMN last_run TIMESTAMP')
        except sqlite3.OperationalError:
            pass  # 列已存在
        try:
            self.cursor.execute('ALTER TABLE scripts ADD COLUMN rating INTEGER DEFAULT 0')
        except sqlite3.OperationalError:
            pass  # 列已存在

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                parent_id INTEGER,
                color TEXT NOT NULL,
                FOREIGN KEY(parent_id) REFERENCES groups(id) ON DELETE CASCADE
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS script_groups (
                script_id INTEGER,
                group_id INTEGER,
                FOREIGN KEY(script_id) REFERENCES scripts(id) ON DELETE CASCADE,
                FOREIGN KEY(group_id) REFERENCES groups(id) ON DELETE CASCADE,
                UNIQUE(script_id, group_id)
            )
        ''')
        self.conn.commit()

    def get_group_script_count(self, group_id):
        """获取一个分组下的脚本数量。"""
        self.cursor.execute('SELECT COUNT(*) FROM script_groups WHERE group_id = ?', (group_id,))
        count = self.cursor.fetchone()
        return count[0] if count else 0

    def get_recent_scripts(self, limit=20):
        """获取最近运行的脚本。"""
        self.cursor.execute('''
            SELECT id, name, path, rating, last_run FROM scripts 
            WHERE last_run IS NOT NULL 
            ORDER BY last_run DESC LIMIT ?
        ''', (limit,))
        return self.cursor.fetchall()
        
    def get_recent_script_count(self):
        """获取最近运行脚本的总数"""
        self.cursor.execute('SELECT COUNT(*) FROM scripts WHERE last_run IS NOT NULL')
        return self.cursor.fetchone()[0]

    def get_scripts_in_group(self, group_id):
        """获取一个分组下的所有脚本。"""
        self.cursor.execute('''
            SELECT s.id, s.name, s.path, s.rating FROM scripts s
            JOIN script_groups sg ON s.id = sg.script_id
            WHERE sg.group_id = ?
            ORDER BY s.name
        ''', (group_id,))
        return self.cursor.fetchall()
        
    def get_all_scripts(self):
        """获取数据库中所有的脚本。"""
        self.cursor.execute('SELECT id, name, path, rating FROM scripts ORDER BY name')
        return self.cursor.fetchall()
        
    def search_scripts(self, text):
        """根据文本模糊搜索脚本。"""
        like_pattern = f'%{text}%'
        self.cursor.execute('SELECT id, name, path, rating FROM scripts WHERE name LIKE ? OR path LIKE ?', (like_pattern, like_pattern))
        return self.cursor.fetchall()

    def add_group(self, name, parent_id=None):
        """添加一个新的分组。"""
        color = self._generate_unique_color()
        self.cursor.execute('INSERT INTO groups (name, parent_id, color) VALUES (?, ?, ?)', (name, parent_id, color))
        self.conn.commit()
        return self.cursor.lastrowid

    def delete_group(self, group_id):
        """删除一个分组及其所有关联。"""
        self.cursor.execute('DELETE FROM groups WHERE id = ?', (group_id,))
        self.cursor.execute('DELETE FROM script_groups WHERE group_id = ?', (group_id,))
        self.conn.commit()
        
    def get_all_groups(self):
        """获取所有分组，用于构建树。"""
        self.cursor.execute('SELECT id, name, parent_id, color FROM groups')
        return self.cursor.fetchall()

    def bind_script_to_group(self, script_id, group_id):
        """将脚本绑定到分组。"""
        try:
            self.cursor.execute('INSERT OR IGNORE INTO script_groups (script_id, group_id) VALUES (?, ?)', (script_id, group_id))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def unbind_script_from_group(self, script_id, group_id):
        """从分组解绑脚本。"""
        self.cursor.execute('DELETE FROM script_groups WHERE script_id = ? AND group_id = ?', (script_id, group_id))
        self.conn.commit()

    def delete_script(self, script_id):
        """从数据库删除脚本。"""
        self.cursor.execute('DELETE FROM scripts WHERE id = ?', (script_id,))
        self.cursor.execute('DELETE FROM script_groups WHERE script_id = ?', (script_id,))
        self.conn.commit()
        
    def delete_script_by_path(self, script_path):
        """根据路径删除脚本，用于清理无效路径。"""
        self.cursor.execute('DELETE FROM scripts WHERE path = ?', (script_path,))
        self.conn.commit()

    def update_script_name(self, script_id, new_name):
        """更新脚本的名称。"""
        self.cursor.execute('UPDATE scripts SET name = ? WHERE id = ?', (new_name, script_id))
        self.conn.commit()

    def update_script_rating(self, script_id, rating):
        """更新脚本的评级。"""
        self.cursor.execute('UPDATE scripts SET rating = ? WHERE id = ?', (rating, script_id))
        self.conn.commit()

    def update_script_last_run(self, script_path, name):
        """更新或插入脚本的最后运行时间。"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('SELECT id FROM scripts WHERE path = ?', (script_path,))
        res = self.cursor.fetchone()
        if res:
            self.cursor.execute('UPDATE scripts SET last_run = ? WHERE path = ?', (current_time, script_path))
        else:
            self.cursor.execute('INSERT INTO scripts (path, name, last_run) VALUES (?, ?, ?)', (script_path, name, current_time))
        self.conn.commit()

    def _generate_unique_color(self):
        """生成一个数据库中尚不存在的随机颜色。"""
        self.cursor.execute('SELECT color FROM groups')
        existing_colors = {row[0] for row in self.cursor.fetchall()}
        while True:
            r = random.randint(100, 255)
            g = random.randint(100, 255)
            b = random.randint(100, 255)
            color = f'#{r:02x}{g:02x}{b:02x}'
            if color not in existing_colors:
                return color
                
    def get_script_details(self, script_id):
        """通过ID获取脚本的名称和路径。"""
        self.cursor.execute('SELECT name, path FROM scripts WHERE id = ?', (script_id,))
        return self.cursor.fetchone()

    def get_group_details(self, group_id):
        """通过ID获取分组的名称。"""
        self.cursor.execute('SELECT name FROM groups WHERE id = ?', (group_id,))
        return self.cursor.fetchone()


    def close(self):
        """关闭数据库连接。"""
        self.conn.close()
