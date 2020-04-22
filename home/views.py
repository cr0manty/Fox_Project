from django.shortcuts import render
from django.views import View

from home.models import MyApp


class HomeView(View):
    def get(self, request):
        apps = MyApp.objects.all()
        return render(request, 'home/home.html', context={
            'apps': apps,
            'amount': apps.count()
        })
