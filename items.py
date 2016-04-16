# coding=utf-8
# !/usr/bin/env python

from scrapy.item import Item, Field


class UserItem(Item):
    name = Field()
    main_page_url = Field()
    desc = Field()
    location = Field()
    business = Field()
    gender = Field()
    employment = Field()
    position = Field()
    education = Field()
    education_extra = Field()
    user_agree = Field()
    user_thanks = Field()
    ask_num = Field()
    answer_num = Field()
    post_num = Field()
    collection_num = Field()
    log_num = Field()
    followees_num = Field()
    followers_num = Field()
    column_num = Field()
    topic_num = Field()
    skilled_at_topic = Field()


class FollowItem(Item):
    user_name = Field()
    user_follower = Field()
    user_followee = Field()

