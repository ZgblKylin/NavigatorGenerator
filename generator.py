# -*- coding: utf-8 -*-
import argparse as argparse
import base64
import os
import sys
import tempfile
from typing import Any, Dict, List, Optional, Tuple

import emoji
import yaml
from PIL import Image

config = []
config_path = ''
output_path = None


def ParseConfig(config_file):
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            global config
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"Error reading config file: {e}")
        sys.exit(1)


def LoadTemplate() -> str:
    try:
        dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(dir, "assets", "index.template.html"), 'r', encoding='utf-8') as f:
            template = f.read()
            return template
    except Exception as e:
        print(f"Error reading template file: {e}")
        sys.exit(1)


def ImageToBase64(path: str) -> str:
    try:
        image = Image.open(path)
        if image.size[0] >= 64 or image.size[1] >= 64:
            ratio = min(64 / image.size[0], 64 / image.size[1])
            image = image.resize(
                (int(image.size[0] * ratio), int(image.size[1] * ratio)))
            # open temp file
            _, suffix = os.path.splitext(path)
            temp_path = os.path.join(os.path.dirname(path), 'temp' + suffix)
            image.save(temp_path, format=image.format)
            content = open(temp_path, 'rb').read()
        else:
            content = open(path, 'rb').read()
        return base64.b64encode(content).decode('utf-8')
    except Exception as e:
        print(f"Error reading image file: {e}")
        sys.exit(1)


def SvgToBase64(path: str) -> str:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            return base64.b64encode(content.encode('utf-8')).decode('utf-8')
    except Exception as e:
        print(f"Error reading svg file: {e}")
        sys.exit(1)


def IcoToBase64(path: str) -> str:
    # get last image less than 64x64 in ico
    try:
        from PIL import Image
        image = Image.open(path)
        if image.size[0] >= 64 or image.size[1] >= 64:
            ratio = min(64 / image.size[0], 64 / image.size[1])
            image = image.resize(
                (int(image.size[0] * ratio), int(image.size[1] * ratio)))
            with tempfile.TemporaryFile(suffix='.ico') as temp:
                image.save(temp, format=image.format)
                temp.seek(0)
                content = temp.read()
        else:
            content = open(path, 'rb').read()
        return base64.b64encode(content).decode('utf-8')
    except Exception as e:
        print(f"Error reading ico file: {e}")
        sys.exit(1)


def LoadIcon(lines: List[str], class_name: str, icon: str, indent: str = ""):
    if icon.startswith(":") and icon.endswith(":"):
        lang = config['lang'].split("-")[0]
        text = emoji.emojize(icon, language=lang)
        if text == icon:
            text = emoji.emojize(icon)
        lines.append(f'{indent}<div class="{class_name}">{text}</div>')
        return

    is_emoji = False
    for _ in emoji.analyze(icon):
        is_emoji = True
    if is_emoji:
        lines.append(f'{indent}<div class="{class_name}">')
        lines.append(f'{indent}  <div class="emoji">{icon}</div>')
        lines.append(f'{indent}</div>')
        return

    # Check if `icon` is existing file
    path = icon
    if not os.path.isfile(path):
        dir = os.path.dirname(os.path.abspath(config_path))
        path = os.path.join(dir, icon)
        if output_path and not os.path.isfile(path):
            dir = os.path.dirname(os.path.abspath(output_path))
            path = os.path.join(dir, icon)
    if os.path.isfile(path):
        _, suffix = os.path.splitext(path)
        suffix = suffix.lower()
        lines.append(f'{indent}<div class="{class_name}">')
        lines.append(f'{indent}  <img src="{icon}" alt="icon"/>')
        lines.append(f'{indent}</div>')  # class_name
        return

    # Fallback to material design icons
    dir = os.path.dirname(os.path.abspath(__file__))
    icon = ''.join(['-' + i.lower() if i.isupper()
                   else i for i in icon]).lstrip('-')
    file = os.path.join(dir, 'assets', 'MaterialDesign', 'svg', icon + '.svg')
    if not os.path.isfile(file):
        print(f"Error: {icon} is not a valid icon")
        sys.exit(1)
    lines.append(f'{indent}<div class="{class_name}">')
    with open(file, 'r', encoding='utf-8') as f:
        text = f.read()
        lines.append(f'{indent}  {text.strip()}')
    lines.append(f'{indent}</div>')  # class_name
    return


def GenerateHtml(template: str) -> str:
    template = template.split("\n")

    def FindLine(token: str, cur: int = 0) -> Optional[int]:
        for i in range(cur, len(template)):
            if token in template[i]:
                return i
        print(f"Error: {token} not found in template")
        sys.exit(1)

    cur = FindLine('@lang@')
    lang = config['lang']
    template[cur] = template[cur].replace('@lang@', lang)

    cur = FindLine('@description@')
    if 'description' in config:
        description = config['description']
    else:
        description = config['title']
    template[cur] = template[cur].replace('@description@', description)

    cur = FindLine('@favicon@')
    if 'favicon' in config:
        favicon = config['favicon']
        template[cur] = f'  <link rel="shortcut icon" href="{favicon}">'
    else:
        template.pop(cur)

    cur = FindLine('@title@')
    title = config['title']
    template[cur] = template[cur].replace('@title@',
                                          title if title else "Navigation")

    cur = FindLine('@greeting@')
    greeting = config['greeting']
    template[cur] = template[cur].replace('@greeting@',
                                          greeting if greeting else "Hello!")

    cur = FindLine('@groups@')
    groups = config['groups']

    groups_lines = []
    for group in groups:
        name = group['name']
        open_new_tab = group['open-new-tab'] if 'open-new-tab' in group else False
        target = '_blank' if open_new_tab else '_self'
        target = f'target="{target}" rel="noopener noreferrer"'

        group_lines = []
        group_lines.append(f'<div id="group" class="group">')

        container_lines = []
        container_lines.append(f'<h2>{name}</h2>')

        if 'links' in group:
            links = group['links']
            container_lines.append('<div class="container clearfix">')
            for entry in links:
                name = entry['name']
                link = entry['link']
                icon = entry['icon'] if 'icon' in entry else ''
                desc = entry['desc'] if 'desc' in entry else link
                tooltip = entry['desc'] if 'desc' in entry else name
                lines = []
                lines.append(f'<div class="button">')
                lines.append(
                    f'  <a class="button-item" {target} href="{link}" title="{tooltip}">')
                if icon:
                    LoadIcon(lines, 'icon', icon, indent="    ")
                lines.append(f'    <div class="text">')
                lines.append(f'      <div class="title">{name}</div>')
                lines.append(f'      <div class="description">{desc}</div>')
                lines.append(f'    </div>')  # text
                lines.append(f'  </a>')  # button-item
                lines.append(f'</div>')  # button
                container_lines.append(lines)
            container_lines.append('</div>')  # container
        elif 'categories' in group:
            categories = group['categories']
            container_lines.append('<div class="category clearfix">')
            for category in categories:
                name = category['name']
                links = category['links']
                cc_lines = []  # category container
                cc_lines.append(f'<div class="category-container">')
                cl_lines = []  # category list
                cl_lines.append(f'<h3 class="category-title">{name}</h3>')
                cl_lines.append(f'<ul class="category-list">')
                for entry in links:
                    name = entry['name']
                    link = entry['link']
                    icon = entry['icon'] if 'icon' in entry else ''
                    tooltip = entry['desc'] if 'desc' in entry else name
                    lines = []
                    lines.append(f'<li>')
                    lines.append(
                        f'  <a class="category-item" {target} href="{link}" title="{tooltip}">')
                    if icon:
                        LoadIcon(lines, 'category-icon', icon, indent="    ")
                    lines.append(f'    <span>{name}</span>')
                    lines.append(f'  </a>')
                    lines.append(f'</li>')
                    cl_lines.append(lines)
                cl_lines.append(f'</ul>')  # category-list
                cc_lines.append(cl_lines)
                cc_lines.append(f'</div>')  # category-container
                container_lines.append(cc_lines)
            container_lines.append('</div>')  # category

        group_lines.append(container_lines)
        group_lines.append('</div>')  # group
        groups_lines.append(group_lines)

    html = []
    for lines in groups_lines:
        def AppendLines(html: List[str], lines: Any, indent: int) -> None:
            if isinstance(lines, list):
                for line in lines:
                    AppendLines(html, line, indent + 1)
            elif isinstance(lines, str):
                html.append('  ' * indent + lines)
            else:
                print(f"Error: {lines} is not a string or list")
                sys.exit(1)
        AppendLines(html, lines, 1)
    template[cur] = '\n'.join(html)

    cur = FindLine('@footer@')
    if config['lang'].startswith('zh'):
        template[cur] = template[cur].replace(
            '@footer@', '由 ZgblKylin/NavigatorGenerator 强力驱动')
    else:
        template[cur] = template[cur].replace(
            '@footer@', 'Powered by ZgblKylin/NavigatiorGenerator')

    return '\n'.join(template)


def OutputHtml(html: str) -> None:
    if output_path:
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
        except Exception as e:
            print(f"Error writing output file: {e}")
            sys.exit(1)
    else:
        print(html)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="The output file to write the generated html to. Defaults to stdout."
    )
    parser.add_argument(
        "config",
        type=str,
        help="The config file to use.",
    )
    args = parser.parse_args()
    if not args.config:
        print("Error: config file is required")
        sys.exit(1)
    config_path = args.config
    output_path = args.output

    ParseConfig(args.config)
    template = LoadTemplate()
    html = GenerateHtml(template)
    OutputHtml(html)
