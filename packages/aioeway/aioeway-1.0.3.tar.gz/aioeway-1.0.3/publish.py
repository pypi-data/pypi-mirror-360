#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyPI发布脚本

使用方法:
    python publish.py --test    # 发布到测试PyPI
    python publish.py          # 发布到正式PyPI
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, check=True):
    """运行命令并打印输出"""
    print(f"执行命令: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    if check and result.returncode != 0:
        print(f"命令执行失败，退出码: {result.returncode}")
        sys.exit(1)
    
    return result


def clean_build():
    """清理构建文件"""
    print("清理构建文件...")
    dirs_to_clean = ['build', 'dist', '*.egg-info']
    for pattern in dirs_to_clean:
        run_command(f"rm -rf {pattern}", check=False)


def check_requirements():
    """检查必要的工具是否安装"""
    print("检查必要工具...")
    required_tools = ['twine', 'build']
    
    for tool in required_tools:
        result = run_command(f"python -m {tool} --version", check=False)
        if result.returncode != 0:
            print(f"错误: {tool} 未安装")
            print(f"请运行: pip install {tool}")
            sys.exit(1)


def build_package():
    """构建包"""
    print("构建包...")
    run_command("python -m build")


def check_package():
    """检查包的完整性"""
    print("检查包完整性...")
    run_command("python -m twine check dist/*")


def upload_package(test=False):
    """上传包到PyPI"""
    if test:
        print("上传到测试PyPI...")
        repository = "--repository testpypi"
        print("\n测试PyPI地址: https://test.pypi.org/project/aioeway/")
    else:
        print("上传到正式PyPI...")
        repository = ""
        print("\n正式PyPI地址: https://pypi.org/project/aioeway/")
    
    run_command(f"python -m twine upload {repository} dist/*")


def verify_version():
    """验证版本信息"""
    print("验证版本信息...")
    
    # 检查setup.py中的版本
    try:
        with open('setup.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'version="1.0.3"' in content:
                print("✓ setup.py版本: 1.0.3")
            else:
                print("⚠ 请检查setup.py中的版本号")
    except FileNotFoundError:
        print("⚠ setup.py文件不存在")
    
    # 检查pyproject.toml中的版本
    try:
        with open('pyproject.toml', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'version = "1.0.2"' in content:
                print("✓ pyproject.toml版本: 1.0.2")
            else:
                print("⚠ 请检查pyproject.toml中的版本号")
    except FileNotFoundError:
        print("⚠ pyproject.toml文件不存在")


def main():
    parser = argparse.ArgumentParser(description='发布包到PyPI')
    parser.add_argument('--test', action='store_true', help='发布到测试PyPI')
    parser.add_argument('--skip-build', action='store_true', help='跳过构建步骤')
    parser.add_argument('--skip-check', action='store_true', help='跳过检查步骤')
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("AIOEway PyPI发布脚本")
    print("=" * 50)
    
    # 验证版本
    verify_version()
    
    # 检查必要工具
    if not args.skip_check:
        check_requirements()
    
    # 清理构建文件
    clean_build()
    
    # 构建包
    if not args.skip_build:
        build_package()
    
    # 检查包
    if not args.skip_check:
        check_package()
    
    # 确认上传
    target = "测试PyPI" if args.test else "正式PyPI"
    confirm = input(f"\n确认上传到{target}? (y/N): ")
    
    if confirm.lower() in ['y', 'yes']:
        upload_package(test=args.test)
        print("\n✓ 发布完成!")
        
        if args.test:
            print("\n测试安装命令:")
            print("pip install --index-url https://test.pypi.org/simple/ aioeway")
        else:
            print("\n安装命令:")
            print("pip install aioeway")
    else:
        print("取消发布")


if __name__ == "__main__":
    main()