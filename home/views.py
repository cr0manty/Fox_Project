import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from home.models import MyApp
from youtube_saver.models import DownloadYoutubeMP3ShortLink


class HomeView(View):
    def get(self, request):
        apps = MyApp.objects.all()
        return render(request, 'home/home.html', context={
            'apps': apps,
        })


class AppView(View):
    def get(self, request, slug):
        app = get_object_or_404(MyApp, slug=slug)
        return render(request, 'home/home.html', context={
            'app': app,
        })


def url_shorter(request, slug):
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    link = get_object_or_404(DownloadYoutubeMP3ShortLink, slug=slug, created_at__gt=yesterday)
    return redirect(link.url)
