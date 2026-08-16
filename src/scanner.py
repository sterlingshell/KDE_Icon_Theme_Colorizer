import os
from config import VARIANTS, SYMLINK_KEYWORDS, STANDALONE_APPS, STANDALONE_REGEXES


def has_variant(filename):
    parts = filename.replace('.svg', '').split('-')
    return any(p in VARIANTS for p in parts)


def is_standalone_target(filename):
    # 先做 O(1) 的完全匹配字典检索，再做正则检索，性能最优
    if filename in STANDALONE_APPS:
        return True
    return any(regex.match(filename) for regex in STANDALONE_REGEXES)


def scan_directory(target_dir):
    tasks = []

    for root, _, files in os.walk(target_dir):
        for f in files:
            if not f.endswith('.svg'):
                continue

            path = os.path.join(root, f)

            # 策略 A: 处理独立实际文件
            if not os.path.islink(path):
                if is_standalone_target(f):
                    tasks.append({
                        'target_path': path,
                        'source_path': path,
                        'is_symlink': False
                    })
                continue

            # 策略 B: 处理多级软链接
            if any(kw in f for kw in SYMLINK_KEYWORDS):
                real_target = os.path.realpath(path)
                if not os.path.exists(real_target):
                    continue

                f_has_variant = has_variant(f)
                target_has_variant = has_variant(os.path.basename(real_target))

                if not f_has_variant and target_has_variant:
                    tasks.append({
                        'target_path': path,
                        'source_path': real_target,
                        'is_symlink': True
                    })

    return tasks