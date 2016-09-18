from __future__ import unicode_literals

from django.db import models

# Create your models here.


class Word(models.Model):
    text = models.CharField(max_length=228, unique=True)

    def __unicode__(self):
        return self.text


class URL(models.Model):
    url = models.URLField(max_length=228, unique=True)

    def __unicode__(self):
        return self.url


class URLIndex(models.Model):
    url = models.ForeignKey(URL)
    text = models.ForeignKey(Word)
    count = models.IntegerField(default=0)

    def __eq__(self, other):
        if self.url.url == other.url.url:
            return True
        else:
            return False

    def __hash__(self):
        return hash(self.url.url)


class Params(models.Model):
    param = models.CharField(max_length=228)
    value = models.IntegerField(default=0)


class WikiResult(models.Model):
    query = models.CharField(max_length=228)
    wiki_url = models.URLField()

