import re
from config import IGNORE_COLORS, CSS_DEFS


def get_luminance(hex_str):
    """计算颜色的相对明度 (Luminance)"""
    hex_str = hex_str.lstrip('#').lower()
    if len(hex_str) == 3:
        hex_str = ''.join(c * 2 for c in hex_str)
    try:
        r, g, b = tuple(int(hex_str[i:i + 2], 16) for i in (0, 2, 4))
        return 0.299 * r + 0.587 * g + 0.114 * b
    except ValueError:
        return 255


def analyze_and_modify_svg(content):
    """解析 SVG 颜色并进行透明度计算与替换"""
    if "current-color-scheme" in content:
        return content, False

    colors = re.findall(r'#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})\b', content)
    colors = set('#' + c.lower() for c in colors)
    theme_colors = [c for c in colors if c not in IGNORE_COLORS]

    if not theme_colors:
        return content, False

    color_y = {c: get_luminance(c) for c in theme_colors}
    sorted_colors = sorted(color_y.keys(), key=lambda c: color_y[c], reverse=True)

    c_main = sorted_colors[0]
    y_main = color_y[c_main]

    # 注入样式表
    content = re.sub(r'(<svg[^>]*>)', rf'\1\n{CSS_DEFS}', content, count=1, flags=re.IGNORECASE)

    def process_tag(match, color, mode):
        tag = match.group(0)
        y_sub = color_y[color]
        tag_mod = re.sub(color, 'currentColor', tag, flags=re.IGNORECASE)

        if mode == 'main':
            if '/>' in tag_mod:
                tag_mod = tag_mod.replace('/>', ' class="ColorScheme-Accent"/>')
            else:
                tag_mod = tag_mod.replace('>', ' class="ColorScheme-Accent">')
            return tag_mod

        elif mode == 'back':
            alpha = max(0.0, min(1.0, (y_main - y_sub) / y_main))
            if '/>' in tag_mod:
                tag_mod = tag_mod.replace('/>', ' class="ColorScheme-Accent"/>')
            else:
                tag_mod = tag_mod.replace('>', ' class="ColorScheme-Accent">')

            tag_dup = re.sub(color, '#000000', tag, flags=re.IGNORECASE)
            if 'style="' in tag_dup:
                tag_dup = re.sub(r'style="([^"]*)"', rf'style="\1; fill-opacity:{alpha:.2f}"', tag_dup)
            else:
                tag_dup = tag_dup.replace('>', f' fill-opacity="{alpha:.2f}">')
            return f'{tag_mod}\n{tag_dup}'

        elif mode == 'icon':
            alpha = max(0.0, min(1.0, (y_main - y_sub) / max(y_main, 1)))
            if 'style="' in tag_mod:
                tag_mod = re.sub(r'style="([^"]*)"', rf'style="\1; fill-opacity:{alpha:.2f}"', tag_mod)
            else:
                tag_mod = tag_mod.replace('>', f' fill-opacity="{alpha:.2f}">')

            if '/>' in tag_mod:
                tag_mod = tag_mod.replace('/>', ' class="ColorScheme-Text"/>')
            else:
                tag_mod = tag_mod.replace('>', ' class="ColorScheme-Text">')
            return tag_mod

    for i, color in enumerate(sorted_colors):
        mode = 'main'
        if i == 1:
            mode = 'back'
        elif i >= 2:
            mode = 'icon'

        pattern = r'<[^>]*?(?:' + color + r')[^>]*?>'
        content = re.sub(pattern, lambda m: process_tag(m, color, mode), content, flags=re.IGNORECASE)

    return content, True