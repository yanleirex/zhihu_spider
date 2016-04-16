# coding=utf-8
# !/usr/bin/env python

import requests
import lxml.html
import json

from settings import login_url, headers_base


def _get_xsrf(url):
    """
    get xsrf
    :param url:
    """
    r = requests.get(url=url)
    doc = lxml.html.fromstring(r.content)
    try:
        xsrf = doc.xpath('//input/@value')[0]
    except Exception, e:
        print Exception, ":", e
    xsrf = str(xsrf)
    if xsrf is None:
        return ''
    else:
        print "xsrf: %s" % xsrf
        return xsrf


def login(username=None, password=None):
    """
    login zhihu
    return:cookies
    :param username:
    :param password:
    :returns: cookie xsrf
    """
    if username is None:
        print "Input your username..."
    elif password is None:
        print "Input your password..."
    else:
        # get xsrf
        _xsrf = _get_xsrf(login_url)

        post_data = {
            "password": password,
            "remember_me": "true",
            "email": username,
            "_xsrf": _xsrf.encode('utf-8')
        }
        try:
            r = requests.post(url=login_url, headers=headers_base, data=post_data)
        except Exception, e:
            print "Connection error: " + e
            print "Login field"
            return None
        # print r.status_code
        if r.status_code == 200:
            ret_code = json.loads(r.text).get("r")

            if ret_code is 0:
                print "login zhihu success..."
                print json.loads(r.text).get("msg")
                return r.cookies, _xsrf
            else:
                print "login zhihu failed..."
                return r.cookies, _xsrf
        else:
            print "login zhihu failed..."
            return None






