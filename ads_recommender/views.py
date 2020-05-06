import time
from _md5 import md5

import requests
import json

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.contrib.auth.models import User

from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from ads_recommender.meta_impl import Meta


class Index(View):
    def get(self, request):
        if request.user.is_authenticated:
            uid = request.user.id
            candidates = Meta().calc_candidates(uid)
            context = {
                'username': request.user.username,
                'candidates': candidates,
            }
            if len(candidates) == 0:
                context['special_list'] = Meta().get_special_list()
            return render(request, "index.html", context=context)
        else:
            return HttpResponseRedirect(redirect_to='/sign_in')

    def post(self, request):
        return HttpResponseRedirect(redirect_to='/')


def logout_view(request):
    logout(request)

    return HttpResponseRedirect(redirect_to='/sign_in')


class SignUp(View):
    def get(self, request):
        return render(request, "sign_up.html")

    def post(self, request):
        print(request.POST)

        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            return render(request, "sign_up.html", context={'username': username})

        pass_hash = int(md5(password1.encode()).hexdigest()[:5], 16)
        user = User.objects.create_user(username, password=pass_hash)

        return HttpResponseRedirect(redirect_to='/sign_in')


class SignIn(View):
    def get(self, request):
        return render(request, "sign_in.html")

    def post(self, request):
        username = request.POST.get('username')
        pass_hash = request.POST.get('password')
        print(pass_hash)
        pass_hash = int(md5(pass_hash.encode()).hexdigest()[:5], 16)
        user = authenticate(username=username, password=pass_hash)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(redirect_to='/')

        return HttpResponseRedirect(redirect_to='/sign_in')


@csrf_exempt
def submit_movies(request):
    movies = json.loads(request.body).get('movies')
    if not movies:
        return HttpResponse()
    Meta().create_user(request.user.id, movies)
    return HttpResponse()
