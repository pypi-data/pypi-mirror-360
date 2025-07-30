import opencc


def tc2sc(tc_text):
    """
    繁体转简体
    :param text:
    :return:
    """
    converter = opencc.OpenCC('t2s.json')
    sc_text = converter.convert(tc_text)
    return sc_text


def sc2tc(sc_text):
    """
    简体转繁体
    :param sc_text:
    :return:
    """
    converter = opencc.OpenCC('s2t.json')
    tc_text = converter.convert(sc_text)
    return tc_text
