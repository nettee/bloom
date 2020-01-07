from pathlib import Path

from model.article import MetaInfo


def test_meta_read():
    print()
    meta_file_name = Path('/Users/william/bloomstore/LeetCode 例题精讲/03-从二叉树遍历到回溯算法/meta.toml')
    MetaInfo.read_from_file(meta_file_name)