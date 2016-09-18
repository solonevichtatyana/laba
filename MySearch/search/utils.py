#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib import urlopen, quote
import re


class WikiChecker(object):
    def __init__(self, query):
        self.query = query
        self.url_result = None

        self.check(self.query)

    def check(self, query):
        wiki_lst = [
            "https://en.wikipedia.org/wiki/",
            "https://ru.wikipedia.org/wiki/"
        ]

        query_url_path = query.replace(" ", "_")

        for wiki in wiki_lst:
            wiki_url = wiki + query_url_path
            wiki_url_encoded = quote(wiki_url.encode('utf8'), ':/')

            try:
                if urlopen(wiki_url_encoded).getcode() != 404:
                    self.url_result = wiki_url
            except IOError:
                print ('Failed to check wiki url')

                return

    def get_wiki_url(self):
        return self.url_result


def get_base_url(url):
    return re.match(r"^.+?[^\/:](?=[?\/]|$)", url).group(0)
