#!/usr/bin/env python
# -*-coding:utf-8-*-

"""

"""

__version__ = '0.2.0'



import re

from .zh_number import zh_number_to_int
from pywander.exceptions import GuessFailed


def multi_delimiter_split(string, delimiters='', split_whitespace=True,
                          remove_whitespace=True):
    """
    多个分隔符分割字符串，

    delimiters = ';,'
    split_whitespace 是否加上按照空白分割   默认是按照空白分割
    remove_whitespace 是否移除分隔符两边多余的空白字符 默认移除


    """
    expr_one = r'\s' if split_whitespace else ''

    expr = '[{0}{1}]'.format(delimiters, expr_one)

    if remove_whitespace:
        expr = r'\s*' + expr + r'\s*'

    res = re.split(expr, string)

    return res


def int_number(string):
    """
    类似 int_zh_number 函数，不过假如了 "132" 的 这样的数字字符支持

    :param string:
    :return:
    """
    try:
        return int(string)
    except ValueError:
        try:
            return zh_number_to_int(string)
        except Exception as e:
            raise e


def guess_chapter_id(string):
    """
    根据给定的简短文本猜测 章节编号
    :param string:
    :return:
    """
    g = re.search(r'第([零一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬\s\d]+)章', string)

    if g:
        try:
            chapter_id = int_number(g.group(1))
            return chapter_id
        except Exception as e:
            pass

    raise GuessFailed


def guess_volume_id(string):
    """
    根据给定的简短文本猜测 卷编号
    :param string:
    :return:
    """
    g = re.search(r'第([零一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬\s\d]+)卷', string)

    if g:
        try:
            volume_id = int_number(g.group(1))
            return volume_id
        except Exception as e:
            pass

    raise GuessFailed


