from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


def login_page(request):
    return render(request, "pages/login.html")


def index(request):
    return HttpResponseRedirect(reverse("login"))