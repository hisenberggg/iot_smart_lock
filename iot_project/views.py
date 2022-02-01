from django.shortcuts import render


def mainpage(request):
    return render(request, "main.html")


def details(request):
    return render(request, "details.html")