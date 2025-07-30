# PyPI发布指南

本指南详细说明如何将AIOEway库发布到PyPI。

## 准备工作

### 1. 安装必要工具

```bash
# 安装构建和发布工具
pip install --upgrade pip setuptools wheel
pip install --upgrade build twine
```

### 2. 注册PyPI账户

- **正式PyPI**: https://pypi.org/account/register/
- **测试PyPI**: https://test.pypi.org/account/register/

### 3. 配置API Token（推荐）

1. 登录PyPI，进入Account Settings
2. 创建API Token
3. 配置到本地：

```bash
# 创建配置文件
mkdir -p ~/.pypirc
cat > ~/.pypirc << EOF
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token-here
EOF

# 设置权限
chmod 600 ~/.pypirc
```

## 发布流程

### 方法一：使用发布脚本（推荐）

```bash
# 发布到测试PyPI
python publish.py --test

# 发布到正式PyPI
python publish.py
```

### 方法二：手动发布

#### 1. 清理旧文件

```bash
rm -rf build/ dist/ *.egg-info/
```

#### 2. 构建包

```bash
# 使用build工具（推荐）
python -m build

# 或使用setup.py
python setup.py sdist bdist_wheel
```

#### 3. 检查包

```bash
# 检查包的完整性
twine check dist/*

# 查看包内容
tar -tzf dist/aioeway-1.0.0.tar.gz
```

#### 4. 测试发布

```bash
# 上传到测试PyPI
twine upload --repository testpypi dist/*

# 测试安装
pip install --index-url https://test.pypi.org/simple/ aioeway
```

#### 5. 正式发布

```bash
# 上传到正式PyPI
twine upload dist/*

# 验证安装
pip install aioeway
```

## 版本管理

### 更新版本号

需要同时更新以下文件中的版本号：

1. `setup.py`
2. `pyproject.toml`
3. `device_mqtt_client.py`（如果有__version__变量）

### 语义化版本

- **主版本号**：不兼容的API修改
- **次版本号**：向下兼容的功能新增
- **修订号**：向下兼容的问题修正

## 发布检查清单

### 发布前检查

- [ ] 代码测试通过
- [ ] 文档更新完整
- [ ] 版本号已更新
- [ ] CHANGELOG.md已更新
- [ ] README.md准确无误
- [ ] 依赖项版本正确
- [ ] 许可证文件存在

### 包内容检查

- [ ] 所有必要文件已包含
- [ ] 敏感信息已排除
- [ ] 包大小合理
- [ ] 元数据正确

### 发布后验证

- [ ] PyPI页面显示正常
- [ ] 安装测试成功
- [ ] 文档链接有效
- [ ] 依赖项解析正确

## 常见问题

### 1. 包名冲突

如果包名已存在，需要：
- 选择新的包名
- 更新所有配置文件
- 重新构建和上传

### 2. 版本冲突

如果版本号已存在，需要：
- 增加版本号
- 重新构建和上传
- 不能覆盖已发布的版本

### 3. 上传失败

常见原因：
- 网络连接问题
- 认证信息错误
- 包格式问题
- 文件大小限制

### 4. 依赖项问题

确保：
- 依赖项版本兼容
- 依赖项在PyPI上可用
- 版本约束合理

## 最佳实践

### 1. 测试优先

始终先发布到测试PyPI，验证无误后再发布到正式PyPI。

### 2. 自动化

使用CI/CD工具自动化发布流程：

```yaml
# GitHub Actions示例
name: Publish to PyPI
on:
  release:
    types: [published]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}
```

### 3. 文档维护

- 保持README.md更新
- 维护详细的CHANGELOG
- 提供使用示例
- 及时回应用户反馈

### 4. 安全考虑

- 使用API Token而非密码
- 定期轮换Token
- 不在代码中硬编码敏感信息
- 使用.gitignore排除敏感文件

## 相关链接

- [PyPI官方文档](https://packaging.python.org/)
- [Twine文档](https://twine.readthedocs.io/)
- [setuptools文档](https://setuptools.pypa.io/)
- [PEP 517/518](https://peps.python.org/pep-0517/)
- [语义化版本](https://semver.org/lang/zh-CN/)