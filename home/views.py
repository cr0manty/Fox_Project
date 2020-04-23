from django.shortcuts import render, get_object_or_404
from django.views import View

from home.models import MyApp


class HomeView(View):
    def get(self, request):
        apps = MyApp.objects.all()
        return render(request, 'home/home.html', context={
            'apps': apps,
            'amount': apps.count(),
            'even': not bool(apps.count() % 2)
        })


class AppView(View):
    def get(self, request, slug):
        app = get_object_or_404(MyApp, slug=slug)
        return render(request, 'home/home.html', context={
            'app': app,
        })
