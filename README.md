# KDE Icon Theme Colorizer

一个用于为 KDE Plasma 图标主题（特别是 Papirus）注入系统配色支持的 Python 自动化工具。

## 核心特性

- **明度智能分析**：自动计算 SVG 图标中颜色的相对明度。明度最高的颜色被映射为 `ColorScheme-Accent`（随系统强调色变化），较低明度的部分被映射为 `ColorScheme-Text`（保持细节可见）。
- **KDE 原生颜色集成**：向 SVG 中注入 `<style>` 定义，使图标能响应 KDE 系统配色方案（Color Scheme）的实时切换。
- **软链接处理策略**：智能识别图标主题中的软链接。当通用图标（如 `folder.svg`）链接到特定颜色的变体（如 `folder-blue.svg`）时，工具会重构链接，将其替换为已注入配色代码的实文件。
- **安全保障**：内置 `dry-run` 试运行模式和自动备份 (`.bak`) 机制。

## 安装要求

- Python 3.8+
- 对于 Python < 3.11，需要安装 `tomli`：`pip install tomli`

## 快速上手

### 1. 试运行 (Dry-run)
在实际修改前，建议先查看哪些文件将被处理：
```bash
python3 src/main.py --dry-run /path/to/Papirus/64x64/places
```

### 2. 执行着色处理
```bash
python3 src/main.py /path/to/Papirus/64x64/places
```
执行后，脚本会请求确认，并在修改前为每个文件生成 `.bak` 备份。

### 3. 命令行参数说明
- `target_dir`: 目标图标目录（如 Papirus 的 `places` 或 `apps` 目录）。
- `--dry-run`: 仅扫描并计算，不修改磁盘文件。
- `--no-backup`: 修改时不生成备份文件。
- `-y`, `--yes`: 自动确认，适用于自动化脚本或 NixOS 构建。

## NixOS 使用指南

在 NixOS 中，`/run/current-system/sw/share/icons` 下的图标目录是只读的，且受到 Nix 存储哈希校验的保护。你**不能**直接对系统目录运行此脚本。

### 方案 A：用户级覆盖 (简单)
1. 将图标主题复制到用户目录：
   ```bash
   mkdir -p ~/.local/share/icons
   cp -r /run/current-system/sw/share/icons/Papirus ~/.local/share/icons/Papirus-Colorized
   ```
2. 对副本运行脚本：
   ```bash
   python3 src/main.py ~/.local/share/icons/Papirus-Colorized
   ```
3. 在 KDE 系统设置中选择 `Papirus-Colorized`。

### 方案 B：Nix 原生集成 (推荐)

本项目提供了完整的 Flake 支持和 Overlay。你可以直接在 NixOS 或 Home Manager 中使用它来生成已着色的图标包。

#### 1. 在 Flake 中引用
```nix
inputs.kde-colorizer.url = "github:sterlingshell/KDE_Icon_Theme_Colorizer/nixpkg-test";
```

#### 2. 应用 Overlay 并安装图标
在你的 NixOS 或 Home Manager 配置中：

```nix
{ pkgs, inputs, ... }: {
  nixpkgs.overlays = [ inputs.kde-colorizer.overlays.default ];

  # 系统级安装 (NixOS)
  environment.systemPackages = [
    (pkgs.papirus-icon-theme-colorized { themeVariant = "Papirus-Dark"; })
  ];

  # 或 用户级安装 (Home Manager)
  home.packages = [
    (pkgs.papirus-icon-theme-colorized { themeVariant = "Papirus-Light"; })
  ];

  # 可选：通过 Home Manager 自动设置图标主题
  gtk.iconTheme = {
    name = "Papirus-Light-Colorized";
    package = pkgs.papirus-icon-theme-colorized { themeVariant = "Papirus-Light"; };
  };
}
```

## 配置说明 (config.toml)

你可以通过项目根目录下的 `config.toml` 调整扫描策略：
- `symlink_keywords`: 触发软链接重构的关键字（如 "folder", "user"）。
- `standalone_apps`: 需要强制处理的独立 SVG 文件列表。
- `standalone_regex_patterns`: 使用正则表达式匹配需要处理的独立文件。

## 许可证
MIT License
