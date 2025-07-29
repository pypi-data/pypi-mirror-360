"""
数字中文转换
"""

def zh_number(num):
    """
    输入一个整数值返回中文表达的字符串
    """
    if not isinstance(num, int):
        try:
            int(num)
        except Exception as e:
            raise ValueError('incorrect number format error.')

    zh_number_ref = [
        (100000000, '亿'),
        (10000000, '千万'),
        (1000000, '百万'),
        (100000, '十万'),
        (10000, '万'),
        (1000, '千'),
        (100, '百'),
        (10, '十'),
        (1, '')
    ]
    zh_number_ref_string = '零一二三四五六七八九'

    result = ''

    if 0 <= num < 10:
        return zh_number_ref_string[num]

    flag = False
    last_suffix = ''
    for factor, suffix in zh_number_ref:
        if num // factor > 0:
            d = num // factor
            num = num - d * factor
            result += '{}{}'.format(zh_number_ref_string[d], suffix)
            flag = True
            last_suffix = suffix
        else:
            if flag and suffix and last_suffix and suffix[-1] != last_suffix[-1]:
                result += '零'
                flag = False

    result = result.rstrip('零')
    return result


def zh_number_to_int(string):
    """
    将 一百一 或者 一百零一 这样的表达 转换称为 数字

    字符串组成只允许是:
    零一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬 此外还有 ‘0123456789’

    推荐的输入是标准中文数字格式，不过1万5千这样的不是很规范的格式也是支持的

    >>> zh_number_to_int('一百')
    100
    >>> zh_number_to_int('二十二')
    22
    >>> zh_number_to_int('1万6千')
    16000

    ref https://github.com/binux/binux-tools/blob/master/python/chinese_digit.py
    """
    result = 0
    pre = 0

    for s in string:
        if s not in CHS_ARABIC_MAP.keys():
            raise ValueError('incorrect string format error.')

    res = list(map(lambda k: CHS_ARABIC_MAP[k], string))

    for d in res:
        # 如果等于1万
        if d == 10000:
            result += pre
            result = result * d
            pre = 0
        # 如果等于十或者百，千
        elif d >= 10:
            if pre == 0:
                pre = 1
            result += d * pre
            pre = 0
        # 如果是个位数
        else:
            pre = d
    result += pre
    return result


CHS_ARABIC_MAP = {'零': 0,
                  '0': 0,
                  '一': 1,
                  '1': 1,
                  '二': 2,
                  '2': 2,
                  '三': 3,
                  '3': 3,
                  '四': 4,
                  '4': 4,
                  '五': 5,
                  '5': 5,
                  '六': 6,
                  '6': 6,
                  '七': 7,
                  '7': 7,
                  '八': 8,
                  '8': 8,
                  '九': 9,
                  '9': 9,
                  '十': 10,
                  '百': 100,
                  '千': 1000,
                  '万': 10000,
                  '壹': 1,
                  '贰': 2,
                  '叁': 3,
                  '肆': 4,
                  '伍': 5,
                  '陆': 6,
                  '柒': 7,
                  '捌': 8,
                  '玖': 9,
                  '拾': 10,
                  '佰': 100,
                  '仟': 1000,
                  '萬': 10000,
                  }
