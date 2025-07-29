"""
处理一行文本的逻辑
"""
import re

def is_blank_line(line):
    pattern = r'^\s*$'
    return bool(re.match(pattern, line))


def is_contain_chinese(check_str):
    """
    判断字符串中是否包含中文
    :param check_str: {str} 需要检测的字符串
    :return: {bool} 包含返回True， 不包含返回False
    """
    for ch in check_str:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False