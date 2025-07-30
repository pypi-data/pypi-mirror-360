# jsapi

可复用的JS接口Python包，集成验证码、签名、代理等功能。

## 安装

在项目根目录下执行：

```bash
pip install .
```

或打包上传到 PyPI 后：

```bash
pip install jsapi
```

## 依赖
- PyExecJS
- requests

## 导入与使用

```python
import jsapi

# 获取验证码签名等
lib = jsapi.get_lib()
abo = jsapi.get_abo()
sign = jsapi.get_sign('param1', 'param2')
pos = jsapi.get_pos('a','b','c','d','e','f','g')

# 业务流程
result = jsapi.jy_main('1461c6af6d31942bae54833e928fb5db')

# 获取优质代理
proxy = jsapi.get_quality_proxy()
```

## 目录结构
- jsapi/ 主要包代码
- jsapi/js/ 相关 JS 文件
- setup.py 打包脚本

## 贡献
欢迎 issue 和 PR！ 