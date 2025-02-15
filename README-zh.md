# NavigatiorGenerator

静态HTML导航页面生成器。[范例](https://zgblkylin.github.io/NavigatorGenerator/)

## 说明

静态HTML导航页面生成器，灵感来自[soulteary/flare](https://github.com/soulteary/docker-flare)。

特性：

- 可由yaml配置文件自定义。
- 超快速的静态HTML。
- 自适应黑暗模式。
- 响应式布局。
- emoji和Material Design图标支持。

## 要求

Python 3，包列表：

- BeautifulSoup
- emoji
- favicon
- pyyaml
- regex
- request

## 使用方式

`python3 generator.py [-o,--output index.html] config.yaml`

如果`output`未设置，则html结果将被输出至stdout。

范例配置详见`/example`，生成的html详见`/doc`或者[GitHub Pages](https://zgblkylin.github.io/NavigatorGenerator/)。

生成html的Google Chrome lighthouse报告（使用Nginx托管，启用gzip压缩支持）：
![lighthouse报告](example/lighthouse.png)

## TODO

- 增加日志输出
