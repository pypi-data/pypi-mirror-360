import logging
import click

from . import __version__
from .encoding import print_encoding_convert_tab
from .pinyin import create_pinyin_string

def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('pywander_text version {}'.format(__version__))
    ctx.exit()

def enable_debug(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return

    logging.basicConfig(level=logging.DEBUG)

@click.group()
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True,
              help="print this software version")
@click.option('-V', '--verbose', is_flag=True, is_eager=True,
              callback=enable_debug, expose_value=False,
              help='print verbose info')
def main():
    """
    pywander_text --version
    """
    pass


@main.command()
@click.argument('string')
def encoding(string):
    """
    猜测某个乱码字符串的可能正确编码

    pywander_text encoding STRING

    STRING: the input string
    """
    print_encoding_convert_tab(string)


@main.command()
@click.argument('string')
@click.option('--hyphen', default='-',)
def pinyin(string, hyphen):
    """
    将某一字符串转成拼音并用某个连接符号连接起来

    params:

    STRING: the input string
    """
    result = create_pinyin_string(string, hyphen=hyphen)
    click.echo(result)

@main.command()
@click.argument('infile')
def process(infile):
    """
    对当前文件夹下的某个文件执行某个脚本处理动作

    你可以在当前文件夹下的pywander.json
    来配置 PROCESS_TEXT: [] 字段来设计一系列的文本处理步骤
    其内的单个动作配置如下：
    {"OPERATION": "remove_english_line",
    }
    该动作可以添加其他值作为目标函数的可选参数


    INFILE: the input file
    """
    from .process_text import process_text
    process_text(infile)


@main.command()
@click.argument('infile')
@click.option('--outputformat', default='epub')
@click.option('--metadata', default='epub.yaml')
@click.option('--resource', default='figures')
def convert(infile, outputformat, metadata, resource):
    """
    利用pandoc进行文档转换

    专门对tex输出epub进行了一些优化

    INFILE: the input file
    """
    out_result = None

    if outputformat == 'epub':
        from .pandoc import convert_tex_to_epub
        out_result = convert_tex_to_epub(infile, metadata, resource)
    else:
        click.echo("暂不支持")

    if out_result:
        click.echo("process: {} done.".format(out_result))
    else:
        click.echo("process: {} failed.".format(out_result))


if __name__ == '__main__':
    main()