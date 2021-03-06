#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# buzz2weibo
# Copyright 2011 Sun Zhigang
# See LICENSE for details.

from weibopy.auth import OAuthHandler
from weibopy.api import API
from urllib2 import urlopen, URLError, HTTPError
from json import load
import sys, os
import codecs

WEIBO_APP_KEY = '3127127763'
WEIBO_APP_SECRET = '21cc35f55fc8fe73b73162964c0bb415'

print '''欢迎使用buzz2weibo配置向导！
===========================
本向导会使用您输入的数据，在当前目录创建config.py文件。 '''

print '''
---------------------------
Google+的API单个KEY每日只能请求1000次。所以您必须申请一个自己的Google API Key
请访问 https://code.google.com/apis/console/ ，
然后Create Project，Enable Google+ API，再转到API Access页面，
Simple API Access中的API key就是你要得到的。拷贝粘贴到下面。
'''

google_api_key = raw_input('请输入Google API key：').strip()

print '''
---------------------------
为了获得您的Google用户ID，请访问 https://plus.google.com/me
登录后，地址栏会变成类似这样：
https://plus.google.com/106019261651260565998/posts
其中最长的那串纯数字，就是您的Google用户ID
'''
buzz_userid = raw_input('请输入Google用户ID：').strip()

print '''
---------------------------
开始验证Google API key和用户ID'''
people_url = 'https://www.googleapis.com/plus/v1/people/' + buzz_userid + '?key=' + google_api_key
fp = urlopen(people_url)
people = load(fp)
fp.close()
yn = raw_input('您在Google+的名字是“%s”吗？(Y/N)：' % people['displayName'].encode('utf-8')).strip()

if yn[0].lower() != 'y':
    print '''请重新运行本向导，输入正确的BuzzID。'''
    sys.exit(1)

# OAuth begins

auth = OAuthHandler(WEIBO_APP_KEY, WEIBO_APP_SECRET)
auth_url = auth.get_authorization_url()
print ''
print '请在浏览器中访问下面链接，授权给buzz2weibo后，会获得一个授权码。'
print ''
print auth_url
print ''

while True:
    verifier = raw_input('请输入授权码：').strip()
    try:
        token = auth.get_access_token(verifier)
    except HTTPError:
        print '授权码不正确或者过期，请重新运行本向导'
        sys.exit(1)
    else:
        break

weibo_token_key = token.key
weibo_token_secret = token.secret

# Generate config.py
config = u'''# vim: set fileencoding=utf-8 :

# Google API key
GOOGLE_API_KEY = '%s'

# 用户参数
BUZZ_USERID = '%s'
WEIBO_TOKEN_KEY = '%s'
WEIBO_TOKEN_SECRET = '%s'

# 是否使用https连接google
USE_HTTPS = True  # Google+ API只支持https

# 保存同步历史的文件路径
HISTORY_FILE = '%s.buzz2weibo_history'

# 下载然后传到微博的图片临时存放目录
IMAGES_PATH = '/tmp/buzz2weibo'

# 调试模式下，不会真的发微博，只打印状态
DEBUG = False

# 是否附带buzz链接
APPEND_SHARE_FROM_BUZZ_LINK = True
''' % (google_api_key, buzz_userid, weibo_token_key, weibo_token_secret, sys.path[0] + os.sep)

fp = codecs.open('config.py', 'w', 'utf-8')
fp.write(config)
fp.close()

print ''
print 'config.py生成完毕，运行buzz2weibo.py开始同步。编辑config.py可以做更多个性化设置'
