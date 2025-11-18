#!/usr/bin/env python3
"""
网络连接测试脚本
用于检查服务器的网络连接情况
"""

import subprocess
import sys


def test_network():
    """测试网络连接"""
    print("=" * 60)
    print("网络连接测试")
    print("=" * 60)

    tests = [
        ("DNS 解析 - Google", "nslookup google.com"),
        ("DNS 解析 - 目标站点", "nslookup www.hollandandbarrett.com"),
        ("Ping - Google", "ping -c 3 8.8.8.8"),
        ("HTTP 连接 - Google", "curl -I --connect-timeout 5 https://www.google.com"),
        ("HTTP 连接 - 目标站点", "curl -I --connect-timeout 5 https://www.hollandandbarrett.com"),
    ]

    passed = 0
    failed = 0

    for test_name, command in tests:
        print(f"\n[测试] {test_name}")
        print(f"命令: {command}")
        print("-" * 60)

        try:
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                print(f"✓ 成功")
                if result.stdout.strip():
                    # 只显示前5行
                    lines = result.stdout.strip().split('\n')[:5]
                    print('\n'.join(lines))
                passed += 1
            else:
                print(f"✗ 失败 (退出码: {result.returncode})")
                if result.stderr.strip():
                    print(f"错误: {result.stderr.strip()[:200]}")
                failed += 1

        except subprocess.TimeoutExpired:
            print(f"✗ 超时（10秒）")
            failed += 1
        except Exception as e:
            print(f"✗ 异常: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"通过: {passed}/{len(tests)}")
    print(f"失败: {failed}/{len(tests)}")

    if failed > 0:
        print("\n⚠️  检测到网络连接问题")
        print("\n可能的原因:")
        print("  1. 服务器无法访问外网")
        print("  2. 防火墙阻止了出站连接")
        print("  3. DNS 解析失败")
        print("  4. 需要配置代理")

        print("\n建议:")
        print("  1. 检查服务器网络配置:")
        print("     curl https://www.google.com")
        print("  2. 如果需要代理，设置环境变量:")
        print("     export HTTP_PROXY='http://proxy:port'")
        print("     export HTTPS_PROXY='http://proxy:port'")
        print("  3. 检查防火墙规则:")
        print("     sudo ufw status")
        print("     sudo iptables -L")
    else:
        print("\n✓ 网络连接正常")

    return failed == 0


if __name__ == "__main__":
    success = test_network()
    sys.exit(0 if success else 1)
