from django.urls import path
from . import views

urlpatterns = [
    path('', views.monument_search, name='home'),
    path("scrape/", views.scrape_data, name='scrape'),
]