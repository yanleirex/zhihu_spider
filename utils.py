# coding=utf-8
# !/usr/bin/env python
import lxml


def content_to_html(content):
    """
    convert requests response to html
    :param content:
    :return:
    """
    return lxml.html.fromstring(content)
