# NavigatiorGenerator

[中文](README-zh.md)

Static HTML navigation page generator. [Example](https://zgblkylin.github.io/NavigatorGenerator/)

## Description

Static HTML navigation page generator inspired by [soulteary/flare](https://github.com/soulteary/docker-flare).

Features:

- Customizable by yaml config file.
- Blazing fast with static HTML.
- Auto adapt to dark mode.
- Responsive layout.
- Emoji and Material Design Icons support.

## Requirements

- Python 3
  - emoji
  - pillow
  - pyyaml

## Usage

`python3 generator.py [-o,--output index.html] config.yaml`

If `output` not given, the generated html will be printed to stdout.

See `/example` for an example config file and `/doc` or [GitHub Pages](https://zgblkylin.github.io/NavigatorGenerator/) for generated html.

Google Chrome lighthouse report for the generated html(hosted on Nginx with gzip compression enabled):
![lighthouse report](example/lighthouse.png)
