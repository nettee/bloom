#!/usr/bin/env python3
"""
博客写作助手 (bloom) 主入口文件
"""


import click

from .slug_generator import generate_blog_slug
from .image_uploader import upload_blog_images
from .blog import find_modified_blog_file


@click.group()
def cli():
    """Bloom - 博客写作助手工具"""
    pass


@cli.command()
def slug():
    """生成博客文章的 URL slug"""
    try:
        result = generate_blog_slug()
        click.secho("成功生成文章 slug", fg="green")
    except Exception as e:
        click.secho(f"错误: {str(e)}", fg="red")
        raise click.Abort()


@cli.command()
@click.argument('markdown_file', required=False)
@click.option('--cdn-url', help='CDN 基础 URL (覆盖环境变量)')
@click.option('--dry-run', is_flag=True, help='干运行模式，不实际上传文件')
def upload(markdown_file, cdn_url, dry_run):
    """上传博客图片到 Cloudflare R2"""
    try:
        # 如果没有指定文件，自动识别正在修改的文章文件
        if not markdown_file:
            click.secho("📁 自动识别正在修改的博客文件...", fg="blue")
            blog_file = find_modified_blog_file()
            markdown_file = str(blog_file)
            click.secho(f"✅ 找到文件: {blog_file.name}", fg="blue")
        
        result = upload_blog_images(markdown_file, cdn_url=cdn_url, dry_run=dry_run)
        
        if dry_run:
            click.secho("干运行完成", fg="yellow")
        else:
            click.secho("成功上传博客图片", fg="green")
            
        # 显示处理结果统计
        click.secho(f"处理图片: {result['processed_images']} 个", fg="blue")
        click.secho(f"成功上传: {result['successful_uploads']} 个", fg="blue")
        click.secho(f"文件已更新: {'是' if result['file_updated'] else '否'}", fg="blue")
        
    except Exception as e:
        click.secho(f"错误: {str(e)}", fg="red")
        raise click.Abort()


if __name__ == "__main__":
    cli()