from flask import Flask
from flask import request
import json
from WXBizMsgCrypt3 import WXBizMsgCrypt,XMLParse
import sys
from urllib.parse import unquote
from flask import Response

app = Flask(__name__)
Token = "你的TOKEN"
EncodingAESKey = "你的key"
corpId = "你的ID"

wxcpt = WXBizMsgCrypt(Token,EncodingAESKey,corpId)
xml_parse = XMLParse()
print("--init--")

@app.route('/')
def hello():
    return 'Hello, GLM'

@app.route("/aaa",methods=['GET','POST'])
def method1():
    method = request.method
    args= request.args
    msg_signature = unquote(args.get('msg_signature'))
    timestamp = unquote(args.get('timestamp'))
    nonce = unquote(args.get('nonce'))
    if method == "GET":
        echostr = unquote(args.get('echostr'))
        #print(request.data)
        wxcpt=WXBizMsgCrypt(Token,EncodingAESKey,corpId)
        ret = wxcpt.VerifyURL(msg_signature, timestamp,nonce,echostr)
        if(ret[0]!=0):
            print("ERR: VerifyURL ret: " + str(ret))
            return "error"
        print(ret[1])
        return ret[1]
    else:
        wxcpt = WXBizMsgCrypt(Token,EncodingAESKey,corpId)
        xml = request.data
        msg = unquote(xml_parse.extract(xml)[1])
        ret, sReplyEchoStr = wxcpt.VerifyURL(msg_signature,timestamp,nonce,msg)
        sReplyEchoStr_decode = sReplyEchoStr.decode("utf-8")
        if ret!=0:
            print("ERR: VerifyURL ret: " + str(ret))
        else:
            print("验证成功")
        ret,xml_info = wxcpt.EncryptMsg("12345678910",nonce,None)
        print("***")
        print("加密结果：",ret)
        print(xml_info)
        return xml_info

if __name__ == '__main__':
    app.run("0.0.0.0",port=5555)
