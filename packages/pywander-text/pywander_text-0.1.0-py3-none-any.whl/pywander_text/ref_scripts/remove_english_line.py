"""
英文原文行-中文翻译行

保留中文行，保留空白行，其余移除。
"""

import os
from pywander.text.line import is_contain_chinese, is_blank_line


def remove_english_line(in_file, **kwargs):
    in_file_name, in_file_ext = os.path.splitext(in_file)
    out_file = in_file_name + '_out' + in_file_ext
    record_file = in_file_name + '_record' + in_file_ext

    with open(in_file, 'rt', encoding='utf8') as f:
        with open(out_file, 'wt', encoding='utf8') as f_out:
            with open(record_file, 'wt', encoding='utf8') as f_record:
                for line in f:
                    if is_contain_chinese(line):
                        f_out.write(line)
                    elif is_blank_line(line):
                        f_out.write(line)
                    else:
                        f_record.write(line)

    return out_file