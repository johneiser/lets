from django.urls import path
from . import views

urlpatterns = [
    path("<path:module>", views.do, name="do")
]