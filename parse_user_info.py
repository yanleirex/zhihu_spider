# coding=utf-8
# !/usr/bin/env python
import requests

from items import UserItem
from settings import headers_base
from utils import content_to_html


def parse_user(main_page_url, cookies=None, xsrf=None):
    """
    parse user information from main page
    :type main_page_url: str
    :param xsrf:
    :param cookies:
    :param main_page_url:
    :return:
    """
    if cookies is None or xsrf is None:
        return None
    else:
        headers_ = headers_base
        headers_['Referer'] = main_page_url + "/answers"
        item = UserItem()
        response = requests.get(main_page_url, headers=headers_, cookies=cookies)
        if response.status_code == 200:
            doc = content_to_html(response.content)
            _parse_profile(html_doc=doc, item=item)
            _parse_home(html_doc=doc, main_page_url=main_page_url, item=item)
            _parse_follow(html_doc=doc, item=item)
        return item


def _parse_profile(html_doc, item):
    """
    from html parse user profile
    :param html_doc:
    :return:
    """
    span_list = html_doc.xpath("//span[@class='info-wrap']/span/@class")
    for span_item in span_list:
        if span_item == 'location item':
            item['location'] = html_doc.xpath("//span[@class='location item']/@title")[0]
        if span_item == 'item gender':
            gender = html_doc.xpath("//span[@class='item gender']/i/@class")[0]
            if gender == 'icon icon-profile-male':
                item['gender'] = 'male'
            else:
                item['gender'] = 'female'
        if span_item == 'education item':
            item['education'] = html_doc.xpath("//span[@class='education item']/@title")[0]
        if span_item == 'business item':
            item['business'] = html_doc.xpath("//span[@class='business item']/@title")[0]
        if span_item == 'employment item':
            item['employment'] = html_doc.xpath("//span[@class='employment item']/@title")[0]
        if span_item == 'position item':
            item['position'] = html_doc.xpath("//span[@class='position item']/@title")[0]
        if span_item == 'education-extra item':
            item['education_extra'] = html_doc.xpath("//span[@class='education-extra item']/@title")[0]
    title_list = html_doc.xpath("//div[@class='title-section ellipsis']/span/@class")
    for title in title_list:
        if title == 'name':
            item['name'] = html_doc.xpath("//span[@class='name']/text()")[0]
        if title == 'bio':
            item['desc'] = html_doc.xpath("//span[@class='bio']/text()")[0]
    item['user_agree'] = html_doc.xpath("//span[@class='zm-profile-header-user-agree']/strong/text()")[0]
    item['user_thanks'] = html_doc.xpath("//span[@class='zm-profile-header-user-thanks']/strong/text()")[0]


def _parse_home(html_doc, main_page_url, item):
    """
    parse home information from html_doc
    :param html_doc:
    :param main_page_url:
    :return:
    """
    ask_xpath = "//a[@class='item ' and @href='%s']/span/text()" % (main_page_url[21:] + "/asks")
    answer_xpath = "//a[@class='item ' and @href='%s']/span/text()" % (main_page_url[21:] + "/answers")
    post_xpath = "//a[@class='item ' and @href='%s']/span/text()" % (main_page_url[21:] + "/posts")
    collection_xpath = "//a[@class='item ' and @href='%s']/span/text()" % (main_page_url[21:] + "/collections")
    log_xpath = "//a[@class='item ' and @href='%s']/span/text()" % (main_page_url[21:] + "/logs")
    ask_num = html_doc.xpath(ask_xpath)
    answer_num = html_doc.xpath(answer_xpath)
    post_num = html_doc.xpath(post_xpath)
    collection_num = html_doc.xpath(collection_xpath)
    log_num = html_doc.xpath(log_xpath)
    item['ask_num'] = ask_num[0]
    item['answer_num'] = answer_num[0]
    item['post_num'] = post_num[0]
    item['collection_num'] = collection_num[0]
    item['log_num'] = log_num[0]
    return item


def _parse_follow(html_doc, item):
    """
    parse follower and followee
    :param html_doc:
    :return:
    """
    followees = html_doc.xpath("//div[@class='zm-profile-side-following zg-clear']/a/strong/text()")[0]
    followers = html_doc.xpath("//div[@class='zm-profile-side-following zg-clear']/a/strong/text()")[1]
    item['followees_num'] = followees
    item['followers_num'] = followers
    return item


def _parse_skilled_topic(html_doc, item):
    """
    parse skilled topics
    :param html_doc:
    :param item:
    :return:
    """
    pass


def _parse_column_num(html_doc, item):
    """
    parse column nums
    :param html_doc:
    :param item:
    :return:
    """
    # item['column_num'] = html_doc.xpath("//a[@class='zg-link-litblue']/strong/text()")[0]
    return item


def _parse_topic_num(html_doc, item):
    """
    parse topic numbers
    :param html_doc:
    :param item:
    :return:
    """
    # item['topic_num'] = html_doc.xpath("//")
    return item
