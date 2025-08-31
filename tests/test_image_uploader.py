#!/usr/bin/env python3
"""
图片上传模块的单元测试 - 只测试 dry run 模式
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from rena.image_uploader import BlogImageUploader, upload_blog_images


class TestBlogImageUploader:
    """BlogImageUploader 类的测试 - 只测试 dry run 模式"""
    
    def test_init_with_cdn_url_dry_run(self):
        """测试使用 CDN URL 初始化 dry run 模式"""
        uploader = BlogImageUploader(cdn_base_url="https://example.com", dry_run=True)
        assert uploader.cdn_base_url == "https://example.com"
        assert uploader.dry_run is True
        
    def test_init_without_cdn_url_should_raise_error(self):
        """测试没有 CDN URL 时应该抛出错误"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="请设置 CDN_BASE_URL 环境变量"):
                BlogImageUploader(dry_run=True)
    
    def test_init_with_env_var_dry_run(self):
        """测试使用环境变量初始化 dry run 模式"""
        with patch.dict(os.environ, {"CDN_BASE_URL": "https://env-example.com"}):
            uploader = BlogImageUploader(dry_run=True)
            assert uploader.cdn_base_url == "https://env-example.com"
    
    def test_cdn_url_trailing_slash_removed_dry_run(self):
        """测试 CDN URL 末尾的斜杠被移除 - dry run 模式"""
        uploader = BlogImageUploader(cdn_base_url="https://example.com/", dry_run=True)
        assert uploader.cdn_base_url == "https://example.com"
    
    @patch('rena.image_uploader.find_git_root')
    def test_init_sets_project_paths_dry_run(self, mock_find_git_root):
        """测试初始化时设置项目路径 - dry run 模式"""
        mock_find_git_root.return_value = Path("/fake/project")
        uploader = BlogImageUploader(cdn_base_url="https://example.com", dry_run=True)
        
        assert uploader.project_root == Path("/fake/project")
        assert uploader.blog_dir == Path("/fake/project/src/content/blog")
    
    def test_find_images_in_markdown(self):
        """测试从 Markdown 中查找图片"""
        uploader = BlogImageUploader(cdn_base_url="https://example.com", dry_run=True)
        
        md_content = """
        # Test Article
        
        Here is an image: ![alt text](./images/test.png)
        
        Another image: ![](relative/path/image.jpg)
        
        This should be ignored: ![remote](https://example.com/remote.png)
        
        Also ignored: ![http image](http://example.com/http.png)
        """
        
        images = uploader.find_images_in_markdown(md_content)
        
        assert len(images) == 2
        assert ("alt text", "./images/test.png") in images
        assert ("", "relative/path/image.jpg") in images
    
    def test_get_content_type(self):
        """测试获取文件 Content-Type"""
        uploader = BlogImageUploader(cdn_base_url="https://example.com", dry_run=True)
        
        assert uploader.get_content_type(Path("test.png")) == "image/png"
        assert uploader.get_content_type(Path("test.jpg")) == "image/jpeg"
        assert uploader.get_content_type(Path("test.gif")) == "image/gif"
        assert uploader.get_content_type(Path("test.unknown")) == "application/octet-stream"
    
    def test_upload_image_to_r2_dry_run(self):
        """测试 dry run 模式下的图片上传"""
        uploader = BlogImageUploader(cdn_base_url="https://example.com", dry_run=True)
        
        with tempfile.NamedTemporaryFile(suffix=".png") as tmp_file:
            tmp_path = Path(tmp_file.name)
            result = uploader.upload_image_to_r2(tmp_path, "test/key.png")
            
            assert result is True
    
    @patch('rena.image_uploader.find_git_root')
    def test_process_markdown_file_no_images_dry_run(self, mock_find_git_root):
        """测试处理没有图片的 Markdown 文件 - dry run 模式"""
        mock_find_git_root.return_value = Path("/fake/project")
        uploader = BlogImageUploader(cdn_base_url="https://example.com", dry_run=True)
        
        md_content = "# Test Article\n\nNo images here."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as tmp_file:
            tmp_file.write(md_content)
            tmp_file.flush()
            
            try:
                result = uploader.process_markdown_file(tmp_file.name)
                
                assert result['processed_images'] == 0
                assert result['successful_uploads'] == 0
                assert result['file_updated'] is False
            finally:
                os.unlink(tmp_file.name)
    
    @patch('rena.image_uploader.find_git_root')
    def test_process_markdown_file_with_images_dry_run(self, mock_find_git_root):
        """测试 dry run 模式下处理有图片的 Markdown 文件"""
        mock_find_git_root.return_value = Path("/fake/project")
        uploader = BlogImageUploader(cdn_base_url="https://example.com", dry_run=True)
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            
            # 创建测试图片文件
            img_path = tmp_path / "test.png"
            img_path.write_bytes(b"fake image data")
            
            # 创建 Markdown 文件
            md_content = "# Test\n\n![test](test.png)\n"
            md_path = tmp_path / "test.md"
            md_path.write_text(md_content)
            
            result = uploader.process_markdown_file(str(md_path))
            
            assert result['processed_images'] == 1
            assert result['successful_uploads'] == 1
            assert result['file_updated'] is False  # dry_run 模式不更新文件
            
            # 验证文件内容没有被修改
            assert md_path.read_text() == md_content
    
    def test_process_markdown_file_not_found(self):
        """测试处理不存在的文件"""
        uploader = BlogImageUploader(cdn_base_url="https://example.com", dry_run=True)
        
        with pytest.raises(FileNotFoundError, match="找不到文件"):
            uploader.process_markdown_file("nonexistent.md")


class TestUploadBlogImages:
    """upload_blog_images 函数的测试 - 只测试 dry run 模式"""
    
    @patch('rena.image_uploader.BlogImageUploader')
    def test_upload_blog_images_function_dry_run(self, mock_uploader_class):
        """测试 upload_blog_images 函数 - dry run 模式"""
        mock_uploader = MagicMock()
        mock_uploader.process_markdown_file.return_value = {
            'processed_images': 2,
            'successful_uploads': 2,
            'file_updated': False  # dry_run 模式不更新文件
        }
        mock_uploader_class.return_value = mock_uploader
        
        result = upload_blog_images(
            "test.md", 
            cdn_url="https://example.com", 
            dry_run=True
        )
        
        # 验证 BlogImageUploader 被正确初始化为 dry_run 模式
        mock_uploader_class.assert_called_once_with(
            cdn_base_url="https://example.com",
            dry_run=True
        )
        
        # 验证 process_markdown_file 被调用
        mock_uploader.process_markdown_file.assert_called_once_with("test.md")
        
        # 验证返回结果
        assert result['processed_images'] == 2
        assert result['successful_uploads'] == 2
        assert result['file_updated'] is False


if __name__ == "__main__":
    pytest.main([__file__]) 