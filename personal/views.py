from django.shortcuts import render


def home_screen_view(request):
    return render(request, 'personal/home.html')
