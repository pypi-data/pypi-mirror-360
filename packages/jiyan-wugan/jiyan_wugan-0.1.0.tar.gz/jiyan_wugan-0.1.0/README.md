# jsapi

标准化 jsapi Python 包，封装 JS 接口调用与业务流程。

## 安装

```bash
pip install .
```

## 依赖
- PyExecJS
- requests

## 主要接口

```python
from tools.jsapi import get_lib, get_abo, get_sign, get_pos, process_and_build_dict, generate_hex, jy_main, load, get_w
```

## 目录结构
- core.py: JS接口相关
- util.py: 工具函数
- sp.py: 业务流程
- js/: 所需 JS 文件

## 示例

```python
from tools.jsapi import jy_main
result = jy_main('your_captcha_id')
``` 