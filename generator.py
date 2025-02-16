# -*- coding: utf-8 -*-
import argparse as argparse
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

import emoji
import favicon
import regex
import requests
import yaml

config = []
config_path = ''
config_dir = ''
output_dir = ''
output_path = ''


def ParseConfig():
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
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


def LoadIcon(lines: List[str], title: str, class_name: str, icon: str,
             indent: str = "", optional: bool = False, max_retry: int = 10):
    max_retry = max_retry + 1 if max_retry and max_retry > 0 else 1
    favicon_dir = os.path.join(output_dir, 'favicon')
    if output_dir:
        os.makedirs(favicon_dir, exist_ok=True)

    # emoji name
    if icon.startswith(":") and icon.endswith(":"):
        lang = config['lang'].split("-")[0]
        text = emoji.emojize(icon, language=lang)
        if text == icon:
            text = emoji.emojize(icon)
        lines.append(f'{indent}<div class="{class_name}">')
        lines.append(f'{indent}  <div class="emoji">{text}</div>')
        lines.append(f'{indent}</div>')
        return

    # emoji character
    is_emoji = False
    for _ in emoji.analyze(icon):
        is_emoji = True
    if is_emoji:
        lines.append(f'{indent}<div class="{class_name}">')
        lines.append(f'{indent}  <div class="emoji">{icon}</div>')
        lines.append(f'{indent}</div>')
        return

    # url
    if regex.match(r'^\w+://', icon):
        def Request(url) -> requests.Response:
            response = requests.Response()
            response.status_code = 404
            for _ in range(max_retry):
                try:
                    HEADERS = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) '
                        'AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/33.0.1750.152 Safari/537.36'
                    }
                    response = requests.get(url,
                                            headers=HEADERS,
                                            allow_redirects=True)
                    if response.status_code == 200:
                        break
                except Exception:
                    pass
            return response

        # Check if favicon already exists
        if output_dir:
            for root, _, files in os.walk(favicon_dir):
                for file in files:
                    if file.startswith(title):
                        path = os.path.join(root, file)
                        path = os.path.relpath(path, output_dir)
                        path = path.replace(os.sep, '/')
                        lines.append(f'{indent}<div class="{class_name}">')
                        lines.append(
                            f'{indent}  <img src="{path}" alt="icon"/>')
                        lines.append(f'{indent}</div>')
                        return

        response = Request(icon)
        if response.status_code != 200:
            if optional:
                print(f"Warning: cannot access {title}'s icon url, "
                      f"skip it: {icon}")
                return
            else:
                print(f"Error: cannot access {title}'s icon url: {icon}")
                sys.exit(1)
        _, suffix = os.path.splitext(response.url)
        if suffix.lower() not in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico']:
            # 'icon' is a website, not a file
            icons = []
            for _ in range(max_retry):
                try:
                    icons = favicon.get(icon)
                    break
                except Exception:
                    pass
            if not icons:
                print(f"Error: Cannot load favicon for {title} from: {icon}")
                sys.exit(1)
            suffix = None
            # prefer svg > ico > png > others
            for format in ['svg', 'ico', 'png']:
                for i in icons:
                    if i.format == format:
                        icon = i.url
                        suffix = '.' + format
                        break
                if suffix:
                    break
            if not suffix:
                icon = icons[0].url
                _, suffix = os.path.splitext(icon)
            response = Request(icon)
            if response.status_code != 200:
                if optional:
                    print(f"Warning: cannot access {title}'s icon url, "
                          f"skip it: {icon}")
                    return
                else:
                    print(f"Error: cannot access {title}'s icon url: {icon}")
                    sys.exit(1)
        if output_dir:
            path = os.path.join(favicon_dir, title + suffix)
            with open(path, 'wb') as f:
                f.write(response.content)
        else:
            # Skip save icon file since output_file not given
            pass
        lines.append(f'{indent}<div class="{class_name}">')
        path = os.path.relpath(path, output_dir)
        path = path.replace(os.sep, '/')
        lines.append(f'{indent}  <img src="{path}" alt="icon"/>')
        lines.append(f'{indent}</div>')  # class_name
        return

    # existing file
    path = icon.replace('/', os.sep).replace('\\', os.sep)
    if os.path.isfile(path):
        # absolute path or realtive to pwd
        pass
    if not os.path.isfile(path):
        # try relative to config file directory
        path = os.path.join(config_dir, icon).replace(
            '/', os.sep).replace('\\', os.sep)
        if not os.path.isfile(path) and output_path:
            # try relative to output file directory
            path = os.path.join(output_dir, icon).replace(
                '/', os.sep).replace('\\', os.sep)
    if os.path.isfile(path):
        # found icon file
        if output_dir:
            dest = os.path.join(favicon_dir, os.path.basename(path))
            if os.path.abspath(path) != os.path.abspath(dest):
                # copy to favicon_dir
                try:
                    with open(path, 'rb') as f:
                        with open(dest, 'wb') as d:
                            d.write(f.read())
                except Exception as e:
                    print(
                        f"Error copying {title}'s icon file from {path} to {dest}: {e}")
                    sys.exit(1)
            icon = os.path.relpath(dest, output_dir)
        else:
            # Skip copy icon file since output_file not given
            pass
        icon = icon.replace(os.sep, '/')
        lines.append(f'{indent}<div class="{class_name}">')
        lines.append(f'{indent}  <img src="{icon}" alt="icon"/>')
        lines.append(f'{indent}</div>')  # class_name
        return

    # Fallback to material design icons
    dir = os.path.dirname(os.path.abspath(__file__))
    name = ''.join(['-' + i.lower() if i.isupper()
                   else i for i in icon]).lstrip('-')
    file = os.path.join(dir, 'assets', 'MaterialDesign', 'svg', name + '.svg')
    if not os.path.isfile(file):
        print(f"Error: {icon} is not a valid icon")
        sys.exit(1)
    lines.append(f'{indent}<div class="{class_name}">')
    try:
        with open(file, 'r', encoding='utf-8') as f:
            text = f.read()
            lines.append(f'{indent}  {text.strip()}')
    except Exception:
        if optional:
            print(f"Warning: unknwon icon for {title}: {icon}")
            return
        else:
            print(f"Error: unknwon icon for {title}: {icon}")
            sys.exit(1)
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
                    LoadIcon(lines, name, 'icon', icon, indent="    ")
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
                        LoadIcon(lines, name, 'category-icon',
                                 icon, indent="    ", optional=True)
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
    config_path = os.path.abspath(args.config)
    output_path = os.path.abspath(args.output)
    config_dir = os.path.dirname(config_path)
    output_dir = os.path.dirname(output_path)

    ParseConfig()
    template = LoadTemplate()
    html = GenerateHtml(template)
    OutputHtml(html)
