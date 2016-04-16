# coding=utf-8
# !/usr/bin/env python


import pymongo


class Pipeline(object):
    def __init__(self, host_url="localhost", host_port=27017):
        self.conn = pymongo.MongoClient(host=host_url, port=host_port)

    def process_data(self, data=None):
        pass
