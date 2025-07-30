"""
找到某一行，进行内容修改，使其成为tex的chapter标签

"""

import re


def modify_line_to_tex_chapter2(in_file, out_file):
    r"""
    {{旧约 -\/- 约伯记(Job) -\/- 第 2 章 ( 本篇共有 42 章 ) 　}}
    =>
    \chapter{约伯记第2章}

    """
    with open(in_file, 'rt', encoding='utf8') as f:
        with open(out_file, 'wt', encoding='utf8') as f_out:
                pattern = r'^{{'

                for line in f:
                    g = re.match(pattern, line)
                    if g:
                        line = re.sub(r'[{}\\/\s-]', '', line)

                        line = re.sub(r'旧约', '', line)

                        line = re.sub(r'\([^)]*\)', '', line)

                        new_line = f'\\chapter{{{line}}}'
                        # 帖撒罗尼迦前书
                        print(new_line)
                        f_out.write(new_line)
                    else:
                        f_out.write(line)

def modify_line_to_tex_chapter(in_file, out_file):
    with open(in_file, 'rt', encoding='utf8') as f:
        with open(out_file, 'wt', encoding='utf8') as f_out:
                pattern = r'^{{'

                for line in f:
                    g = re.match(pattern, line)
                    if g:
                        line = re.sub(r'[{}\-\\/\s]', '', line)

                        line = re.sub(r'新约', '', line)

                        line = re.sub(r'\([^)]*\)', '', line)

                        new_line = f'\\chapter{{{line}}}'
                        # 帖撒罗尼迦前书
                        print(new_line)
                        f_out.write(new_line)
                    else:
                        f_out.write(line)