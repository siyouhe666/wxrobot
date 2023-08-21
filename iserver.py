from flask import Flask
import xml.etree.ElementTree as ET
from flask import request
import json
from WXBizMsgCrypt3 import WXBizMsgCrypt,XMLParse
import sys
from urllib.parse import unquote
from flask import Response
from demo import *

app = Flask(__name__)
Token = "EapMIQgIFXjqJj3M2JM0lkhUkei6Ai"
EncodingAESKey = "5bu6D9F49TeAy6DJXe12FmJvBrfmDoYSCe7WWeOgUiI"
corpId = "wwcb064012f8a72f8d"

wxcpt = WXBizMsgCrypt(Token,EncodingAESKey,corpId)
xml_parse = XMLParse()


history = {}
def get_his(username,prompt,max_iter):
    if username in history:
        if len(history[username])>max_iter:
             history[username] =  history[username][-max_iter:]
        history[username].append(prompt)
    else:
        history[username] = [prompt]
    return history[username]


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
        xml = request.data
        wxcpt = WXBizMsgCrypt(Token,EncodingAESKey,corpId)
        ret,sMsg=wxcpt.DecryptMsg( xml, msg_signature, timestamp, nonce)
        #print("###")
        #print(sMsg)
        #print("###")
        xml_tree = ET.fromstring(sMsg)
        ToUserName = xml_tree.find("ToUserName").text
        CreateTime = xml_tree.find("CreateTime").text
        FromUserName = xml_tree.find("FromUserName").text
        MsgType = xml_tree.find("MsgType").text
        AgentID = xml_tree.find("AgentID").text
        Content = xml_tree.find("Content").text
        print(ToUserName)
        print(FromUserName)



        prompt1 = {"role":"user","content":Content}
        print("prompt1",prompt1)
        input_prompt = get_his(FromUserName,prompt1,3*2)
        print("input_prompt",input_prompt)
        reply = ai_response(input_prompt)
        prompt2 = {"role":"assistant","content":reply}
        output_prompt = get_his(FromUserName,prompt2,3*2)
        print("prompt2",prompt2)
        print("output_prompt",output_prompt)



        sRespData = "<xml><ToUserName>"+ToUserName+"</ToUserName><FromUserName>"+FromUserName+"</FromUserName><CreateTime>"+CreateTime+"</CreateTime><MsgType>text</MsgType><Content>"+reply+"</Content><AgentID>"+AgentID+"</AgentID></xml>"
        ret,sEncryptMsg=wxcpt.EncryptMsg(sRespData, nonce, timestamp)
        return sEncryptMsg


if __name__ == '__main__':
    app.run("0.0.0.0",port=5555)
