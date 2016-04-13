# coding=utf-8
# !/usr/bin/env python

import requests
import lxml.html
import time
import json

headers_base = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
    'Connection': 'keep-alive',
    'Host': 'www.zhihu.com',
    'User-Agent': 'Mozilla/5.0 (Linux; U; Android 2.3.6; en-us; Nexus S Build/GRK39F) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
    'Referer': 'http://www.zhihu.com/',
}

zhihu_base_url = "https://www.zhihu.com"
login_url = "https://www.zhihu.com/login/email"
# main_page = "https://www.zhihu.com/people/yanleirex"
main_page = "https://www.zhihu.com/people/tian-yuan-dong"
activity_page = main_page + "/activities"


def get_xsrf(url):
    """
    get xsrf
    :param url:
    """
    r = requests.get(url=url)
    doc = lxml.html.fromstring(r.content)
    xsrf = doc.xpath('//input/@value')[0]
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
        _xsrf = get_xsrf(login_url)

        post_data = {
            "password": password,
            "remember_me": "true",
            "email": username,
            "_xsrf": _xsrf.encode('utf-8')
        }

        r = requests.post(url=login_url, headers=headers_base, data=post_data)
        # print r.status_code
        if r.status_code == 200:
            ret_code = json.loads(r.text).get("r")

            if ret_code is 0:
                print "login zhihu success..."
                print json.loads(r.text).get("msg")
                return r.cookies, _xsrf
            else:
                print "login zhihu failed..."
                return None
        else:
            print "login zhihu failed..."
            return None


def parse_main_page(cookies, xsrf, user_main_page):
    """
    parse user's main_page
    :param xsrf:
    :param cookies:
    :param user_main_page:
    :return:
    """
    # cook, xsrf = login(username=username, password=password)
    if cookies is not None:
        rr = requests.get(user_main_page, headers=headers_base, cookies=cookies)
        parse_follower(rr)
        # request more
        print "xsrf: " + xsrf
        parse_more_activity(xsrf=xsrf)


def parse_followees(cookies, xsrf, user_main_page):
    """
    parse user's followees
    :param xsrf:
    :param cookies:
    :param user_main_page:
    :return:
    """
    if cookies is not None:
        print "xsrf:" + xsrf
        rr = requests.get(user_main_page + '/followees', headers=headers_base, cookies=cookies)
        parse_follower(rr)
        if rr.content is not None and rr.content is not u'':
            html = lxml.html.fromstring(rr.content)
            followee_lists = html.xpath("//div[@class='zm-profile-card zm-profile-section-item zg-clear no-hovercard']/a[@class='zm-item-link-avatar']")
            for followee_list in followee_lists:
                followee_name = followee_list.xpath("@title")[0]
                followee_page = followee_list.xpath("@href")[0]
                print "You followed: " + followee_name + "(" + zhihu_base_url + followee_page + ")"


def parse_followers(cookies, xsrf, user_main_page):
    """
    parse user's followers
    :param cookies:
    :param xsrf:
    :param user_main_page:
    :return:
    """
    print "xsrf:" + xsrf
    rr = requests.get(user_main_page + '/followers', headers=headers_base, cookies=cookies)
    if rr.content is not None and rr.content is not u'':
        html = lxml.html.fromstring(rr.content)
        params = get_params(html)
        while True:
            r = load_more(xsrf, params)
        follower_lists = html.xpath("//div[@class='zm-profile-card zm-profile-section-item zg-clear no-hovercard']/a[@class='zm-item-link-avatar']")
        for follower_list in follower_lists:
            follower_name = follower_list.xpath("@title")[0]
            follower_page = follower_list.xpath("@href")[0]
            print follower_name + "(" + zhihu_base_url + follower_page + ")followed you"

        # print r.content


def get_params(html):
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


def parse_more_activity(xsrf):
    """
    parse user main page activity
    :param xsrf:
    :return:
    """
    start_time = str(time.time())[:10]
    while True:
        if start_time is None:
            break
        post_data = {
            "start": start_time,
            "_xsrf": xsrf.encode('utf-8')
        }
        rr = requests.post(activity_page, headers=headers_base, data=post_data)
        parse_activity(rr)
        msg = json.loads(rr.content)["msg"][1]
        start_time = get_timestamp(msg)


def get_timestamp(content):
    """
    get time
    :param content:
    :return:
    """
    if content is not u'':
        html = lxml.html.fromstring(content)
        time_lists = html.xpath("//div[@class='zm-profile-section-item zm-item clearfix']/@data-time")
        return time_lists[-1]


def parse_follower(rr):
    """
    parse how many followers and followees
    :param rr:
    :return:
    """
    html = lxml.html.fromstring(rr.content)
    followees = html.xpath("//div[@class='zm-profile-side-following zg-clear']/a/strong/text()")[0]
    followers = html.xpath("//div[@class='zm-profile-side-following zg-clear']/a/strong/text()")[1]
    print "You have followd %d zhihuers" % int(followees)
    print "You have %s followers" % int(followers)


def load_more(xsrf, params):
    """
    load more when dynamic load
    :param xsrf:
    :param params:
    :return: response.content
    """
    node_name = params['nodename']
    request_url = zhihu_base_url + "/node/" + node_name
    post_param = params['params']
    offset = post_param['offset'] + 20
    order_by = post_param['order_by']
    hash_id = post_param['hash_id']
    post_data = {
        "method": "next",
        "params": {
            "offset": offset,
            "order_by": order_by,
            "hash_id": hash_id
        },
        "_xsrf": xsrf
    }
    post_data = str(post_data)
    rr = requests.post(url=request_url, data=post_data, headers=headers_base)
    if rr.status_code == 200:
        return rr.content


def parse_activity(rr):
    # print rr.status_code
    if rr.status_code == 200:
        msg = json.loads(rr.content)["msg"][1]
        # print msg
        if msg is not u'':
            html = lxml.html.fromstring(msg)
            activity_lists = html.xpath("//div[@class='zm-profile-section-item zm-item clearfix']")

            for a_list in activity_lists:
                data_time = a_list.xpath("@data-time")[0]
                data_type_detail = a_list.xpath("@data-type-detail")[0]

                # check activity type
                # follow topic
                if data_type_detail == "member_follow_topic":
                    topic = a_list.xpath(
                        "div[@class='zm-profile-section-main zm-profile-section-activity-main zm-profile-activity-page-item-main']/a[@class='topic-link']/@title")[
                        0]
                    topic_url = a_list.xpath(
                        "div[@class='zm-profile-section-main zm-profile-section-activity-main zm-profile-activity-page-item-main']/a[@class='topic-link']/@href")[
                        0]
                    print time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(float(
                        data_time))) + " You follow the topic: " + topic + " Topic url: " + zhihu_base_url + topic_url
                # follow column
                elif data_type_detail == "member_follow_column":
                    column = a_list.xpath(
                        "div[@class='zm-profile-section-main zm-profile-section-activity-main zm-profile-activity-page-item-main']/a[@class='column_link']/text()")[
                        0]
                    column_url = a_list.xpath(
                        "div[@class='zm-profile-section-main zm-profile-section-activity-main zm-profile-activity-page-item-main']/a[@class='column_link']/@href")[
                        0]
                    print time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(
                        float(data_time))) + " You follow the column: " + column + " Column url: " + column_url
                # follow question
                elif data_type_detail == "member_follow_question":
                    question = a_list.xpath(
                        "div[@class='zm-profile-section-main zm-profile-section-activity-main zm-profile-activity-page-item-main']/a[@class='question_link']/text()")[
                        0]
                    question_link = a_list.xpath(
                        "div[@class='zm-profile-section-main zm-profile-section-activity-main zm-profile-activity-page-item-main']/a[@class='question_link']/@href")[
                        0]
                    print time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(float(
                        data_time))) + " You follow the question: " + question + " Question link: " + zhihu_base_url + question_link
                # vote column article
                elif data_type_detail == "member_voteup_article":
                    column = a_list.xpath("div[@class='zm-profile-section-main zm-profile-section-activity-main zm-profile-activity-page-item-main']/a[@class='column_link']/text()")[0]
                    column_link = a_list.xpath("div[@class='zm-profile-section-main zm-profile-section-activity-main zm-profile-activity-page-item-main']/a[@class='column_link']/@href")[0]
                    post_link = a_list.xpath("div[@class='zm-profile-section-main zm-profile-section-activity-main zm-profile-activity-page-item-main']/a[@class='post-link']/@href")[0]
                    post_name = a_list.xpath("div[@class='zm-profile-section-main zm-profile-section-activity-main zm-profile-activity-page-item-main']/a[@class='post-link']/text()")[0]
                    print time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(float(
                        data_time))) + " You vote the article: " + post_name + " article link: " + post_link + " of column " + column + ", column link: " + column_link
                # follow collection
                elif data_type_detail == "member_follow_favlist":
                    collection_name = a_list.xpath("div[@class='zm-profile-section-main zm-profile-section-activity-main zm-profile-activity-page-item-main']/a/text()")[0]
                    collection_url = a_list.xpath("div[@class='zm-profile-section-main zm-profile-section-activity-main zm-profile-activity-page-item-main']/a/@href")[0]
                    print time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(float(
                        data_time))) + " You follow the collection: " + collection_name + " collection link: " + collection_url
                # vote the answer
                elif data_type_detail == "member_voteup_answer":
                    question = a_list.xpath("div[@class='zm-profile-section-main zm-profile-section-activity-main zm-profile-activity-page-item-main']/a[@class='question_link']/text()")[0]
                    question_link = a_list.xpath("div[@class='zm-profile-section-main zm-profile-section-activity-main zm-profile-activity-page-item-main']/a[@class='question_link']/@href")[0]
                    author_link = a_list.xpath("div[@class='zm-item-answer ']//a[@class='zg-link']/@href")[0]
                    author = a_list.xpath("div[@class='zm-item-answer ']//a[@class='zg-link']/text()")[0]
                    answer_url = a_list.xpath("div[@class='zm-item-answer ']/div[@class='zm-item-rich-text js-collapse-body']/@data-entry-url")[0]
                    print time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(float(
                        data_time))) + " You vote the question: " + question + "(question link: " + zhihu_base_url + question_link + ")of " + author + "'s(" + author_link + ") answer,answer link: " + zhihu_base_url + answer_url
                # create article
                elif data_type_detail == "member_create_article":
                    column = a_list.xpath("div[@class='zm-profile-section-main zm-profile-section-activity-main zm-profile-activity-page-item-main']/a[@class='column_link']/text()")[0]
                    column_link = a_list.xpath("div[@class='zm-profile-section-main zm-profile-section-activity-main zm-profile-activity-page-item-main']/a[@class='column_link']/@href")[0]
                    post_title = a_list.xpath("div[@class='zm-profile-section-main zm-profile-section-activity-main zm-profile-activity-page-item-main']/a[@class='post-link']/text()")[0]
                    post_link = a_list.xpath("div[@class='zm-profile-section-main zm-profile-section-activity-main zm-profile-activity-page-item-main']/a[@class='post-link']/@href")[0]
                    print time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(float(
                        data_time))) + " You at the column: " + column + "(" + column_link + ")create an article: " + post_title + "(" + post_link + ")"
                # answer question
                elif data_type_detail == "member_answer_question":
                    question = a_list.xpath("div[@class='zm-profile-section-main zm-profile-section-activity-main zm-profile-activity-page-item-main']/a[@class='question_link']/text()")[0]
                    question_link = a_list.xpath("div[@class='zm-profile-section-main zm-profile-section-activity-main zm-profile-activity-page-item-main']/a[@class='question_link']/@href")[0]
                    print time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(float(
                        data_time))) + " You answer the question: " + question + "(" + question_link + ")"
                else:
                    print "Sorry,I don't know what you did..."


if __name__ == "__main__":
    user = ""
    psd = ""
    cook1, xsrf1 = login(username=user, password=psd)
    # parse_main_page(cook1, xsrf1, main_page)
    # parse_followees(cook1, xsrf1, main_page)
    parse_followers(cook1, xsrf1, main_page)
