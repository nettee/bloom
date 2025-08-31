#!/usr/bin/env python3
"""
Blog - 博客文件处理模块
"""

import re
import subprocess
import sys
from pathlib import Path


def find_git_root() -> Path:
    """动态查找.git仓库的根目录"""
    # 从脚本执行的当前工作目录开始
    current_path = Path.cwd()
    # 向上遍历目录，直到找到 .git 文件夹
    while current_path != current_path.parent:
        if (current_path / ".git").is_dir():
            return current_path
        current_path = current_path.parent
    # 检查文件系统的根目录 (e.g., /)
    if (current_path / ".git").is_dir():
        return current_path
    raise FileNotFoundError("错误：无法找到.git仓库根目录。请在项目仓库内运行此脚本。")


def find_workdir_modified_blog_files(root_dir: Path, blog_dir: Path) -> list[Path]:
    """
    查找工作区中修改的博客文件
    
    Args:
        root_dir: 项目根目录
        blog_dir: 博客目录路径
        
    Returns:
        list[Path]: 工作区中修改的 .md 文件列表
        
    Raises:
        subprocess.CalledProcessError: 如果无法获取git状态
    """
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=root_dir,
        capture_output=True,
        text=True,
        check=True
    )
    
    # 使用正则表达式直接匹配博客目录下的.md文件
    # 匹配模式：任意git状态 + src/content/blog/xxx.md
    blog_pattern = re.compile(r'src/content/blog/.*\.md')
    modified_files = []
    
    for line in result.stdout.strip().split('\n'):
        if not line:
            continue
        
        # 使用正则表达式提取博客文件路径
        file_path_match = blog_pattern.search(line)
        if file_path_match:
            file_path = file_path_match.group()
            full_path = root_dir / file_path
            if full_path.exists():
                modified_files.append(full_path)
    
    return modified_files


def find_last_commit_blog_files(root_dir: Path, blog_dir: Path) -> list[Path]:
    """
    查找最近一次提交中修改的博客文件
    
    Args:
        root_dir: 项目根目录
        blog_dir: 博客目录路径
        
    Returns:
        list[Path]: 最近提交中修改的 .md 文件列表
        
    Raises:
        subprocess.CalledProcessError: 如果无法获取提交信息
    """
    # 获取最近一次提交中修改的文件
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
        cwd=root_dir,
        capture_output=True,
        text=True,
        check=True
    )
    
    # 使用正则表达式直接匹配博客目录下的.md文件
    blog_pattern = re.compile(r'src/content/blog/.*\.md')
    committed_files = []
    
    for line in result.stdout.strip().split('\n'):
        if not line:
            continue
        
        # 使用正则表达式提取博客文件路径
        file_path_match = blog_pattern.search(line)
        if file_path_match:
            file_path = file_path_match.group()
            full_path = root_dir / file_path
            if full_path.exists():  # 确保文件仍然存在
                committed_files.append(full_path)
    
    return committed_files


def find_modified_blog_file() -> Path:
    """
    找到正在修改的博客文件
    
    优先级：
    1. 工作区中修改的 .md 文件（未提交的内容）
    2. 最近一次提交中的 .md 文件（如果只有一个）
    
    Returns:
        Path: 修改的博客文件路径
        
    Raises:
        SystemExit: 如果找不到文件或找到多个文件
    """
    # 获取项目根目录
    try:
        root_dir = find_git_root()
    except FileNotFoundError as e:
        print(f"{e}")
        sys.exit(1)
    
    blog_dir = root_dir / "src" / "content" / "blog"
    
    # 1. 优先检查工作区状态（未提交的修改）
    try:
        modified_files = find_workdir_modified_blog_files(root_dir, blog_dir)
    except subprocess.CalledProcessError as e:
        print(f"错误：无法获取git状态: {e}")
        sys.exit(1)
    
    # 如果工作区有修改的文件，优先使用
    if len(modified_files) == 1:
        return modified_files[0]
    elif len(modified_files) > 1:
        print(f"错误：找到多个修改的 .md 文件，请确保只修改一个文件：")
        for file in modified_files:
            print(f"  - {file.relative_to(root_dir)}")
        sys.exit(1)
    
    # 2. 如果工作区没有修改，检查最近一次提交
    print("📝 工作区无修改文件，检查最近一次提交...")
    try:
        committed_files = find_last_commit_blog_files(root_dir, blog_dir)
    except subprocess.CalledProcessError as e:
        print(f"错误：无法获取最近提交的文件: {e}")
        sys.exit(1)
    
    if len(committed_files) == 0:
        print("错误：在工作区和最近一次提交中都没有找到博客 .md 文件")
        sys.exit(1)
    elif len(committed_files) == 1:
        print(f"✅ 使用最近提交中的文件: {committed_files[0].name}")
        return committed_files[0]
    else:
        print(f"错误：最近一次提交中找到多个 .md 文件：")
        for file in committed_files:
            print(f"  - {file.relative_to(root_dir)}")
        sys.exit(1)


def rename_blog_file(old_path: Path, slug: str) -> Path:
    """
    根据slug重命名文件
    
    Args:
        old_path: 原文件路径
        slug: 新的slug
        
    Returns:
        Path: 新文件路径
        
    Raises:
        SystemExit: 如果重命名失败
    """
    new_filename = f"{slug}.md"
    new_path = old_path.parent / new_filename
    
    # 检查新文件名是否已存在
    if new_path.exists():
        print(f"错误：目标文件已存在: {new_path}")
        sys.exit(1)
    
    try:
        old_path.rename(new_path)
        return new_path
    except Exception as e:
        print(f"错误：重命名文件失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # 测试代码
    try:
        file_path = find_modified_blog_file()
        print(f"找到博客文件: {file_path}")
    except SystemExit:
        print("测试失败")