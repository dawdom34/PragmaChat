from django.shortcuts import render, redirect
from django.conf import settings

from friend.models import FriendList

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

def create_group_view(request):
    """
    Create new group view.
    This function displays the friends in the template that the user can select to create a group
    """
    user = request.user
    context = {}

    # Redirect them if not authenticated
    if not user.is_authenticated:
        return redirect("login")
    
    # Get all friends of authenticated user
    friend_list = FriendList.objects.get(user=user)
    friends = friend_list.friends.all()

    context['friends'] = friends

    return render(request, 'group_chat/create_group.html', context)