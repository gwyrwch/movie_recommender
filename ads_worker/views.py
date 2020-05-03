import json

from django.http import JsonResponse
from django.shortcuts import render

from ads_worker.worker_impl import Worker


def worker(request):
    uvec = json.loads(request.body)['user_vec']
    return JsonResponse(Worker().recommend(uvec))
