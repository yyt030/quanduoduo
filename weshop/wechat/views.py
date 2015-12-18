# encoding: utf8
import time
from django.shortcuts import HttpResponse, render_to_response, redirect
from lxml import etree
from shop.models import Order
from core.models import CompanyInfo
import handler as HD
import string
from backends.dj import Helper, wechat_login
from .lib import WeixinHelper, WxPayConf_pub, catch
from .pay import JsApi_pub, UnifiedOrder_pub, Notify_pub
from utils import render_json
from utils import add_wechat_user_to_db
from django.views.decorators.csrf import csrf_exempt
from shopextend.models import MyOrder
from django.http import HttpResponse, HttpResponseRedirect
from utils import generate_nonce_str, generate_trade_time


@csrf_exempt
def we_chat_interface(request):
    """公众平台对接"""
    signature = request.REQUEST.get("signature", "")
    timestamp = request.REQUEST.get("timestamp", "")
    nonce = request.REQUEST.get("nonce", "")
    print request.REQUEST
    if not any([signature, timestamp, nonce]) or not WeixinHelper.checkSignature(signature, timestamp, nonce):
        return HttpResponse("check failed")
    if request.method == "GET":
        return HttpResponse(request.GET.get("echostr"))
    elif request.method == "POST":
        try:
            # print request.raw_post_data
            str_xml = request.body
            xml = etree.fromstring(str_xml)
            msg_type = xml.find('MsgType').text
            from_user = xml.find('FromUserName').text
            add_wechat_user_to_db(request, from_user)
            request.session['openid'] = from_user
            print msg_type
        except Exception, e:
            print e
        else:
            # if msg_type == 'event':
            # event_name = xml.find('Event')
            #     event_key = xml.find('EventKey')
            #     print event_key.text
            #     # return reverse('register')
            #     if event_key.text == 'my_profile':
            #
            #         #return HttpResponseRedirect(event_key.text)
            # 消息处理器
            handler = HD.MessageHandle(request.body)
            response = handler.start()
            return HttpResponse(response)

    else:
        return HttpResponse("")


@HD.subscribe
def subscribe(xml):
    company_info_query = CompanyInfo.objects.all()
    if company_info_query:
        companyInfo = company_info_query[0]
        return str(companyInfo.welcome)
    else:
        return "欢迎加入缤芬兰！您已链接全球最洁净食品来源地---芬兰"


@HD.unsubscribe
def subscribe(xml):
    print "leave"
    return "leave  brain"


@HD.text
def text(xml):
    content = xml.Content
    if content == "111":
        return {"Title": "美女", "Description": "比基尼美女",
                "PicUrl": "http://9smv.com/static/mm/uploads/150411/2-150411115450247.jpg",
                "Url": "http://9smv.com/beauty/list?category=5"}
    elif content == "222":
        return [
            ["比基尼美女", "比基尼美女", "http://9smv.com/static/mm/uploads/150411/2-150411115450247.jpg",
             "http://9smv.com/beauty/list?category=5"],
            ["长腿美女", "长腿美女", "http://9smv.com/static/mm/uploads/150506/2-150506111A9648.jpg",
             "http://9smv.com/beauty/list?category=8"]
        ]
    elif content == "push":
        Helper.send_text_message(xml.FromUserName, "推送消息测试")
        return "push ok"
    company_info_query = CompanyInfo.objects.all()
    if company_info_query:
        companyInfo = company_info_query[0]
        return str(companyInfo.welcome)
    else:
        return "欢迎加入"


@wechat_login
def oauth(request):
    """网页授权获取用户信息"""
    resp = HttpResponse(request.openid)
    resp.set_cookie("openid", Helper.sign_cookie(request.openid))
    return resp


def share(request):
    """jssdk 分享"""
    url = "http://" + request.get_host() + request.path
    sign = Helper.jsapi_sign(url)
    sign["appId"] = WxPayConf_pub.APPID
    return render_to_response("share.html", {"jsapi": sign})


@wechat_login
def pay(request):
    response = render_to_response("pay.html")
    response.set_cookie("openid", Helper.sign_cookie(request.openid))
    return response


@csrf_exempt
@wechat_login
@catch
def paydetail(request):
    """获取支付信息"""
    if 'openid' in request.session:
        openid = request.session['openid']
        print "openid " + str(openid)
        # money = request.POST.get("money") or "0.01"
        # money = int(float(money) * 100)
        jsApi = JsApi_pub()
        unifiedOrder = UnifiedOrder_pub()
        unifiedOrder.setParameter("openid", openid)  # openid
        unifiedOrder.setParameter("body", "商品购买")  # 商品描述
        order_id = request.REQUEST.get("order_id", "")
        order = MyOrder.objects.get(pk=order_id)
        # timeStamp = time.time()
        # out_trade_no = "{0}{1}".format(WxPayConf_pub.APPID, int(timeStamp * 100))
        out_trade_no = order.out_trade_no
        if out_trade_no == '':
            # 订单编号 32 位，由14位长度 time_str + 18位长度的随机数字
            time_str = generate_trade_time()
            nonce_str = generate_nonce_str(size=18, chars=string.digits)
            out_trade_no = time_str + nonce_str
            order.out_trade_no = out_trade_no
            order.save()
        # 总金额：商品金额+运费
        payment_amount = order.order_subtotal
        payment_amount = int(float(payment_amount) * 100)
        unifiedOrder.setParameter("out_trade_no", str(out_trade_no))  # 商户订单号
        unifiedOrder.setParameter("total_fee", str(payment_amount))  # 总金额
        unifiedOrder.setParameter("notify_url", WxPayConf_pub.NOTIFY_URL)  # 通知地址
        unifiedOrder.setParameter("trade_type", "JSAPI")  # 交易类型
        # unifiedOrder.setParameter("attach", "6666") #附件数据，可分辨不同商家(string(127))
        try:
            prepay_id = unifiedOrder.getPrepayId()
            jsApi.setPrepayId(prepay_id)
            jsApiParameters = jsApi.getParameters()
        except Exception as e:
            print(e)
        else:
            print jsApiParameters
            return HttpResponse(jsApiParameters)
    else:
        return render_json({'error': "no openid found"})


FAIL, SUCCESS = "FAIL", "SUCCESS"


@csrf_exempt
@catch
def wechat_pay_notify(request):
    """支付回调"""
    xml = request.raw_post_data
    # 使用通用通知接口
    notify = Notify_pub()
    notify.saveData(xml)
    print xml
    # 验证签名，并回应微信。
    # 对后台通知交互时，如果微信收到商户的应答不是成功或超时，微信认为通知失败，
    # 微信会通过一定的策略（如30分钟共8次）定期重新发起通知，
    # 尽可能提高通知的成功率，但微信不保证通知最终能成功
    if not notify.checkSign():
        notify.setReturnParameter("return_code", FAIL)  # 返回状态码
        notify.setReturnParameter("return_msg", "签名失败")  # 返回信息
    else:
        result = notify.getData()

        if result["return_code"] == FAIL:
            notify.setReturnParameter("return_code", FAIL)
            notify.setReturnParameter("return_msg", "通信错误")
        elif result["result_code"] == FAIL:
            notify.setReturnParameter("return_code", FAIL)
            notify.setReturnParameter("return_msg", result["err_code_des"])
        else:
            notify.setReturnParameter("return_code", SUCCESS)
            out_trade_no = result["out_trade_no"]  # 商户系统的订单号，与请求一致。
            ###检查订单号是否已存在,以及业务代码(业务代码注意重入问题)

    return HttpResponse(notify.returnXml())


def test(request):
    json_data = {}

    return render_json(json_data)
