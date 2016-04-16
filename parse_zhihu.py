# coding=utf-8
# !/usr/bin/env python
import json
import requests

import lxml

import time
from urllib import urlencode

from settings import headers_base
from settings import zhihu_base_url


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
        parse_more_activity(xsrf=xsrf, main_page=user_main_page)


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
    request_url = user_main_page + '/followers'
    rr = requests.get(request_url, headers=headers_base, cookies=cookies)
    if rr.content is not None and rr.content is not u'':
        html = lxml.html.fromstring(rr.content)
        params = get_params(html)
        while True:
            r = load_more(xsrf, params, request_url)
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


def parse_more_activity(xsrf, main_page):
    """
    parse user main page activity
    :param xsrf:
    :param main_page
    :return:
    """
    activity_page = main_page + "/activities"
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
    print "You have followd %d followees" % int(followees)
    print "You have %s followers" % int(followers)


def load_more(xsrf, params, referer_url):
    """
    load more when dynamic load
    :param xsrf:
    :param params:
    :param referer_url
    :return: response.content
    """
    node_name = params['nodename']
    request_url = zhihu_base_url + "/node/" + node_name
    post_param = params['params']
    offset = post_param['offset'] + 20
    order_by = post_param['order_by']
    hash_id = post_param['hash_id']
    post_data = {
        "_xsrf": xsrf,
        "params": '{"offset":%d,"order_by":"%s","hash_id":"%s"}' % (offset, order_by, hash_id),
        "method": "next"
    }
    post_data = urlencode(post_data)
    headers_ = headers_base
    headers_['X-Requested-With'] = "XMLHttpRequest"
    headers_['Accept'] = "*/*"
    headers_['Referer'] = referer_url
    headers_['Accept-Language'] = "en-US,en;q=0.5"
    headers_['Accept-Encoding'] = "gzip, deflate, br"
    headers_['Content-Type'] = "application/x-www-form-urlencoded; charset=UTF-8"
    headers_['Content-Length'] = "171"
    # h = {"Host": "www.zhihu.com",
    #         "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0",
    #         "Accept": "*/*",
    #         "Accept-Language": "en-US,en;q=0.5",
    #         "Accept-Encoding": "gzip, deflate, br",
    #         "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    #         "X-Requested-With": "XMLHttpRequest",
    #         "Referer": "https://www.zhihu.com/people/tian-yuan-dong",
    #         "Content-Length": "55",
    #         "Connection": "keep-alive"
    # }
    rr = requests.post(url=request_url, data=post_data, headers=headers_, cookies=cook1)
    if rr.status_code == 200:
        return rr.content


def parse_activity(rr):
    # print rr.status_code
    if rr.status_code == 200 and rr.ok is True:
        msg = json.loads(rr.content)["msg"][1]
        # print msg
        # TODO:check msg
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
                        data_time))) + " You follow the topic: " + topic + "(" + zhihu_base_url + topic_url + ")"
                # follow column
                elif data_type_detail == "member_follow_column":
                    column = a_list.xpath(
                        "div[@class='zm-profile-section-main zm-profile-section-activity-main zm-profile-activity-page-item-main']/a[@class='column_link']/text()")[
                        0]
                    column_url = a_list.xpath(
                        "div[@class='zm-profile-section-main zm-profile-section-activity-main zm-profile-activity-page-item-main']/a[@class='column_link']/@href")[
                        0]
                    print time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(
                        float(data_time))) + " You follow the column: " + column + "(" + column_url + ")"
                # follow question
                elif data_type_detail == "member_follow_question":
                    question = a_list.xpath(
                        "div[@class='zm-profile-section-main zm-profile-section-activity-main zm-profile-activity-page-item-main']/a[@class='question_link']/text()")[
                        0]
                    question_link = a_list.xpath(
                        "div[@class='zm-profile-section-main zm-profile-section-activity-main zm-profile-activity-page-item-main']/a[@class='question_link']/@href")[
                        0]
                    print time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(float(
                        data_time))) + " You follow the question: " + question + "(" + zhihu_base_url + question_link + ")"
                # vote column article
                elif data_type_detail == "member_voteup_article":
                    column = a_list.xpath("div[@class='zm-profile-section-main zm-profile-section-activity-main zm-profile-activity-page-item-main']/a[@class='column_link']/text()")[0]
                    column_link = a_list.xpath("div[@class='zm-profile-section-main zm-profile-section-activity-main zm-profile-activity-page-item-main']/a[@class='column_link']/@href")[0]
                    post_link = a_list.xpath("div[@class='zm-profile-section-main zm-profile-section-activity-main zm-profile-activity-page-item-main']/a[@class='post-link']/@href")[0]
                    post_name = a_list.xpath("div[@class='zm-profile-section-main zm-profile-section-activity-main zm-profile-activity-page-item-main']/a[@class='post-link']/text()")[0]
                    print time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(float(
                        data_time))) + " You vote the article: " + post_name + "(" + post_link + ")of column " + column + "(" + column_link + ")"
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
                    author_link_ = a_list.xpath("div[@class='zm-item-answer ']//a[@class='zg-link']/@href")
                    if author_link_ is not None:
                        author_link = author_link_[0]
                    else:
                        author_link = ""
                    author_ = a_list.xpath("div[@class='zm-item-answer ']//a[@class='zg-link']/text()")
                    if author_ is not None:
                        author = author_[0]
                    else:
                        author = ""
                    # author = a_list.xpath("a[@class='zg-link']/text()")[0]
                    answer_url = a_list.xpath("div[@class='zm-item-answer ']/div[@class='zm-item-rich-text js-collapse-body']/@data-entry-url")[0]
                    # answer_url = a_list.xpath("div[@class='zm-item-rich-text js-collapse-body']/@data-entry-url")[0]
                    print time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(float(
                        data_time))) + " You vote the question: " + question + "(" + zhihu_base_url + question_link + ")of " + author + "'s(" + author_link + ") answer,answer link: " + zhihu_base_url + answer_url
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
                        data_time))) + " You answer the question: " + question + "(" + zhihu_base_url + question_link + ")"
                # ask question
                elif data_type_detail == "member_ask_question":
                    question_link = a_list.xpath("div[@class='zm-profile-section-main zm-profile-section-activity-main zm-profile-activity-page-item-main']/a[@class='question_link']/@href")[0]
                    question = a_list.xpath("div[@class='zm-profile-section-main zm-profile-section-activity-main zm-profile-activity-page-item-main']/a[@class='question_link']/text()")[0]
                    print time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(float(
                        data_time))) + " You asked the question: " + question + "(" + zhihu_base_url + question_link + ")"
                else:
                    print "Sorry,I don't know what you did..."
