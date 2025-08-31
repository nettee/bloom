#!/usr/bin/env python3
"""
图片上传模块 - 将博客图片上传到 Cloudflare R2
"""

import os
import re
import mimetypes
from pathlib import Path
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from .blog import find_git_root


class BlogImageUploader:
    def __init__(self, cdn_base_url=None, dry_run=False):
        """
        初始化上传器
        
        Args:
            cdn_base_url: CDN 基础 URL
            dry_run: 是否为干运行模式（不实际上传）
        """
        self.dry_run = dry_run
        self.cdn_base_url = cdn_base_url or os.environ.get("CDN_BASE_URL", "")
        
        if not self.cdn_base_url:
            raise ValueError("请设置 CDN_BASE_URL 环境变量或使用 --cdn-url 参数")
        
        # 确保 CDN URL 不以斜杠结尾
        self.cdn_base_url = self.cdn_base_url.rstrip('/')
        
        # 使用 find_git_root 找到项目根目录
        self.project_root = find_git_root()
        self.blog_dir = self.project_root / "src" / "content" / "blog"
        
        # 只有在非 dry_run 模式下才设置 R2 客户端
        if not self.dry_run:
            self.setup_r2_client()
        
    def setup_r2_client(self):
        """设置 R2 客户端"""
        required_env_vars = [
            "R2_ACCOUNT_ID",
            "R2_ACCESS_KEY_ID", 
            "R2_SECRET_ACCESS_KEY",
            "R2_BUCKET_NAME"
        ]
        
        missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
        if missing_vars:
            raise ValueError(f"缺少环境变量: {', '.join(missing_vars)}")
        
        self.account_id = os.environ["R2_ACCOUNT_ID"]
        self.bucket_name = os.environ["R2_BUCKET_NAME"]
        
        # 配置 S3 客户端连接到 R2
        self.s3_client = boto3.client(
            's3',
            endpoint_url=f'https://{self.account_id}.r2.cloudflarestorage.com',
            aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
            region_name='auto',
            config=Config(signature_version='s3v4')
        )
        
    def find_images_in_markdown(self, md_content):
        """从 Markdown 内容中找到所有图片引用"""
        # 匹配 ![alt](path) 格式的图片
        pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        matches = re.findall(pattern, md_content)
        
        # 只返回相对路径的图片（不是 http/https 开头的）
        local_images = []
        for alt_text, img_path in matches:
            if not img_path.startswith(('http://', 'https://')):
                local_images.append((alt_text, img_path))
                
        return local_images
    
    def get_content_type(self, file_path):
        """获取文件的 Content-Type"""
        content_type, _ = mimetypes.guess_type(str(file_path))
        return content_type or 'application/octet-stream'
    
    def upload_image_to_r2(self, local_path, r2_key):
        """
        上传单个图片到 R2
        
        Args:
            local_path: 本地文件路径
            r2_key: R2 中的键名
            
        Returns:
            bool: 上传是否成功
        """
        if self.dry_run:
            print(f"  [DRY RUN] {local_path.name} -> {r2_key}")
            return True
            
        try:
            content_type = self.get_content_type(local_path)
            
            with open(local_path, 'rb') as file:
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=r2_key,
                    Body=file,
                    ContentType=content_type
                )
            
            print(f"  ✓ {local_path.name} -> {r2_key}")
            return True
            
        except ClientError as e:
            print(f"  ✗ 上传失败 {local_path.name}: {e}")
            return False
        except Exception as e:
            print(f"  ✗ 上传失败 {local_path.name}: {e}")
            return False
    
    def process_markdown_file(self, md_file_path):
        """
        处理单个 Markdown 文件
        
        Args:
            md_file_path: Markdown 文件路径
            
        Returns:
            dict: 处理结果信息
        """
        md_path = Path(md_file_path)
        
        # 如果传入的是相对路径，尝试在博客目录中查找
        if not md_path.is_absolute():
            if not md_path.exists():
                md_path = self.blog_dir / md_path
        
        if not md_path.exists():
            raise FileNotFoundError(f"找不到文件: {md_file_path}")
        
        print(f"正在处理文件: {md_path.name}")
        
        # 读取 Markdown 文件内容
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # 提取文章 slug
        slug = md_path.stem  # 去掉 .md 扩展名
        
        # 找到所有本地图片引用
        local_images = self.find_images_in_markdown(md_content)
        
        if not local_images:
            print("未发现本地图片引用")
            return {
                'processed_images': 0,
                'successful_uploads': 0,
                'file_updated': False
            }
        
        print(f"发现图片: {len(local_images)} 个")
        for alt_text, img_path in local_images:
            print(f"  - {img_path}")
        
        mode_text = "[DRY RUN] " if self.dry_run else ""
        print(f"\n{mode_text}上传到 R2:")
        
        # 上传图片并记录替换映射
        replacements = {}
        successful_uploads = 0
        
        for alt_text, img_path in local_images:
            # 构建本地图片完整路径
            local_img_path = md_path.parent / img_path
            
            if not local_img_path.exists():
                print(f"  ✗ 本地文件不存在: {img_path}")
                continue
            
            # 构建 R2 路径: images/blog/{slug}/{filename}
            filename = local_img_path.name
            r2_key = f"images/blog/{slug}/{filename}"
            
            # 上传到 R2
            if self.upload_image_to_r2(local_img_path, r2_key):
                # 构建 CDN URL
                cdn_url = f"{self.cdn_base_url}/{r2_key}"
                replacements[img_path] = cdn_url
                successful_uploads += 1
        
        if not replacements:
            print("没有成功上传的图片，不更新 Markdown 文件")
            return {
                'processed_images': len(local_images),
                'successful_uploads': 0,
                'file_updated': False
            }
        
        print(f"\n{mode_text}更新 Markdown 文件:")
        
        # 替换 Markdown 中的图片路径
        updated_content = md_content
        for old_path, new_url in replacements.items():
            # 替换 ![alt](old_path) 为 ![alt](new_url)
            pattern = rf'(!\[[^\]]*\])\({re.escape(old_path)}\)'
            replacement = r'\1(' + new_url + ')'
            updated_content = re.sub(pattern, replacement, updated_content)
            print(f"  ✓ {old_path} -> {new_url}")
        
        # 保存更新后的文件（除非是 dry_run 模式）
        if not self.dry_run:
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
        
        print(f"\n完成! 处理了 {successful_uploads} 个图片文件")
        
        return {
            'processed_images': len(local_images),
            'successful_uploads': successful_uploads,
            'file_updated': not self.dry_run
        }


def upload_blog_images(markdown_file, cdn_url=None, dry_run=False):
    """
    上传博客图片的主函数
    
    Args:
        markdown_file: Markdown 文件路径
        cdn_url: CDN 基础 URL
        dry_run: 是否为干运行模式
        
    Returns:
        dict: 处理结果信息
    """
    uploader = BlogImageUploader(cdn_base_url=cdn_url, dry_run=dry_run)
    return uploader.process_markdown_file(markdown_file) 