from django.urls import path
from . import views

urlpatterns = [
    # ex: /polls/

    path('', views.home, name='home'),
    path('recommend/', views.recommend, name='recommend'),
    path('get_movies/', views.get_movies, name='get_movies'),
    # path('<int:movie_id>/', views.recommendation, name='recommendation'),
]
