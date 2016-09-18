from bs4 import BeautifulSoup
from collections import Counter
from .indexer import Indexer
import re
import urllib2
import robotparser
from validators import url
from .utils import get_base_url


class Crawler(object):
    def __init__(self):
        self.base_url = None
        self.visited_urls = set()
        self.global_search = False
        self.indexer = Indexer()
        self.width = None
        self.current_depth = None

        self.max_file_size = 500 * 1024

    def pass_robots_txt(self, url):
        rp = robotparser.RobotFileParser()
        rp.set_url(self.base_url)
        rp.read()

        if rp.can_fetch("*", url):
            return True
        else:
            print ("robots.txt pass failed for", url)
            return False

    def remember_base_url(self, url):
        self.base_url = get_base_url(url)

    def run(self, url, width=0, depth=0, global_search = False):
        self.remember_base_url(url)
        self.global_search = global_search
        self.visit_url_and_save_index(url, width, depth)

    def visit_url_and_save_index(self, url, width, depth):
        if depth == -1:
            return

        if not self.pass_robots_txt(url):
            return

        current_url = url

        try:
            response = urllib2.urlopen(current_url)
            html = response.read()

            if len(html) > self.max_file_size:
                raise Exception

            soup = BeautifulSoup(html)
        except Exception:
            print ("Failed while visiting (very big or corrupted):", current_url)
            return

        self.indexer.add_url_to_database(current_url)

        depth -= 1

        urls = self.get_useful_urls(soup)

        self.current_depth = depth
        self.width = width

        for url in urls:
            if width == 0:
                break

            if url in self.visited_urls:
                continue

            self.visited_urls.add(url)
            width -= 1

            self.visit_url_and_save_index(url, width, depth)

        words = self.get_visible_words_and_count(soup).iteritems()

        print ("adding to index:", current_url)

        self.indexer.create_index(words, current_url)

    def get_visible_words_and_count(self, soup):
        def visible(element):
            if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
                return False
            elif re.match('<!--.*-->', str(element)):
                return False

            if element == '\n':
                return False

            return True

        data = soup.findAll(text=True)

        visible_texts = filter(visible, data)
        words = list()
        for text in visible_texts:
            result = re.findall(r'[0-9a-z\']+', text.lower())

            for res in result:
                words.append(res)

        self.indexer.add_words_to_database(set(words))

        return Counter(words)

    def get_useful_urls(self, soup):
        urls = set()

        refs = soup.findAll('a')

        for ref in refs:
            try:
                href = ref['href']
            except KeyError:
                continue

            if self.global_search and url(href):
                Crawler().run(href, self.width, self.current_depth)
                continue

            if self.base_url in href:
                urls.add(href)
                continue

            if len(href) < 2:
                continue

            if '//' in href:
                continue

            if href[0] != '/':
                continue

            urls.add(self.base_url + href)

        return urls



