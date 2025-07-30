// jsapi-test/jsapi/js/jy.js

// 业务数据
const _lib = { "86JE": "38wv" };
const _abo = { "n[22:23]+n[25:26]": "n[20:27]" };

// 业务算法（请根据实际业务替换下面的实现）
function feiyue(c, t) {
    // TODO: 替换为真实签名算法
    return c + ':' + t;
}

function pos(t, n, i, r, _, a, s) {
    // TODO: 替换为真实算法
    return {
        pow_msg: t + n + i + r + _ + a + s,
        pow_sign: t + n
    };
}

// 导出接口
function get_lib() { return _lib; }
function get_abo() { return _abo; }
function sign(c, t) { return feiyue(c, t); }

module.exports = { get_lib, get_abo, sign, pos };