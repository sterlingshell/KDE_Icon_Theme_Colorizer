import os
import re
import sys

# 兼容 Python 3.11+ 的内置 tomllib
if sys.version_info >= (3, 11):
    import tomllib
else:
    # 兼容老版本 Python 的备用方案
    try:
        import tomli as tomllib
    except ImportError:
        print("错误: 您的 Python 版本低于 3.11，请先运行 'pip install tomli' 安装 TOML 解析库。")
        sys.exit(1)

# 核心系统配色定义（不建议用户轻易修改，保留在源码中）
CSS_DEFS = '''<defs id="defs_plasma_colors">
  <style type="text/css" id="current-color-scheme">
    .ColorScheme-Text { color:#31363b; }
    .ColorScheme-Accent { color:#5294e2; }
  </style>
</defs>'''

IGNORE_COLORS = {'#ffffff', '#fff', '#000000', '#000', '#e4e4e4'}
VARIANTS = {
    'adwaita', 'black', 'blue', 'bluegrey', 'breeze', 'brown', 'carmine', 'cyan',
    'darkcyan', 'deeporange', 'green', 'grey', 'indigo', 'magenta', 'nordic',
    'orange', 'palebrown', 'paleorange', 'pink', 'red', 'teal', 'violet', 'white',
    'yaru', 'yellow'
}

# 动态加载外部配置文件
TOML_PATH = os.getenv("KDE_COLORIZER_CONFIG")
if not TOML_PATH:
    TOML_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.toml")

if not os.path.exists(TOML_PATH):
    print(f"错误: 未在项目根目录下找到配置文件 {TOML_PATH}")
    sys.exit(1)

with open(TOML_PATH, "rb") as f:
    _data = tomllib.load(f)

# 导出给其他模块使用的配置项
SCANNER_CFG = _data.get("scanner", {})
SYMLINK_KEYWORDS = SCANNER_CFG.get("symlink_keywords", ["folder", "user"])
STANDALONE_APPS = set(SCANNER_CFG.get("standalone_apps", []))

# 在内存中自动将配置文件的字符串编译为正则对象
STANDALONE_REGEXES = [re.compile(p) for p in SCANNER_CFG.get("standalone_regex_patterns", [])]