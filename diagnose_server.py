#!/usr/bin/env python3
"""
服务器环境诊断脚本
用于排查 ChromeDriver 初始化问题
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """运行命令并返回结果"""
    print(f"\n{'='*60}")
    print(f"检查: {description}")
    print(f"命令: {cmd}")
    print('-' * 60)
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(f"✓ 成功")
            if result.stdout.strip():
                print(f"输出: {result.stdout.strip()}")
            return True, result.stdout.strip()
        else:
            print(f"✗ 失败 (退出码: {result.returncode})")
            if result.stderr.strip():
                print(f"错误: {result.stderr.strip()}")
            return False, result.stderr.strip()
    except subprocess.TimeoutExpired:
        print(f"✗ 超时 (10秒)")
        return False, "timeout"
    except Exception as e:
        print(f"✗ 异常: {e}")
        return False, str(e)


def main():
    print("=" * 60)
    print("服务器环境诊断")
    print("=" * 60)

    issues = []

    # 1. 检查操作系统
    success, output = run_command("uname -a", "操作系统信息")

    # 2. 检查 Chrome/Chromium 安装
    chrome_found = False
    for chrome_cmd in ["google-chrome --version", "chromium-browser --version", "chromium --version"]:
        success, output = run_command(chrome_cmd, "Chrome/Chromium 版本")
        if success:
            chrome_found = True
            break

    if not chrome_found:
        issues.append("❌ Chrome/Chromium 未安装")

    # 3. 检查 Chrome 可执行文件位置
    for path in ["/usr/bin/google-chrome", "/usr/bin/chromium-browser", "/usr/bin/chromium"]:
        if os.path.exists(path):
            print(f"\n✓ 找到 Chrome: {path}")
            run_command(f"ls -lh {path}", "文件权限")
            break

    # 4. 检查必要的系统库
    print(f"\n{'='*60}")
    print("检查: 系统依赖库")
    print('-' * 60)
    required_libs = [
        "libnss3",
        "libgconf-2-4",
        "libfontconfig1",
        "libxss1",
        "libappindicator3-1",
        "libasound2"
    ]

    for lib in required_libs:
        success, output = run_command(f"dpkg -l | grep {lib}", f"  {lib}")
        if not success or not output:
            issues.append(f"❌ 缺少依赖库: {lib}")

    # 5. 检查网络连接
    print(f"\n{'='*60}")
    print("检查: 网络连接")
    print('-' * 60)
    success, _ = run_command("curl -I https://chromedriver.storage.googleapis.com/ --connect-timeout 5",
                            "ChromeDriver 下载站点")
    if not success:
        issues.append("⚠️  无法连接到 ChromeDriver 下载站点")

    success, _ = run_command("curl -I https://www.google.com --connect-timeout 5",
                            "Google 连接测试")

    # 6. 检查 Python 环境
    print(f"\n{'='*60}")
    print("检查: Python 环境")
    print('-' * 60)
    run_command("python --version", "Python 版本")
    run_command("which python", "Python 路径")

    # 7. 检查 selenium 和 webdriver-manager
    print(f"\n{'='*60}")
    print("检查: Python 包")
    print('-' * 60)
    try:
        import selenium
        print(f"✓ selenium 版本: {selenium.__version__}")
    except ImportError:
        issues.append("❌ selenium 未安装")
        print("✗ selenium 未安装")

    try:
        import webdriver_manager
        print(f"✓ webdriver-manager 已安装")
    except ImportError:
        issues.append("❌ webdriver-manager 未安装")
        print("✗ webdriver-manager 未安装")

    # 8. 检查 ChromeDriver 缓存
    wdm_cache = Path.home() / ".wdm"
    print(f"\n{'='*60}")
    print(f"检查: ChromeDriver 缓存目录")
    print(f"路径: {wdm_cache}")
    print('-' * 60)
    if wdm_cache.exists():
        run_command(f"ls -lhR {wdm_cache}", "缓存内容")
    else:
        print("✗ 缓存目录不存在（首次运行正常）")

    # 9. 检查磁盘空间
    run_command("df -h", "磁盘空间")

    # 10. 检查内存
    run_command("free -h", "内存状态")

    # 总结
    print(f"\n{'='*60}")
    print("诊断总结")
    print('=' * 60)

    if issues:
        print(f"\n发现 {len(issues)} 个问题:\n")
        for issue in issues:
            print(f"  {issue}")

        print("\n" + "="*60)
        print("建议的解决方案:")
        print("="*60)

        if any("Chrome" in issue for issue in issues):
            print("\n1. 安装 Chrome:")
            print("   wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb")
            print("   sudo apt install -y ./google-chrome-stable_current_amd64.deb")

        if any("依赖库" in issue for issue in issues):
            print("\n2. 安装依赖库:")
            print("   sudo apt update")
            print("   sudo apt install -y libnss3 libgconf-2-4 libfontconfig1 libxss1 libappindicator3-1 libasound2")

        if any("无法连接" in issue for issue in issues):
            print("\n3. 网络连接问题:")
            print("   尝试手动下载 ChromeDriver 或配置代理")
            print("   参考下面的手动安装方法")

        if any("selenium" in issue or "webdriver" in issue for issue in issues):
            print("\n4. 安装 Python 依赖:")
            print("   uv sync")
    else:
        print("\n✓ 未发现明显问题")
        print("\n可能的原因:")
        print("  1. ChromeDriver 下载速度慢（网络问题）")
        print("  2. 首次运行需要下载 ChromeDriver（需要等待）")
        print("\n建议:")
        print("  - 尝试手动安装 ChromeDriver（见下方）")
        print("  - 增加超时时间")
        print("  - 检查防火墙设置")

    # 手动安装 ChromeDriver 的方法
    print(f"\n{'='*60}")
    print("手动安装 ChromeDriver 的方法")
    print('=' * 60)
    print("""
如果自动下载失败，可以手动安装:

1. 查看 Chrome 版本:
   google-chrome --version

2. 下载对应版本的 ChromeDriver:
   # 例如 Chrome 120，则下载 ChromeDriver 120
   CHROME_VERSION=$(google-chrome --version | grep -oP '\\d+\\.\\d+\\.\\d+')
   DRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION%%.*}")
   wget "https://chromedriver.storage.googleapis.com/${DRIVER_VERSION}/chromedriver_linux64.zip"

3. 解压并安装:
   unzip chromedriver_linux64.zip
   sudo mv chromedriver /usr/local/bin/
   sudo chmod +x /usr/local/bin/chromedriver

4. 验证安装:
   chromedriver --version

5. 修改代码使用本地 ChromeDriver (不使用 webdriver-manager)
""")

    print(f"\n{'='*60}")
    print("完成诊断")
    print('=' * 60)


if __name__ == "__main__":
    main()
