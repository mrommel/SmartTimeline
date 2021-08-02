from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard', views.index, name='index'),
    # apps
    path('apps/', views.apps, name='apps'),
    path('apps/<int:app_id>/', views.app, name='app'),
    # releases
    path('releases/', views.releases_redirect, name='releases_redirect'),
    path('releases/all', views.releases_all, name='releases_all'),
    path('releases/<int:release_month>/<int:release_year>', views.releases, name='releases'),
    path('releases/add/', views.add_release, name='add_release'),
    path('releases/<int:release_id>/', views.add_release, name='add_release'),
    # ratings
    path('ratings/', views.ratings, name='ratings'),
    path('lastratings/', views.ratings_last_months, name='ratings_last_months'),
    path('ratings/add/', views.add_ratings, name='add_ratings'),
    # active users
    path('active_users/', views.active_users, name='active_users'),
    path('active_users/add/', views.add_active_users, name='add_active_users'),
]
