"""
对某个文档执行某个正则表达式替换逻辑

将 \texttt{what...}
=>
\verb+what...+

re_match_pattern
r'\\texttt{(?P<content>[^}]+)}'

re_replace_pattern
f'\\verb+{content}+'

"""
import logging
import os
import re

logger = logging.getLogger(__name__)


def re_replace(in_file, re_match_pattern=None, re_replace_pattern=None, **kwargs):
    """
    """
    in_file_name, in_file_ext = os.path.splitext(in_file)
    out_file = in_file_name + '_out' + in_file_ext
    record_file = in_file_name + '_record' + in_file_ext

    if re_match_pattern is None:
        logger.warning("re_match_pattern must be defined")
        return in_file
    if re_replace_pattern is None:
        logger.warning("re_replace_pattern must be defined")
        return in_file

    def do_something(matched):
        content = matched.group('content')
        value = re_replace_pattern
        return value

    line_count = 1

    with open(in_file, 'rt', encoding='utf8') as f:
        with open(out_file, 'wt', encoding='utf8') as f_out:
            with open(record_file, 'at+', encoding='utf8') as f_record:
                pattern = re_match_pattern

                for line in f:
                    old_line = line

                    if re.search(pattern, line):
                        new_line = re.sub(pattern, do_something, line)

                        f_record.write(f"""line:{line_count} \n
{old_line}
=>
{new_line}
\n
""")
                    else:
                        new_line = line

                    line_count += 1
                    f_out.write(new_line)
    return out_file
