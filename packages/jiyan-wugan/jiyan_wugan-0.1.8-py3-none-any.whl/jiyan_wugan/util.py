import json
import re
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

import execjs
import subprocess
from functools import partial
import sys

subprocess.Popen = partial(subprocess.Popen, encoding="utf-8", errors="ignore")

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

JS_PATH = os.path.join(os.path.dirname(__file__), "js/jy.js")

def get_lib():
    with open(JS_PATH, encoding='utf-8') as f:
        js_str = f.read()
    content = execjs.compile(js_str)
    xs = content.call('get_lib')
    return xs

def get_abo():
    with open(JS_PATH, encoding='utf-8') as f:
        js_str = f.read()
    content = execjs.compile(js_str)
    xs = content.call('get_abo')
    return xs

def get_sign(e, t):
    with open(JS_PATH, encoding='utf-8') as f:
        js_str = f.read()
    content = execjs.compile(js_str)
    xs = content.call('sign', e, t)
    return xs

def get_pos(t, n, i, r, _, a, s):
    with open(JS_PATH, encoding='utf-8') as f:
        js_str = f.read()
    content = execjs.compile(js_str)
    xs = content.call('pos', t, n, i, r, _, a, s)
    return xs

def process_and_build_dict(expression_dict, n):
    def process_slice(slice_expression):
        slice_expression = re.sub(r':(\d+)', lambda m: f":{int(m.group(1)) + 1}", slice_expression)
        match = re.match(r'n\[(\d+)(?::(\d+))?\]', slice_expression)
        if not match:
            return ''
        start = int(match.group(1))
        end = int(match.group(2)) if match.group(2) else start + 1
        return n[start:end]
    def evaluate_expression(expression):
        parts = re.findall(r'n\[[^\]]+\]', expression)
        results = [process_slice(part) for part in parts]
        return ''.join(results)
    def build_nested_dict(keys, value):
        if len(keys) == 1:
            return evaluate_expression(keys[0])
        return {evaluate_expression(keys[0]): build_nested_dict(keys[1:], value)}
    result_dict = {}
    for key, value in expression_dict.items():
        key_parts = key.split('.')
        nested_key = build_nested_dict(key_parts, value)
        processed_value = evaluate_expression(value)
        current_level = result_dict
        for part in key_parts[:-1]:
            part_key = evaluate_expression(part)
            if part_key not in current_level:
                current_level[part_key] = {}
            current_level = current_level[part_key]
        current_level[evaluate_expression(key_parts[-1])] = processed_value
    return result_dict

import random

def generate_hex():
    num = int(65536 * (1 + random.random()))
    hex_str = hex(num)[2:]
    return hex_str[1:] 
