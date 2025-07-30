"""
# File       : config.py
# Time       ：2024/8/20 下午5:25
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
import os
from pathlib import Path



if Path("configs/config_payments.py").exists():
    from configs.config_payments import *
else:
    # 如果配置文件不存在，则使用环境变量

    # 开发模式控制变量
    DEV_MODE = True


    # postgresql数据库
    DATABASE_URL = os.environ.get('PAYMENT_DATABASE_URL')  # 读取docker配置的环境变量
    if not DATABASE_URL:
        DATABASE_URL = "sqlite+aiosqlite:///./test_database.db"
        os.environ['PAYMENT_DATABASE_URL'] = DATABASE_URL  # 设置环境变量, 以便在docker、alembic中读取


    # 微信公众号
    class WeChatPub:
        app_id = "..."
        app_secret = "..."
        scope = "snsapi_login"
        scope_qrcode_login = "snsapi_login"  # 二维码登录必须用snsapi_login
        state = "your_custom_state"  # 用于防止CSRF
        接口配置信息_Token = "..."  # 自己去微信公众号设置


    # 微信小程序
    class WeChatMini:
        # 正式
        app_id = "..."
        app_secret = "..."


    # 阿里云
    class Aliyun:
        ali_access_key_id = "..."
        ali_access_key_secret = "..."
        ali_secretNo_pool_key = "..."


    # 微信支付专用
    class WeChatPay:
        APP_ID = "..."
        MCH_ID = '...'
        SECRET = '...'
        NONCE_STR = '...'
        KEY = '...'
        PAYMENT_NOTIFY_URL_小程序 = 'http://0.0.0.0:8000/msvc_order'  # 小程序支付成功后的回调地址
        REFUND_NOTIFY_URL_小程序 = 'http://0.0.0.0:8000/wxpay_recall'  # 小程序退款成功后的回调地址
        PAYMENT_NOTIFY_URL_二维码 = 'http://localhost:8000/wechat/pay_h5/payment_callback'  # 二维码支付成功后的回调地址
        REFUND_NOTIFY_URL_二维码 = 'http://localhost:8000/wechat/pay_h5/refund_callback'  # 二维码退款成功后的回调地址
        # 微信退款需要用到的商户证书，没有配置的话请求退款会出错
        # 详情见：https://pay.weixin.qq.com/wiki/doc/api/wxa/wxa_api.php?chapter=4_3
        CERT = '.../apiclient_cert.pem'
        CERT_KEY = '.../apiclient_key.pem'


    # 支付宝专用
    class AliPayConfig:
        appid = "..."
        key应用私钥 = Path("pems/应用私钥2048.txt")
        # key应用公钥 = Path(".../应用公钥2048.txt")
        key支付宝公钥 = Path("pems/支付宝公钥.pem")
        # 支付宝支付成功后的回调地址
        回调路径_root = "http://localhost:8000"
        回调路径_prefix = "/alipay/pay_qr"


    # 发送邮件
    class Email:
        sender = '...@163.com'  # 发件人
        server = 'smtp.163.com'  # 所使用的用来发送邮件的SMTP服务器
        username = '...@163.com'  # 发送邮箱的用户名和授权码（不是登录邮箱的密码）
        password = '...'  # 服务器: MVQDSPUQATBDOIFU / 自用电脑: FFHBMPJSXXFEEZIK


    # AES密码密匙
    class AESKey:
        key_web = "..."
        key_local = "..."
