# -*- coding: utf-8 -*-
import os
from kombu import Exchange, Queue
from celery.schedules import crontab
from .http_config import API_HOST

env = os.environ
BASEDIR = os.path.abspath(os.path.join(__file__, '../../../'))

# db
database = "qixing"
host = "119.3.47.90"
# host = "127.0.0.1"
port = "3306"
username = 'root'
password = 'LaI#UvabRIOMyTx5'
charset = "utf8mb4"
sqlenginename = 'mysql+pymysql'
DB_PARAMS = "{0}://{1}:{2}@{3}/{4}?charset={5}".format(
    sqlenginename,
    username,
    password,
    host,
    database,
    charset)

# 微信商户
mch_id = "1598811931"
mch_key = "7JCztbDHCsNjH6aq2ycD4J9up56FirEd"
apiclient_cert = os.path.join(BASEDIR, 'pem', 'apiclient_cert.pem')
apiclient_key = os.path.join(BASEDIR, 'pem', 'apiclient_key.pem')
apiclient_public = os.path.join(BASEDIR, 'pem', 'apiclient_public.pem')

# 小程序
MiniProgramAppId = "wxcd2d900e92d2e383"
MiniProgramAppSecret = "d42ced6c3aaee35b5ba24f050708e1d4"
MiniProgramWxpay_notify_url = API_HOST + '/api/order/wechat_notify'

# 身份实名认证
ID_CHECK_APPCODE = env.get("ID_CHECK_APPCODE", '4909312d8a334c86b392048bdcc14cc4')

#  腾讯地图
TencentMapSK = 'WkeMamiWgVwi8jpliEE0EmiDfdSEaWab'
TencentMapKey = 'KZKBZ-M7XLX-RF34D-TNQIM-JS6RQ-A2BKH'

miniprogram_dir = os.path.join(BASEDIR, 'wxminiprogram')

if not os.path.isdir(miniprogram_dir):
    os.makedirs(miniprogram_dir)

# 七牛云OSS
QINIU_ACCESS_KEY = 'X8Ra-aIOadk0NZS9GRBnAW-Xs1cxx1H3ci9jd5AS'
QINIU_SECRET_KEY = '7xW7HQjB8oJ2XcTh6AQUt_1Qgz9bh5-w5oYLOEMu'
QINIU_BUCKET_NAME = 'media_bigxingxing'
QINIU_BUCKET_DOMAIN = 'img.planet.sanbinit.cn'


class DefaltSettig(object):
    SECRET_KEY = env.get('SECRET', 'guess')
    TOKEN_EXPIRATION = 3600 * 7 * 24  # token过期时间(秒)
    IMG_TO_OSS = True
    DEBUG = True
    BASEDIR = BASEDIR
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    # celery doc: http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html
    CELERY_BROKER_URL = 'redis://localhost:6379/1',
    CELERY_RESULT_BACKEND = 'redis://localhost:6379'
    CACHE_REDIS_URL = 'redis://localhost:6379/1'
    CELERY_TIMEZONE = 'Asia/Shanghai'
    CELERY_ENABLE_UTC = True

    # 配置低优先级和高优先级队列
    CELERY_QUEUES = (
        Queue(name='celery'),  # 为celery的默认队列，如果项目中不使用，可以不启用
        Queue(name='low_priority', exchange=Exchange('low_priority', type='direct'), routing_key='low_priority'),
        Queue(name='high_priority', exchange=Exchange('high_priority', type='direct'), routing_key='high_priority')
    )

    CELERYBEAT_SCHEDULE = {

    }


class TestSetting(object):
    pass
