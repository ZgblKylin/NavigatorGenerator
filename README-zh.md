# NavigatiorGenerator

静态HTML导航页面生成器。

## 说明

静态HTML导航页面生成器，灵感来自[soulteary/flare](https://github.com/soulteary/docker-flare)。

特性：

- 可由yaml配置文件自定义。
- 超快速的静态HTML。
- 自适应黑暗模式。
- 响应式布局。
- emoji和Material Design图标支持。

## 要求

- Python 3
  - emoji
  - pillow
  - pyyaml

## 使用方式

`python3 generator.py [-o,--output index.html] config.yaml`

如果`output`未设置，则html结果将被输出至stdout。

范例配置和生成的html详见`/example`。

生成html的Google Chrome lighthouse报告（使用Nginx托管，启用gzip压缩支持）：
![lighthouse报告](example/lighthouse.png)
