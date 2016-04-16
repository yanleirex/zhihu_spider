# coding=utf-8
# !/usr/bin/env python
from login_zhihu import login
from parse_user_info import parse_user
from parse_zhihu import parse_main_page
from parse_follow import parse_followees

def test_login():
    user = ""
    psd = ""
    return login(username=user, password=psd)


def test_parse_activity():
    main_page = "https://www.zhihu.com/people/gui-mu-zhi"
    cook, xsrf = test_login()
    parse_main_page(cookies=cook, xsrf=xsrf, user_main_page=main_page)


def test_qr():
    from queue_redis import Queue
    bqueue = Queue('Beatles')
    bqueue.push('Pete')
    bqueue.push('John')
    print bqueue.pop()


def test_parse_user():
    main_page = "https://www.zhihu.com/people/kao-la-kao-la"
    cook, xsrf = test_login()
    parse_user(cookies=cook, xsrf=xsrf, main_page_url=main_page)

def test_parse_followees():
    main_page = "https://www.zhihu.com/people/kao-la-kao-la"
    cook, xsrf = test_login()
    parse_followees(main_page, cookies=cook, xsrf=xsrf)

if __name__ == "__main__":
    # test_login()
    # test_parse_activity()
    # test_qr()
    # test_parse_user()
    test_parse_followees()
