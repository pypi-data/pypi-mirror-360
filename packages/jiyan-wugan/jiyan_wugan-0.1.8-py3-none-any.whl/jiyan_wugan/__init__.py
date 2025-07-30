# jsapi: 可复用的JS接口Python包

import os
from .core import get_lib, get_abo, get_sign, get_pos
from .util import process_and_build_dict, generate_hex
from .sp import jy_main, load, get_w 
from app.utils.proxy import get_quality_proxy

# 获取 js 目录的绝对路径，供 core/util 等模块引用
JSAPI_JS_PATH = os.path.join(os.path.dirname(__file__), 'js')

__all__ = [
    'get_lib', 'get_abo', 'get_sign', 'get_pos',
    'process_and_build_dict', 'generate_hex',
    'jy_main', 'load', 'get_w',
    'get_quality_proxy',
    'JSAPI_JS_PATH',
] 