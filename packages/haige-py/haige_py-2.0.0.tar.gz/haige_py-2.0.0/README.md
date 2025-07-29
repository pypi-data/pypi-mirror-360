# haige_pyqt

江湖海哥的 python 通用包类库。

## 目录结构

``` text
haige_py: 主目录
haige_py/Lib：常用类库封装
haige_py/cmdFactory.py：命令模式实现，提供 Command 和 CommandMager，可直接用于需要命令模式的场景。
```

## 依赖类库

``` text
astunparse~=1.6.3
```

## 快速上手


## 常用操作

### 1. 编译成 wheel
```shell
python setup.py sdist bdist_wheel
```

### 2. 发布 packages
```shell
pip install --upgrade twine
# a. 配置 ~/.pypirc 文件（Windows 为 %USERPROFILE%\.pypirc）
[distutils]
index-servers =
    pypi
[pypi]
username = __token__
password = pypi-你的API令牌  # 从PyPI账户获取

# b.发布
twine upload dist/*
```
