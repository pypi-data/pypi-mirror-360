# pywander
文本处理工具集

## USAGE
```
pip install pywander-text
```


## Console Scripts
### pywander_text_web
将会打开网页端，很多文本处理工具整合在里面。

已有的工具：

- 繁体简体转换
- 汉字转拼音
- 作者国籍名缩写规范检测
- 正则表达式匹配替换
- 字符乱码侦测


### pywander_text
命令行工具，在某些情况下用命令行工具会更方便一些。

猜测某个乱码字符串的可能正确编码
```text
pywander_text encoding 濉旂撼鎵樻媺闆呯殑钁ぜ
```

将某一字符串转成拼音并用某个连接符号连接起来
```text
pywander_text pinyin 塔纳托拉雅的葬礼
```
选择连接符号
```text
pywander_text pinyin 塔纳托拉雅的葬礼 --hyphen=_
```

利用pandoc进行文档转换

专门对tex输出epub进行了一些优化

```text
pywander_text.exe  convert main.tex
```


对当前文件夹下的某个文件执行某个脚本处理动作
    
你可以在当前文件夹下的pywander.json
来配置 PROCESS_TEXT: [] 字段来设计一系列的文本处理步骤
其内的单个动作配置如下：
{"OPERATION": "remove_english_line",
}
该动作可以添加其他值作为目标函数的可选参数

```text
pywander_text.exe process test.txt
```



## TEST
local environment run 
```
pip install -e .
```
and run 

```
pytest
```
