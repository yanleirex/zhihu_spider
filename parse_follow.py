# coding=utf-8
# !/usr/bin/env python
import json
import requests

import lxml

from settings import headers_base, zhihu_base_url


def parse_followees(user_main_page, cookies=None, xsrf=None):
    """
    parse user's followees
    :param xsrf:
    :param cookies:
    :param user_main_page:
    :return:
    """
    if cookies is not None and xsrf is not None:
        print "xsrf:" + xsrf
        rr = requests.get(user_main_page + '/followees', headers=headers_base, cookies=cookies)
        if rr.content is not None and rr.content is not u'':
            html = lxml.html.fromstring(rr.content)
            followee_lists = html.xpath("//div[@class='zm-profile-card zm-profile-section-item zg-clear no-hovercard']/a[@class='zm-item-link-avatar']")
            followee_list = list()
            for followee_list in followee_lists:
                followee_dict = dict()
                followee_name = followee_list.xpath("@title")[0]
                followee_page = followee_list.xpath("@href")[0]
                followee_dict['followee_name'] = followee_name
                followee_dict['followee_page'] = followee_page
                followee_list.append(followee_dict)
                print "You followed: " + followee_name + "(" + zhihu_base_url + followee_page + ")"
            return followee_list
    else:
        return None


def parse_followers(user_main_page, cookies=None, xsrf=None):
    """
    parse user's followers
    :param cookies:
    :param xsrf:
    :param user_main_page:
    :return:
    """
    if cookies is not None and xsrf is not None:
        print "xsrf:" + xsrf
        rr = requests.get(user_main_page + '/followers', headers=headers_base, cookies=cookies)
        if rr.content is not None and rr.content is not u'':
            html = lxml.html.fromstring(rr.content)
            params = _get_params(html)
            while True:
                #r = load_more(xsrf, params, request_url)
                _load_more(xsrf, params, )
            follower_lists = html.xpath("//div[@class='zm-profile-card zm-profile-section-item zg-clear no-hovercard']/a[@class='zm-item-link-avatar']")
            for follower_list in follower_lists:
                follower_name = follower_list.xpath("@title")[0]
                follower_page = follower_list.xpath("@href")[0]
                print follower_name + "(" + zhihu_base_url + follower_page + ")followed you"


def _get_params(html):
    """
    get params from html
    :param html:
    :return:
    """
    data_init = json.loads(html.xpath("//div[@class='zh-general-list clearfix']/@data-init")[0])
    params = data_init['params']
    order_by = params['order_by']
    hash_id = params['hash_id']
    node_name = data_init['nodename']
    ret_params = {
        "params": {
            "offset": 0,
            "order_by": order_by,
            "hash_id": hash_id
        },
        "nodename": node_name
    }
    return ret_params


def _load_more(xsrf, params, referer_url):
    """
    process dynamic load
    :param xsrf:
    :param params:
    :param referer_url:
    :return:
    """
    req_url = 'https://www.zhihu.com/node/ProfileFollowersListV2'
    post_data = {
        "method":"next",
        "params":"{'offset':"
    }
    pass
