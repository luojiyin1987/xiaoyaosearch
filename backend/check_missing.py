#!/usr/bin/env python
"""
快速检查 PyInstaller 可能缺失的依赖
用于在打包前验证环境是否完整
"""
import sys

print("=" * 60)
print("  依赖检查工具")
print("=" * 60)
print()

# 检查是否安装
packages = [
    'jaraco',
    'jaraco.text',
    'importlib_metadata',
    'pkg_resources',
    'setuptools',
]

missing = []
present = []

print("检查常见依赖包:")
print()

for pkg in packages:
    try:
        __import__(pkg)
        present.append(pkg)
        print(f"  ✓ {pkg}")
    except ImportError:
        print(f"  ✗ {pkg} (缺失)")
        missing.append(pkg)

print()
print("=" * 60)

if missing:
    print(f"⚠️  发现 {len(missing)} 个缺失的包")
    print()
    print("安装命令:")
    print(f"  pip install {' '.join(missing)}")
    print()
    print("或者使用国内镜像:")
    print(f"  pip install -i https://pypi.tuna.tsinghua.edu.cn/simple {' '.join(missing)}")
else:
    print("✓ 所有依赖都已安装")
    print()
    print("可以开始打包了!")

print()
print("=" * 60)