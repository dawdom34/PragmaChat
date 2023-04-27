from django.urls import path

from users.views import (
	account_view,
    edit_account_view
)

app_name = 'users'

urlpatterns = [
	path('<user_id>/', account_view, name="view"),
    path('<user_id>/edit/', edit_account_view, name='edit'),
]