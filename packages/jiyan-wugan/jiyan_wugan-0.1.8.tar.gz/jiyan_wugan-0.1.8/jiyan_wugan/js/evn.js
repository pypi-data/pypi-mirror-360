window = global
delete global
delete buffer

var canvas = {
    toDataURL: function toDataURL(){},
    getContext: function getContext(x){
        return {}
    }
}
document = {
    'body':'<body></body>',
    'head':'<head></head>',
    'documentElement': '<html></html>',
    createEvent: function createEvent() {

    },
    createElement: function createElement(x){
        debugger
        console.log(x)
        // return canvas
    },
    getElementsByTagName: function (key) {
        console.log(key)
        if(key==='body'){
            return 'body'
        }
        if(key==='head'){
            return 'head'
        }
    }
}

HTMLCollection = ['body']

window.location={
    "ancestorOrigins": {},
    "href": "https://iam.pt.ouchn.cn/am/UI/Login?realm=%2F&service=initService&goto=https%3A%2F%2Fiam.pt.ouchn.cn%2Fam%2Foauth2%2Fauthorize%3Fservice%3DinitService%26response_type%3Dcode%26client_id%3D345fcbaf076a4f8a%26scope%3Dall%26redirect_uri%3Dhttps%253A%252F%252Fmenhu.pt.ouchn.cn%252Fouchnapp%252Fwap%252Flogin%252Findex%26decision%3DAllow",
    "origin": "https://iam.pt.ouchn.cn",
    "protocol": "https:",
    "host": "iam.pt.ouchn.cn",
    "hostname": "iam.pt.ouchn.cn",
    "port": "",
    "pathname": "/am/UI/Login",
    "search": "?realm=%2F&service=initService&goto=https%3A%2F%2Fiam.pt.ouchn.cn%2Fam%2Foauth2%2Fauthorize%3Fservice%3DinitService%26response_type%3Dcode%26client_id%3D345fcbaf076a4f8a%26scope%3Dall%26redirect_uri%3Dhttps%253A%252F%252Fmenhu.pt.ouchn.cn%252Fouchnapp%252Fwap%252Flogin%252Findex%26decision%3DAllow",
    "hash": ""
}
navigator = {
    "appCodeName": "Mozilla",
    'appName': "Netscape",
    "appVersion": "5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
}
// window.crypto = {}
// window = {
//     addEventListener: function addEventListener(x){
//         return function mousemove(){
//
//         }
//     },
//     attachEvent: function attachEvent(x){
//         console.log(x)
//     },
//     document:document,
//     location: location,
//     navigator:navigator
// }
function setProxy(proxyObjs) {
    for (let i = 0; i < proxyObjs.length; i++) {
        const handler = `{
          get: function(target, property, receiver) {
          if (property!="Math" && property!="isNaN"){
             if (target[property] && typeof target[property] !="string" &&  Object.keys(target[property]).length>3){
              }else{
            console.log("方法:", "get  ", "对象:", "${proxyObjs[i]}", "  属性:", property, "  属性类型：", typeof property, ", 属性值：", target[property]);}}
            return target[property];
          },
          set: function(target, property, value, receiver) {
            console.log("方法:", "set  ", "对象:", "${proxyObjs[i]}", "  属性:", property, "  属性类型：", typeof property, ", 属性值：", value, ", 属性值类型：", typeof target[property]);
            return Reflect.set(...arguments);
          }
        }`;
        eval(`try {
            ${proxyObjs[i]};
            ${proxyObjs[i]} = new Proxy(${proxyObjs[i]}, ${handler});
        } catch (e) {
            ${proxyObjs[i]} = {};
            ${proxyObjs[i]} = new Proxy(${proxyObjs[i]}, ${handler});
        }`);
    }
}

setProxy(['window', 'document', ' navigator', 'screen', 'localStorage', 'location','HTMLCollection','config'])