from django.shortcuts import render
from thread import start_new_thread
from .crawler import Crawler
from .indexer import Indexer
from .models import URL, URLIndex, Params, Word, WikiResult
from .forms import RadioForm, CleanDataBaseForm
import re
# Create your views here.


def home_view(request):
    context = {}

    query = request.GET.get('input')

    if query:
        indexer = Indexer()
        urls = indexer.get_url_results(query)

        wiki_url = None

        if 'site:' not in query:
            wiki_url = indexer.get_wiki_url_result(query)

        if Params.objects.get(param='wiki').value != 0:
            if wiki_url is not None:

                context['wiki_url'] = wiki_url

        context['urls'] = urls
        context['number_of_results'] = len(urls)

    return render(request, 'home.html', context)


def indexing_view(request):
    context = {}

    try:
        if request.method == 'GET':
            data = request.GET

            if data.items():
                url = data.get('url')
                width = int(data.get('width'))
                depth = int(data.get('depth'))

                start_new_thread(Crawler().run, (url, width, depth,
                                 Params.objects.get(param='crawler_global_search').value))

        if request.method == 'POST':
            data = request.POST
            f = request.FILES['docfile']
            f.open('r')

            width = int(data.get('width'))
            depth = int(data.get('depth'))

            urls = f.read().split('\n')
            f.close()

            print urls

            for url in urls:
                print "run for:", url
                start_new_thread(Crawler().run, (url, width, depth,))
    except Exception:
        print "one big error.."

    return render(request, 'index_url.html', context)


def known_urls_view(request):
    context = {}

    url_list = list()

    if request.GET.get('update'):
        indexed_urls = URL.objects.all()

        for url_obj in indexed_urls:
            url_list.append(url_obj)

    context['urls'] = url_list

    return render(request, 'known_urls.html', context)


def words_view(request):
    context = {}

    id = int(request.GET.get('id'))

    url_indices = URLIndex.objects.filter(url=URL.objects.get(id=id))

    words = list()

    for url_index in url_indices:
        words.append((url_index.text.text, url_index.count,))

    words = sorted(words, key=lambda x: x[1], reverse=True)

    context['words'] = words
    context['url'] = URL.objects.get(id=id).url

    return render(request, 'words.html', context)


def params_view(request):
    context = {}

    if not Params.objects.filter(param='wiki').exists():
        param = Params(param='wiki', value=1)
        param.save()

    if not Params.objects.filter(param='crawler_global_search').exists():
        param = Params(param='crawler_global_search', value=0)
        param.save()

    if request.POST.get('Save'):

        if request.method == 'POST':
            data = request.POST

            param = Params.objects.get(param='wiki')
            param.value = data.get('wiki')
            param.save()

            param = Params.objects.get(param='crawler_global_search')
            param.value = data.get('crawler_global_search')
            param.save()

    if request.POST.get('Clear'):
        checked_list = request.POST.getlist('clear_database')

        if 'wiki' in checked_list:
            pass

        if 'index' in checked_list:
            URLIndex.objects.all().delete()
            Word.objects.all().delete()
            URL.objects.all().delete()

    radio = RadioForm({'wiki': Params.objects.get(param='wiki').value,
                   'crawler_global_search': Params.objects.get(param='crawler_global_search').value})

    clear_db = CleanDataBaseForm()
    context['clear_db'] = clear_db
    context['radio'] = radio

    return render(request, 'params.html', context)
