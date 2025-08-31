#!/usr/bin/env python3
import unittest
import tempfile
import os
import sys
from pathlib import Path

from rena.article import ArticleReader


class TestArticleReader(unittest.TestCase):
    """ArticleReader 类的单元测试"""
    
    def setUp(self):
        """测试前准备，创建测试文件"""
        self.test_content = """---
title: 测试文章
date: 2024-01-01T00:00:00+08:00
updated: 2024-01-01T00:00:00+08:00
keywords: [测试, 文章]
featured: false
summary: "这是一个测试文章"
---

## 测试标题

这是测试文章的正文内容。

### 子标题

更多内容...
"""
        # 创建临时测试文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(self.test_content)
            self.test_file = Path(f.name)
        
        # 创建 ArticleReader 实例
        self.reader = ArticleReader(self.test_file)
    
    def tearDown(self):
        """测试后清理，删除测试文件"""
        os.unlink(self.test_file)
    
    def test_get_title(self):
        """测试获取标题功能"""
        title = self.reader.get_title()
        self.assertEqual(title, "测试文章")
    
    def test_get_content(self):
        """测试获取正文内容功能"""
        content = self.reader.get_content()
        self.assertIn("测试文章的正文内容", content)
        self.assertGreater(len(content), 10)
    
    def test_get_metadata(self):
        """测试获取元数据功能"""
        metadata = self.reader.get_metadata()
        self.assertEqual(metadata["title"], "测试文章")
        # frontmatter 库会将日期字符串解析为 datetime 对象
        self.assertTrue(hasattr(metadata["date"], "isoformat"))  # 验证是日期对象
        self.assertEqual(metadata["featured"], False)
        self.assertEqual(metadata["summary"], "这是一个测试文章")
        self.assertEqual(metadata["keywords"], ["测试", "文章"])
    
    def test_get_title_and_content(self):
        """测试同时获取标题和内容功能"""
        title, content = self.reader.get_title_and_content()
        self.assertEqual(title, "测试文章")
        self.assertIn("测试文章的正文内容", content)
    
    def test_has_field(self):
        """测试检查字段是否存在功能"""
        self.assertTrue(self.reader.has_field("title"))
        self.assertTrue(self.reader.has_field("keywords"))
        self.assertFalse(self.reader.has_field("author"))
        self.assertFalse(self.reader.has_field("non_existent_field"))
    
    def test_get_field(self):
        """测试获取字段值功能"""
        self.assertEqual(self.reader.get_field("title"), "测试文章")
        self.assertEqual(self.reader.get_field("featured"), False)
        self.assertEqual(self.reader.get_field("author", "默认作者"), "默认作者")
        self.assertIsNone(self.reader.get_field("non_existent_field"))


if __name__ == "__main__":
    unittest.main() 