"""
移除一行前面某些不要的部分
"""

import re

def remove_unwanted_parts(in_file, out_file, record_file):
    def do_something(matched):
        value = matched.group('deleted')
        with open(record_file, 'at+', encoding='utf8') as f_deleted:
            f_deleted.write(value)
            f_deleted.write('\n')
        return ""

    with open(in_file, 'rt', encoding='utf8') as f:
        with open(out_file, 'wt', encoding='utf8') as f_out:
            pattern = r'(?P<deleted>^\d+:\d+[\s]+)'

            for line in f:
                new_line = re.sub(pattern, do_something, line)
                f_out.write(new_line)
