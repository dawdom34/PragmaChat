from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse

from .models import GroupChatRoom

from friend.models import FriendList

from users.models import Account

import json

DEBUG = False

def group_chat_room_view(request):
    user = request.user
    context = {}

    # Redirect to login page if user not authenticated
    if not user.is_authenticated:
        return redirect('login')
    
    # Get groups of which the user is a part
    groups_raw = GroupChatRoom.objects.filter(users=user)

    # Combine groups with infomation about if user is an admin of each one
    groups = [(x, x.is_admin(user)) for x in groups_raw]
    
    context['debug'] = DEBUG
    context['debug_mode'] = settings.DEBUG
    context['groups'] = groups
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

def create_group(request):
    """
    Activated by ajax function to create the group with given users
    """
    user = request.user
    payload = {}
    
    # Get args from request
    group_name = request.POST.get('group_name')
    selected_friends = request.POST.get('selected_friends')
    
    # Convert str to list
    friends = selected_friends.split(',')
    # Remove last element, it's empty string
    friends.pop(-1)

    if friends == None:
        friends = []

    if request.method == 'POST' and user.is_authenticated:
        # Check if group title is not empty
        if group_name.strip() != '':
            # Check if selected users contains at least two users
            if len(friends) >= 2:
                # Check if selected users exist
                friends_valid = True
                for friend in friends:
                    try:
                        user_validate = Account.objects.get(id=int(friend))
                    except Account.DoesNotExist:
                        friends_valid = False
                        payload['response'] = 'One of selected friend is invalid.'

                # Add auth user id to friends list
                friends.append(user.id)

                group_valid = True
                # Check if group with the same users already exist
                # users_group = [[1,3,4], [3], [3,6,7]]
                users_groups = []
                for friend in friends:
                    # Get user object
                    x = Account.objects.get(id=int(friend))
                    # Get all groups of witch the user is a part of 
                    g = GroupChatRoom.objects.filter(users=x)
                    temp = []
                    # Append id's to users groups
                    for y in g:
                        temp.append(y.id)
                    users_groups.append(temp)

                common_groups = set(users_groups[0])
                for s in users_groups[1:]:
                    common_groups.intersection_update(s)

                for gr in common_groups:
                    qr = GroupChatRoom.objects.get(id=gr)
                    qr_users = qr.users.all()
                    if len(qr_users) == len(friends):
                        group_valid = False
                        payload['response'] = 'Group with selected users already exist.'

                if friends_valid and group_valid:
                    # Create group
                    group_chat_rom = GroupChatRoom.objects.create(title=group_name, owner=user)

                    # Add selected users to the group
                    for friend in friends:
                        person = Account.objects.get(id=int(friend))
                        group_chat_rom.add_user(person)
                    
                    # Add owner to admins group
                    group_chat_rom.add_admin(user)

                    payload['response'] = 'Group created.'
            else:
                payload['response'] = 'You must select at least two friends to create a group.'
        else:
            payload['response'] = 'Invalid group name.'
    else:
        payload['response'] = 'You must be authenticated to create group.'
    
    return HttpResponse(json.dumps(payload))

def edit_group_view(request, *args, **kwargs):
    """
    Display all information about the group with ability to edit them
    Only admin have access to this view
    """
    user = request.user
    context = {}
    group_id = kwargs.get('group_id')

    if not user.is_authenticated:
        return redirect('login')
    
    # Check if group exist
    try:
        group = GroupChatRoom.objects.get(id=group_id)
    except GroupChatRoom.DoesNotExist:
        raise ValueError('Group does not exist')
    
    # Check if user is admin
    if not group.is_admin(user):
        raise ValueError('You have no admin privileges.')
    
    # Combine users is group with extra information about privileges
    group_friends = [(x, group.is_owner(x), group.is_admin(x)) for x in group.users.all()]
    
    # Get all friends of authenticated user
    friends_list = FriendList.objects.get(user=user)
    # Filter users who are not in the group
    friends = []
    for friend in friends_list.friends.all():
        if friend not in group.users.all():
            friends.append(friend)

    context['group_friends'] = group_friends
    context['friends'] = friends
    context['admins'] = group.admins.all()
    context['owner'] = group.owner
    context['group_title'] = group.title
    context['group_id'] = group.id
    
    return render(request, 'group_chat/edit_group.html', context)