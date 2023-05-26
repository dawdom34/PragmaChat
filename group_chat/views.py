from django.shortcuts import render, redirect
from django.conf import settings

DEBUG = False

def group_chat_room_view(request):
    user = request.user
    context = {}

    # Redirect to login page if user not authenticated
    if not user.is_authenticated:
        return redirect('login')
    
    context['debug'] = DEBUG
    context['debug_mode'] = settings.DEBUG
    return render(request, 'group_chat/room.html', context)
