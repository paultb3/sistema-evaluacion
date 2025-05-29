from . import views
from django.urls import path


app_name = "core"
urlpatterns = [
    path("", views.login_view, name="login"),
]
