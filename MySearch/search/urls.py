from django.conf.urls import url
import include

urlpatterns = [
    url(r'^indexing_view/', 'search.views.indexing_view' , name = 'indexing_view'),
    url(r'^known_urls_view/', 'search.views.known_urls_view', name = 'known_urls_view' ),
    url(r'^words_view/', 'search.views.words_view', name = 'words_view'),
    url(r'^params_view/', 'search.views.params_view', name = 'params_view'),
    url(r'^$', 'search.views.home_view', name = 'home_view'),
]
