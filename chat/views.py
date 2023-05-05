from django.shortcuts import render, redirect
from django.conf import settings


DEBUG = False

def private_chat_room_view(request):
    user = request.user

    # Check if user is authenticated
    if not user.is_authenticated:
        return redirect('login')
    
    context = {}
    context['debug'] = DEBUG
    context['debug_mode'] = settings.DEBUG
    return render(request, 'chat/room.html', context)
