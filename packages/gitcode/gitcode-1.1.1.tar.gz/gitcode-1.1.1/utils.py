import os
import sys
from pathlib import Path
from typing import Optional
from colorama import Fore, Style, init
import urllib.parse

# 初始化colorama
init(autoreset=True)


def print_success(message: str) -> None:
    """打印成功信息"""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")


def print_error(message: str) -> None:
    """打印错误信息"""
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")


def print_warning(message: str) -> None:
    """打印警告信息"""
    print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")


def print_info(message: str) -> None:
    """打印信息"""
    print(f"{Fore.CYAN}ℹ {message}{Style.RESET_ALL}")


def validate_repo_name(repo_name: str) -> bool:
    """验证仓库名称格式"""
    if not repo_name:
        return False
    
    # 先解码URL编码
    decoded_name = urllib.parse.unquote(repo_name)
    
    # 检查是否包含至少一个斜杠（在解码后的名称中）
    if '/' not in decoded_name:
        return False
    
    parts = decoded_name.split('/')
    # 支持多层次仓库名称，至少需要2个部分，但可以有更多
    # 允许hf_mirrors/Qwen/Qwen3-Reranker-0.6B这样的格式
    if len(parts) < 2:
        return False
    
    # 检查每个部分都不为空
    for part in parts:
        if not part:
            return False
    
    # 检查字符是否合法（字母、数字、下划线、短横线、点号、斜杠）
    # 对于原始名称，也允许%字符用于URL编码
    allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.%/')
    
    # 验证原始名称的字符
    for char in repo_name:
        if char not in allowed_chars:
            return False
    
    return True


def validate_repo_type(repo_type: str) -> bool:
    """验证仓库类型"""
    return repo_type in ['model', 'dataset']


def get_file_size(file_path: Path) -> int:
    """获取文件大小"""
    try:
        return file_path.stat().st_size
    except OSError:
        return 0


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def get_directory_size(dir_path: Path) -> int:
    """获取目录大小"""
    total_size = 0
    try:
        for file_path in dir_path.rglob('*'):
            if file_path.is_file():
                total_size += get_file_size(file_path)
    except OSError:
        pass
    return total_size


def count_files_in_directory(dir_path: Path) -> int:
    """统计目录中的文件数量"""
    count = 0
    try:
        for file_path in dir_path.rglob('*'):
            if file_path.is_file():
                count += 1
    except OSError:
        pass
    return count


def confirm_action(message: str, default: bool = False) -> bool:
    """确认操作"""
    suffix = " [Y/n]" if default else " [y/N]"
    while True:
        response = input(f"{message}{suffix}: ").strip().lower()
        if response == '':
            return default
        elif response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("请输入 y/yes 或 n/no")


def is_valid_path(path_str: str) -> bool:
    """检查路径是否有效"""
    try:
        Path(path_str)
        return True
    except (ValueError, OSError):
        return False


def ensure_directory(dir_path: Path) -> bool:
    """确保目录存在"""
    try:
        dir_path.mkdir(parents=True, exist_ok=True)
        return True
    except OSError:
        return False


def get_relative_path(file_path: Path, base_path: Path) -> str:
    """获取相对路径"""
    try:
        return str(file_path.relative_to(base_path))
    except ValueError:
        return str(file_path) 