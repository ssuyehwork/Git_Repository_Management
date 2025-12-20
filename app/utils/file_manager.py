# app/core/file_manager.py
import os
import re
import shutil
import zipfile
from app.config import constants

class FileManager:
    @staticmethod
    def scan_zip_files(folder):
        """扫描符合条件的压缩文件"""
        if not os.path.exists(folder):
            return []
        zip_files = []
        try:
            for filename in os.listdir(folder):
                if "jules_" in filename and filename.endswith(".zip"):
                    full_path = os.path.join(folder, filename)
                    if os.path.isfile(full_path):
                        zip_files.append(full_path)
        except Exception:
            pass
        return zip_files

    @staticmethod
    def get_next_jules_number(extract_base):
        """获取下一个文件夹序号"""
        if not os.path.exists(extract_base):
            return 1
        max_num = 0
        try:
            for item in os.listdir(extract_base):
                if os.path.isdir(os.path.join(extract_base, item)):
                    match = re.match(r"jules_(\d+)", item)
                    if match:
                        num = int(match.group(1))
                        max_num = max(max_num, num)
        except Exception:
            pass
        return max_num + 1

    @staticmethod
    def extract_zip(zip_path, extract_to):
        """解压并返回文件列表"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                zip_ref.extractall(extract_to)
            return True, file_list
        except Exception as e:
            return False, str(e)

    @staticmethod
    def copy_files_recursive(source, target):
        """递归覆盖复制文件"""
        count = 0
        errors = []
        for root_dir, dirs, files in os.walk(source):
            for file in files:
                try:
                    src_file = os.path.join(root_dir, file)
                    rel_path = os.path.relpath(src_file, source)
                    dst_file = os.path.join(target, rel_path)
                    os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                    shutil.copy2(src_file, dst_file)
                    count += 1
                except Exception as e:
                    errors.append((os.path.relpath(os.path.join(root_dir, file), source), str(e)))
        return count, errors

    @staticmethod
    def get_adjacent_folder(current_path, direction='prev'):
        """
        获取上一个或下一个版本文件夹
        :param current_path: 当前选中的路径
        :param direction: 'prev' 或 'next'
        :return: 新路径 或 None
        """
        # This function assumes a specific folder structure (e.g., jules_1, jules_2)
        # and may need adjustment based on the actual use case.
        # For now, it's included as is from the reference code.
        base_dir = os.path.dirname(current_path) if current_path else constants.DOWNLOAD_FOLDER

        if not os.path.exists(base_dir):
            return None

        folders = []
        try:
            for item in os.listdir(base_dir):
                full_path = os.path.join(base_dir, item)
                if os.path.isdir(full_path):
                    match = re.match(r"jules_(\d+)", item)
                    if match:
                        num = int(match.group(1))
                        folders.append((num, full_path))
        except Exception:
            return None

        folders.sort(key=lambda x: x[0])

        if not folders:
            return None

        norm_current = os.path.normpath(current_path) if current_path else ""
        current_idx = -1
        for i, (_, path) in enumerate(folders):
            if os.path.normpath(path) == norm_current:
                current_idx = i
                break

        target_idx = -1
        if current_idx != -1:
            if direction == 'prev':
                target_idx = current_idx - 1
            else:
                target_idx = current_idx + 1

        if 0 <= target_idx < len(folders):
            return folders[target_idx][1]

        return None
