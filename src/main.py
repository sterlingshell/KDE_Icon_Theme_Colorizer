#!/usr/bin/env python3
import os
import sys
import argparse
import shutil
from scanner import scan_directory
from colorizer import analyze_and_modify_svg


def main():
    parser = argparse.ArgumentParser(description="KDE 图标主题颜色处理工具")
    parser.add_argument("target_dir", help="Papirus 图标的 places/apps 目录路径")
    parser.add_argument("--dry-run", action="store_true", help="试运行模式，不进行实际修改")
    parser.add_argument("--no-backup", action="store_true", help="不生成 .bak 备份文件")
    parser.add_argument("-y", "--yes", action="store_true", help="自动确认并执行修改（非交互模式）")

    args = parser.parse_args()

    if not os.path.isdir(args.target_dir):
        print(f"错误: 提供的路径 '{args.target_dir}' 不是一个有效的目录。")
        sys.exit(1)

    if args.dry_run:
        print(">>> 试运行模式已开启，将不会修改任何文件 <<<\n")

    print("正在扫描目录并解析对象...")
    tasks = scan_directory(args.target_dir)

    if not tasks:
        print("没有找到符合条件的待处理文件。")
        sys.exit(0)

    print(f"\n检测到 {len(tasks)} 个目标将要被处理。")
    print("示例:")
    for task in tasks[:5]:
        action = "[软链接重构]" if task['is_symlink'] else "[直接覆盖]"
        print(f" - {action} {os.path.basename(task['target_path'])} (源: {os.path.basename(task['source_path'])})")

    if len(tasks) > 5:
        print("   ...")

    if not args.dry_run and not args.yes:
        confirm = input("\n确认要执行替换和注入操作吗？(y/n): ").strip().lower()
        if confirm != 'y':
            print("操作已取消。")
            sys.exit(0)
    else:
        if args.dry_run:
            print("\n试运行模式跳过确认步骤。")
        else:
            print("\n已启用 --yes 参数，自动开始处理...")

    success_count = 0
    for task in tasks:
        target_path = task['target_path']
        source_path = task['source_path']

        try:
            with open(source_path, 'r', encoding='utf-8') as file:
                content = file.read()

            new_content, modified = analyze_and_modify_svg(content)

            if modified:
                if args.dry_run:
                    print(f"[DRY-RUN] 准备处理: {target_path}")
                    success_count += 1
                    continue

                # 备份逻辑
                if not args.no_backup:
                    backup_path = target_path + ".bak"
                    if not os.path.exists(backup_path):
                        shutil.copy2(target_path, backup_path)

                # 执行修改
                if task['is_symlink']:
                    os.remove(target_path)

                with open(target_path, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                
                success_count += 1
        except Exception as e:
            print(f"处理文件 {target_path} 时失败: {e}")

    if args.dry_run:
        print(f"\n试运行完成！模拟处理了 {success_count} 个文件。")
    else:
        print(f"\n操作完成！共成功处理 {success_count} 个文件。")
        print("请在 KDE 系统设置中重新应用图标主题，或重启 plasmashell 以查看效果。")


if __name__ == "__main__":
    main()
