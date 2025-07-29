from pypinyin import lazy_pinyin


def create_pinyin_string(string, hyphen="-"):
    s_lst= lazy_pinyin(string)
    return hyphen.join(s_lst)