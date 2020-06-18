from django.shortcuts import render
from redis import Redis
from rq_scheduler import Scheduler

scheduler = Scheduler(connection=Redis())


def test(request):
    return render(request, '404.html')
