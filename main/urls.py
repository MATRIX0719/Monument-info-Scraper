from django.urls import path
from . import views

urlpatterns = [
    path("search/",views.monument_search),
    path("data/", views.scrape_data, name='data'),
]