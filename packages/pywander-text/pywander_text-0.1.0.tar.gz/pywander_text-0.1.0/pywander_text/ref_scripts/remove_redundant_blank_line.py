"""
移除多余的空白行

"""
from pywander.text.line import is_blank_line
import os

def remove_redundant_blank_line(in_file, **kwargs):
    in_file_name, in_file_ext = os.path.splitext(in_file)
    out_file = in_file_name + '_out' + in_file_ext
    record_file = in_file_name + '_record' + in_file_ext

    with open(in_file, 'rt', encoding='utf8') as f:
        with open(out_file, 'wt', encoding='utf8') as f_out:
                in_blank_line = False
                wrote = False

                for line in f:
                    if is_blank_line(line):
                        in_blank_line = True

                        if not wrote:
                            f_out.write(line)
                            wrote = True
                    else:
                        in_blank_line = False
                        wrote = False
                        f_out.write(line)

    return out_file