import os
import sys
from scanner import scan_directory
from colorizer import analyze_and_modify_svg


def main():
    if len(sys.argv) < 2:
        print(f"用法: python3 {sys.argv[0]} <Papirus 图标的 places/apps 目录路径>")
        sys.exit(1)

    target_dir = sys.argv[1]
    if not os.path.isdir(target_dir):
        print("错误: 提供的路径不是一个有效的目录。")
        sys.exit(1)

    print("正在扫描目录并解析对象...")
    tasks = scan_directory(target_dir)

    if not tasks:
        print("没有找到符合条件的待处理文件。")
        sys.exit(0)

    print(f"\n检测到 {len(tasks)} 个目标将要被处理。")
    print("示例:")
    for task in tasks[:5]:
        if task['is_symlink']:
            print(
                f" - [软链接重构] {os.path.basename(task['target_path'])} (源: {os.path.basename(task['source_path'])})")
        else:
            print(f" - [直接覆盖]   {os.path.basename(task['target_path'])}")

    if len(tasks) > 5: print("   ...")

    confirm = input("\n确认要执行替换和注入操作吗？(y/n): ").strip().lower()
    if confirm != 'y':
        print("操作已取消。")
        sys.exit(0)

    success_count = 0
    for task in tasks:
        target_path = task['target_path']
        source_path = task['source_path']

        try:
            with open(source_path, 'r', encoding='utf-8') as file:
                content = file.read()

            new_content, modified = analyze_and_modify_svg(content)

            if modified:
                if task['is_symlink']:
                    os.remove(target_path)

                with open(target_path, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                success_count += 1
        except Exception as e:
            print(f"处理文件 {target_path} 时失败: {e}")

    print(f"\n操作完成！共成功处理 {success_count} 个文件。")
    print("请在 KDE 系统设置中重新应用图标主题，或重启 plasmashell 以查看效果。")


if __name__ == "__main__":
    main()