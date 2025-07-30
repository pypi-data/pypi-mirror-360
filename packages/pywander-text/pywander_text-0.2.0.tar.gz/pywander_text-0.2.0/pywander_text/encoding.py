#!/usr/bin/env python
# -*-coding:utf-8-*-

"""
编码转换问题
"""
import click
from tabulate import tabulate

def convert_encoding(origin_string, origin_encoding, to_encoding,
                     errors='ignore'):
    b = origin_string.encode(origin_encoding, errors=errors)
    s = b.decode(to_encoding, errors)
    return s


def print_encoding_convert_tab(string, encoding_list=None, errors='ignore'):
    """
    猜测某个乱码中文字符的可能字符编码和内容
    """

    if encoding_list is None:
        encoding_list = ["UTF-8", "GB18030", "GB2312", "GBK", "Windows-1252",
                         "ISO8859-1"]

    table = []

    for encoding in encoding_list:
        for origin_encoding in encoding_list:
            if encoding == origin_encoding:
                continue

            s = convert_encoding(string, encoding, origin_encoding)

            table.append([encoding, origin_encoding, s])

    headers = [' 假定现在编码 ', ' 假定原来的编码 ', ' 恢复后的字符串 ']

    result = tabulate(table, headers=headers, tablefmt="plain")

    click.echo(result)

    return result


if __name__ == '__main__':
    print_encoding_convert_tab('涓枃')
