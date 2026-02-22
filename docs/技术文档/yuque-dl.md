# 语雀知识库下载工具

https://github.com/gxr404/yuque-dl

语雀知识库下载为本地markdown

## Install

npm i -g yuque-dl

## Usage

```
$ yuque-dl --help

  Usage:
    $ yuque-dl <url>

  Commands:
    <url>                语雀知识库url
    server <serverPath>  启动web服务

  For more info, run any command with the `--help` flag:
    $ yuque-dl --help
    $ yuque-dl server --help

  Options:
    -d, --distDir <dir>                  下载的目录
                                          └─ eg: -d download (默认值: download)
    -i, --ignoreImg                      忽略图片不下载 (默认值: false)
    --ignoreAttachments [fileExtension]  忽略附件, 可选带上忽略的附件文件后缀(多种后缀逗号分割)
                                          └─ eg: --ignoreAttachments mp4,pdf // 忽略后缀名mp4,pdf的附件
                                          └─ eg: --ignoreAttachments // 忽略所有附件 (默认值: false)
    -k, --key <key>                      语雀的cookie key， 默认是 "_yuque_session"， 在某些企业版本中 key 不一样
    -t, --token <token>                  语雀的cookie key 对应的值 
    --toc                                是否输出文档toc目录 (默认值: false)
    --incremental                        开启增量下载[初次下载加不加该参数没区别] (默认值: false)
    --convertMarkdownVideoLinks          转化markdown视频链接为video标签 (默认值: false)
    --hideFooter                         是否禁用页脚显示[更新时间、原文地址...] (默认值: false)
    -h, --help                           显示帮助信息
    -v, --version                        显示当前版本
```

