import datetime #模块
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
import time
#全自动化Python代码操作
from selenium import webdriver
import win32com.client
speaker = win32com.client.Dispatch("SAPI.SpVoice")

ashduadiwdndia = "2022-02-12 17:47:00.00000000"
zhangsan = webdriver.Chrome()
zhangsan.get("https://www.taobao.com")
time.sleep(3)  #查找  网络元素 来自 链接 文本(亲,请登录)    #点击
zhangsan.find_element_by_link_text("亲，请登录").click()
print(f"请尽快扫码登录")
time.sleep(10)
zhangsan.get("https://cart.taobao.com/cart.htm")
time.sleep(3)
# 是否全选购物车
while True:
    try:            #查找 元素 来自  ID
        if zhangsan.find_element_by_id("J_SelectAll1"):
            zhangsan.find_element_by_id("J_SelectAll1").click()
            break
    except:
        print(f"找不到购买按钮")
while True:
    #获取电脑现在的时间,                      year month day
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    # 对比时间，时间到的话就点击结算
    print(now)
    if now > ashduadiwdndia:
        # 点击结算按钮
        while True:
            try:
                if zhangsan.find_element_by_link_text("结 算"):
                    print("here")
                    zhangsan.find_element_by_link_text("结 算").click()
                    print(f"主人,程序锁定商品,结算成功")
                    break
            except:
                pass
        while True:
            try:
                if zhangsan.find_element_by_link_text('提交订单'):
                    zhangsan.find_element_by_link_text('提交订单').click()
                    print(f"抢购成功，请尽快付款")
            except:
                print(f"主人,结算提交成功,我已帮你抢到商品啦,请及时支付订单")
                speaker.Speak(f"主人,结算提交成功,我已帮你抢到商品啦,请及时支付订单")
                break
        time.sleep(0.01)