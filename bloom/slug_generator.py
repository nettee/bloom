#!/usr/bin/env python3
"""
Slug Generator - 博客文章slug生成器
"""

import re
import sys
from pathlib import Path

from .llm import create_llm_client
from .blog import find_modified_blog_file, rename_blog_file
from .article import ArticleReader


def generate_slug_with_llm(title: str) -> str:
    """
    调用LLM生成slug
    
    Args:
        title: 文章标题
        
    Returns:
        str: 生成的slug
        
    Raises:
        SystemExit: 如果LLM调用失败
    """
    prompt = f"Generate a URL slug for this article title: {title}\n\nRequirements:\n- Only use lowercase letters, numbers, and hyphens (-)\n- Maximum 50 characters\n- Be concise and reflect the main topic\n- Return only the slug string\n\nSlug:"

    try:
        client = create_llm_client()
        
        # 调用LLM生成slug
        messages = [{"role": "user", "content": prompt}]
        response_obj = client.chat_completion(
            messages=messages,
            temperature=0.3  # 降低随机性，确保输出稳定
        )
        
        response = response_obj.choices[0].message.content or ""
        
        # 清理响应，去除可能的前缀和后缀
        slug = response.strip()
        if slug.startswith('slug:'):
            slug = slug[5:].strip()
        if slug.startswith('Slug:'):
            slug = slug[5:].strip()
        
        # 验证生成的slug格式
        if not slug:
            print(f"错误：LLM返回空响应")
            sys.exit(1)
        
        if not all(c.islower() or c.isdigit() or c == '-' for c in slug):
            print(f"错误：生成的slug包含非法字符: {slug}")
            print(f"非法字符: {[c for c in slug if not (c.islower() or c.isdigit() or c == '-')]}")
            sys.exit(1)
            
        return slug
        
    except Exception as e:
        print(f"错误：LLM调用失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def generate_blog_slug() -> None:
    """
    生成博客文章slug的主函数
    """
    print("🚀 开始自动生成文章slug...")
    
    # 1. 找到正在修改的博客文件
    print("📁 检测正在修改的博客文件...")
    blog_file = find_modified_blog_file()
    print(f"✅ 找到文件: {blog_file.name}")
    
    # 2. 提取文章标题
    print("📝 提取文章标题...")
    reader = ArticleReader(blog_file)
    title = reader.get_title()
    print(f"✅ 文章标题: {title}")
    
    # 3. 生成slug
    print("🤖 调用LLM生成slug...")
    slug = generate_slug_with_llm(title)
    print(f"✅ 生成的slug: {slug}")
    
    # 4. 重命名文件
    print("📝 重命名文件...")
    new_path = rename_blog_file(blog_file, slug)
    print(f"✅ 文件已重命名: {blog_file.name} -> {new_path.name}")
    
    print("🎉 slug生成完成！")


if __name__ == "__main__":
    generate_blog_slug()