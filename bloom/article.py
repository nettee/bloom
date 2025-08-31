#!/usr/bin/env python3
"""
Article Reader - 文章读取器
统一处理博客文章的读取操作
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any

import frontmatter


class ArticleReader:
    """
    文章读取器，负责读取和解析博客文章
    
    使用 frontmatter 库统一处理 markdown 文件的读取，
    避免重复的文件读取和解析逻辑。
    """
    
    def __init__(self, file_path: Path):
        """
        初始化文章读取器
        
        Args:
            file_path: markdown文件路径
        """
        self.file_path = file_path
        self._post: Optional[frontmatter.Post] = None
        self._loaded = False
    
    def _load_file(self) -> None:
        """
        加载文件内容（懒加载）
        
        Raises:
            SystemExit: 如果无法读取文件
        """
        if self._loaded:
            return
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self._post = frontmatter.load(f)
            self._loaded = True
        except Exception as e:
            print(f"错误：无法读取文件 {self.file_path}: {e}")
            sys.exit(1)
    
    def get_title(self) -> str:
        """
        获取文章标题
        
        Returns:
            str: 文章标题
            
        Raises:
            SystemExit: 如果无法解析文件或缺少标题
        """
        self._load_file()
        
        if not self._post:
            print(f"错误：无法解析文件 {self.file_path}")
            sys.exit(1)
        
        title = self._post.metadata.get('title')
        if not title:
            print(f"错误：文件 {self.file_path} 的frontmatter中缺少 'title' 字段")
            sys.exit(1)
        
        return str(title)
    
    def get_content(self) -> str:
        """
        获取文章正文内容
        
        Returns:
            str: 文章正文内容
            
        Raises:
            SystemExit: 如果无法解析文件或正文为空
        """
        self._load_file()
        
        if not self._post:
            print(f"错误：无法解析文件 {self.file_path}")
            sys.exit(1)
        
        content = self._post.content.strip()
        if not content:
            print(f"错误：文件 {self.file_path} 的正文内容为空")
            sys.exit(1)
        
        return content
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        获取文章的 frontmatter 元数据
        
        Returns:
            Dict[str, Any]: frontmatter 元数据字典
            
        Raises:
            SystemExit: 如果无法解析文件
        """
        self._load_file()
        
        if not self._post:
            print(f"错误：无法解析文件 {self.file_path}")
            sys.exit(1)
        
        return self._post.metadata
    
    def get_title_and_content(self) -> tuple[str, str]:
        """
        同时获取标题和正文内容
        
        Returns:
            tuple[str, str]: (标题, 正文内容)
            
        Raises:
            SystemExit: 如果无法解析文件或缺少必要字段
        """
        title = self.get_title()
        content = self.get_content()
        return title, content
    
    def has_field(self, field_name: str) -> bool:
        """
        检查 frontmatter 中是否包含指定字段
        
        Args:
            field_name: 字段名称
            
        Returns:
            bool: 是否包含该字段
        """
        self._load_file()
        
        if not self._post:
            return False
        
        return field_name in self._post.metadata
    
    def get_field(self, field_name: str, default: Any = None) -> Any:
        """
        获取 frontmatter 中的指定字段值
        
        Args:
            field_name: 字段名称
            default: 默认值
            
        Returns:
            Any: 字段值，如果不存在则返回默认值
        """
        self._load_file()
        
        if not self._post:
            return default
        
        return self._post.metadata.get(field_name, default)


class ArticleUpdater:
    """
    文章更新器，负责更新博客文章的 frontmatter
    使用正则表达式处理 markdown 文件的更新
    """
    
    def __init__(self, file_path: Path):
        """
        初始化文章更新器
        
        Args:
            file_path: markdown文件路径
        """
        self.file_path = file_path
    
    @staticmethod
    def _escape_yaml_string(text: str) -> str:
        """转义YAML字符串中的特殊字符"""
        return text.replace('"', '\\"').replace('\n', '\\n')
    
    @staticmethod
    def _get_current_time() -> str:
        """获取当前时间（上海时区）"""
        from datetime import datetime
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo("Asia/Shanghai"))
        return now.isoformat(timespec="seconds")
    
    def _replace_field(self, content: str, field: str, value: str, add_if_missing: bool = True) -> str:
        """
        替换或添加frontmatter字段
        
        Args:
            content: 文件内容
            field: 字段名
            value: 字段值
            add_if_missing: 如果字段不存在是否添加
            
        Returns:
            str: 更新后的文件内容
        """
        import re
        
        # 匹配字段: "xxx" 或 'xxx' 或 xxx
        field_pattern = fr'({field}:\s*)(["\']?)([^"\'\n]*)\2'
        
        def replace_field_value(match):
            prefix = match.group(1)  # "field: "
            quote = match.group(2) or '"'  # 使用原有的引号，如果没有则用双引号
            return f'{prefix}{quote}{value}{quote}'
        
        # 尝试替换已存在的字段
        new_content = re.sub(field_pattern, replace_field_value, content)
        
        # 如果字段不存在且需要添加
        if new_content == content and add_if_missing:
            print(f"警告：未找到{field}字段，将在frontmatter中添加")
            frontmatter_end_pattern = r'(---\n(?:.*\n)*?)(---)'
            
            def add_field(match):
                frontmatter_content = match.group(1)
                closing_marker = match.group(2)
                return f'{frontmatter_content}{field}: "{value}"\n{closing_marker}'
            
            new_content = re.sub(frontmatter_end_pattern, add_field, content, count=1)
        
        return new_content
    
    def update_summary(self, summary: str) -> None:
        """
        更新文章摘要
        
        Args:
            summary: 新的摘要内容
            
        Raises:
            SystemExit: 如果更新失败
        """
        try:
            # 读取文件内容
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 转义summary中的特殊字符
            escaped_summary = self._escape_yaml_string(summary)
            
            # 更新summary字段
            new_content = self._replace_field(content, "summary", escaped_summary)
            
            # 更新updated时间
            current_time = self._get_current_time()
            new_content = self._replace_field(new_content, "updated", current_time)
            
            # 写回文件
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ 已更新摘要到文件: {self.file_path.name}")
            print(f"📝 摘要内容: {summary}")
            
        except Exception as e:
            print(f"错误：更新文件失败: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    def update_updated_time(self) -> None:
        """
        更新文章的updated时间为当前时间
        
        Raises:
            SystemExit: 如果更新失败
        """
        try:
            # 读取文件内容
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 获取当前时间
            current_time = self._get_current_time()
            
            # 更新updated字段
            new_content = self._replace_field(content, "updated", current_time)
            
            # 写回文件
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ 已更新发布时间到文件: {self.file_path.name}")
            print(f"🕒 发布时间: {current_time}")
            
        except Exception as e:
            print(f"错误：更新文件失败: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1) 