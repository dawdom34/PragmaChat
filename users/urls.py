from django.urls import path

from users.views import (
	account_view,
)

app_name = 'users'

urlpatterns = [
	path('<user_id>/', account_view, name="view"),
]