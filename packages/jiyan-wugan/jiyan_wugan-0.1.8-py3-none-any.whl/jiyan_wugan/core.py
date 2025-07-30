import importlib.resources
import os
import execjs

JS_FILENAMES = {
    'jy': 'jy.js',
    'evn': 'evn.js',
    'sdk': 'sdk.js',
}

def get_js_content(js_name):
    filename = JS_FILENAMES[js_name]
    with importlib.resources.open_text('tools.jsapi.js', filename, encoding='utf-8') as f:
        js_code = f.read()
    # 兼容 execjs：只把需要的函数声明为全局变量
    js_code += """
if (typeof module !== 'undefined' && module.exports) {
    if (module.exports.get_lib) get_lib = module.exports.get_lib;
    if (module.exports.get_abo) get_abo = module.exports.get_abo;
    if (module.exports.sign) sign = module.exports.sign;
    if (module.exports.pos) pos = module.exports.pos;
}
"""
    return js_code

def get_lib():
    js_str = get_js_content('jy')
    content = execjs.compile(js_str)
    return content.call('get_lib')

def get_abo():
    js_str = get_js_content('jy')
    content = execjs.compile(js_str)
    return content.call('get_abo')

def get_sign(e, t):
    js_str = get_js_content('jy')
    content = execjs.compile(js_str)
    return content.call('sign', e, t)

def get_pos(t, n, i, r, _, a, s):
    js_str = get_js_content('jy')
    content = execjs.compile(js_str)
    return content.call('pos', t, n, i, r, _, a, s)

# source.js和static_path.txt的生成路径

def ensure_js_output_dir():
    js_dir = os.path.join(os.getcwd(), 'js')
    if not os.path.exists(js_dir):
        os.makedirs(js_dir)
    return js_dir

def get_source_js_path():
    return os.path.join(ensure_js_output_dir(), 'source.js')

def get_static_path_txt_path():
    return os.path.join(ensure_js_output_dir(), 'static_path.txt') 