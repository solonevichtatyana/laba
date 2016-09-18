from collections import Counter
from .models import URL, URLIndex, Word, WikiResult
import re
from .utils import WikiChecker, get_base_url
from threading import Lock
from django.db.utils import IntegrityError
from django.db.models import ObjectDoesNotExist


class Indexer(object):
    def __init__(self):
        self.site = None

    def add_words_to_database(self, words_with_count):
        lock = Lock()
        lock.acquire()

        try:
            words_to_db = [Word(text=word) for word in words_with_count if not Word.objects.filter(text=word).exists()]
            Word.objects.bulk_create(words_to_db)
        except IntegrityError:
            pass

        lock.release()

    def add_url_to_database(self, url):
        lock = Lock()
        lock.acquire()

        if not URL.objects.filter(url=url).exists():
            URL.objects.create(url=url)

        lock.release()

    def create_index(self, words_with_count, url):
        lock = Lock()
        lock.acquire()

        try:

            saved_url = URL.objects.get(url=url)

            ind = [URLIndex(url=saved_url, text=Word.objects.get(text=word), count=count)
                   for word, count in words_with_count if not
                   URLIndex.objects.filter(url=saved_url, text=Word.objects.get(text=word), count=count).exists()]

            URLIndex.objects.bulk_create(ind)

        except ObjectDoesNotExist:
            pass

        lock.release()

    def get_wiki_url_result(self, query):
        if WikiResult.objects.filter(query=query).exists():
            return WikiResult.objects.get(query=query).wiki_url

        wiki = WikiChecker(query)

        wiki_url = wiki.get_wiki_url()

        if wiki_url is not None:
            wiki_res = WikiResult(query=query, wiki_url=wiki_url)
            wiki_res.save()

            return wiki_url

        return None

    def get_url_results(self, query):

        regex_site = re.compile(r"site:[a-z]+\.[a-z]+")

        if regex_site.search(query):
            site_query = str(regex_site.search(query).group(0))
            query = query.replace(site_query, "")
            self.site = site_query.replace("site:", "").replace(" ", "")

            query = regex_site.sub("", query)

        query_words = re.findall(r'[0-9a-z\']+', query.lower())

        words = Word.objects.filter(text__in=query_words)
        url_indices = URLIndex.objects.filter(text__in=words)

        if self.site is None:
            url_indices = [ind for ind, count in Counter(url_indices).items()
                           if count == len(query_words)]  # black magic
        else:
            url_indices = [ind for ind, count in Counter(url_indices).items() if count == len(query_words)
                           and self.site in get_base_url(ind.url.url)]

        lst = [(url_index.count, url_index.url.url,) for url_index in url_indices]

        lst = sorted(lst, key=lambda x: x[0], reverse=True)

        result = [pair[1] for pair in lst]

        min_len_ind = -1
        min_len = 228

        for ind, link in enumerate(result):
            for word in query_words:
                if word in link:
                    if len(link) < min_len:
                        min_len = len(link)
                        min_len_ind = ind

        if min_len_ind != -1:
            result[0], result[min_len_ind] = result[min_len_ind], result[0]

        return result
