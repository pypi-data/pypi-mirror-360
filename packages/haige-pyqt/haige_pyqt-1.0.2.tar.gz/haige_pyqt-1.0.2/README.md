# haige_pyqt

海哥的 pyqt 公共类库。

## 目录结构

## 依赖类库
``` text
PyQt5==5.15.9
astunparse~=1.6.3
pywin32~=310
astunparse~=1.6.3
```

## 快速上手


## 常用操作

### 1. qt .ui 文件生成 .py 代码

```shell
pyuic5.exe .\haige_pyqt\uis\about.ui -o .\haige_pyqt\uis\about.py
```

### 2. 预编译【关于作者图片】与【源表模板文件】资源


### 3. 编译成 wheel 包
```shell
python setup.py sdist bdist_wheel
```

### 4. 发布 packages
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