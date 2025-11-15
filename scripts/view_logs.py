"""日志查看工具"""

import sys
from pathlib import Path
import argparse
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))


def view_log_file(log_file: Path, lines: int = 50, follow: bool = False, level: str = None):
    """
    查看日志文件

    Args:
        log_file: 日志文件路径
        lines: 显示最后N行
        follow: 是否实时跟踪
        level: 过滤日志级别
    """
    if not log_file.exists():
        print(f"❌ 日志文件不存在: {log_file}")
        return

    print(f"\n{'=' * 80}")
    print(f"📄 日志文件: {log_file.name}")
    print(f"📅 修改时间: {datetime.fromtimestamp(log_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 文件大小: {log_file.stat().st_size / 1024:.2f} KB")
    print(f"{'=' * 80}\n")

    try:
        if follow:
            # 实时跟踪模式
            print("🔄 实时跟踪模式（Ctrl+C 退出）\n")
            import subprocess
            subprocess.run(['tail', '-f', str(log_file)])
        else:
            # 读取最后N行
            with open(log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()

            # 过滤日志级别
            if level:
                level_upper = level.upper()
                filtered_lines = [line for line in all_lines if level_upper in line]
            else:
                filtered_lines = all_lines

            # 显示最后N行
            display_lines = filtered_lines[-lines:] if lines else filtered_lines

            for line in display_lines:
                # 为不同级别添加颜色
                if 'ERROR' in line or 'CRITICAL' in line:
                    print(f"\033[31m{line}\033[0m", end='')
                elif 'WARNING' in line:
                    print(f"\033[33m{line}\033[0m", end='')
                elif 'INFO' in line:
                    print(f"\033[32m{line}\033[0m", end='')
                elif 'DEBUG' in line:
                    print(f"\033[36m{line}\033[0m", end='')
                else:
                    print(line, end='')

            print(f"\n{'=' * 80}")
            print(f"显示了 {len(display_lines)} 行")
            if level:
                print(f"（过滤级别: {level_upper}，共 {len(filtered_lines)} 行）")
            print(f"{'=' * 80}\n")

    except KeyboardInterrupt:
        print("\n\n👋 已退出")
    except Exception as e:
        print(f"❌ 读取日志失败: {e}")


def list_log_files(log_dir: Path):
    """列出所有日志文件"""
    if not log_dir.exists():
        print(f"❌ 日志目录不存在: {log_dir}")
        return

    log_files = sorted(log_dir.glob('*.log'), key=lambda x: x.stat().st_mtime, reverse=True)

    if not log_files:
        print(f"❌ 目录中没有日志文件: {log_dir}")
        return

    print(f"\n{'=' * 80}")
    print(f"📁 日志目录: {log_dir}")
    print(f"{'=' * 80}\n")

    print(f"{'序号':<4} {'文件名':<40} {'大小':<10} {'修改时间':<20}")
    print("-" * 80)

    for idx, log_file in enumerate(log_files, 1):
        size_kb = log_file.stat().st_size / 1024
        mtime = datetime.fromtimestamp(log_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')

        # 高亮错误日志
        name = log_file.name
        if 'error' in name:
            name = f"\033[31m{name}\033[0m"

        print(f"{idx:<4} {name:<40} {size_kb:>8.2f}KB {mtime}")

    print(f"\n共 {len(log_files)} 个日志文件\n")


def search_logs(log_dir: Path, keyword: str, file_pattern: str = "*.log"):
    """搜索日志内容"""
    if not log_dir.exists():
        print(f"❌ 日志目录不存在: {log_dir}")
        return

    log_files = list(log_dir.glob(file_pattern))

    if not log_files:
        print(f"❌ 未找到匹配的日志文件: {file_pattern}")
        return

    print(f"\n{'=' * 80}")
    print(f"🔍 搜索关键词: {keyword}")
    print(f"📁 搜索目录: {log_dir}")
    print(f"{'=' * 80}\n")

    total_matches = 0

    for log_file in log_files:
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            matches = [(i + 1, line) for i, line in enumerate(lines) if keyword.lower() in line.lower()]

            if matches:
                print(f"\n📄 {log_file.name} ({len(matches)} 处匹配)")
                print("-" * 80)

                for line_num, line in matches[:10]:  # 最多显示10条
                    # 高亮关键词
                    highlighted = line.replace(
                        keyword,
                        f"\033[1;33m{keyword}\033[0m"
                    ).replace(
                        keyword.lower(),
                        f"\033[1;33m{keyword.lower()}\033[0m"
                    ).replace(
                        keyword.upper(),
                        f"\033[1;33m{keyword.upper()}\033[0m"
                    )
                    print(f"  {line_num:>5}: {highlighted}", end='')

                if len(matches) > 10:
                    print(f"\n  ... 还有 {len(matches) - 10} 处匹配")

                total_matches += len(matches)

        except Exception as e:
            print(f"❌ 读取 {log_file.name} 失败: {e}")

    print(f"\n{'=' * 80}")
    print(f"共找到 {total_matches} 处匹配")
    print(f"{'=' * 80}\n")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="日志查看工具")

    parser.add_argument(
        'action',
        nargs='?',
        default='list',
        choices=['list', 'view', 'search', 'tail'],
        help='操作: list(列出日志), view(查看日志), search(搜索), tail(实时跟踪)'
    )

    parser.add_argument(
        '-f', '--file',
        default='scraper.log',
        help='日志文件名（默认: scraper.log）'
    )

    parser.add_argument(
        '-n', '--lines',
        type=int,
        default=50,
        help='显示行数（默认: 50）'
    )

    parser.add_argument(
        '-l', '--level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='过滤日志级别'
    )

    parser.add_argument(
        '-k', '--keyword',
        help='搜索关键词'
    )

    parser.add_argument(
        '-d', '--dir',
        default='logs',
        help='日志目录（默认: logs）'
    )

    args = parser.parse_args()

    log_dir = Path(args.dir)

    if args.action == 'list':
        list_log_files(log_dir)

    elif args.action == 'view':
        log_file = log_dir / args.file
        view_log_file(log_file, args.lines, level=args.level)

    elif args.action == 'tail':
        log_file = log_dir / args.file
        view_log_file(log_file, follow=True)

    elif args.action == 'search':
        if not args.keyword:
            print("❌ 请使用 -k 指定搜索关键词")
            return
        search_logs(log_dir, args.keyword)


if __name__ == "__main__":
    main()
