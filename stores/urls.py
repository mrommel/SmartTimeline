from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard', views.index, name='index'),
    path('apps/ios/<int:sku>', views.ios_app, name='ios_app'),
    path('apps/ios/betaTesters/<id>', views.ios_beta_testers, name='ios_beta_testers'),
    path('apps/ios/allInhouseTesters', views.ios_all_inhouse_beta_testers, name='ios_all_inhouse_beta_testers'),
    path('apps/ios/delete/beta_tester/<id>', views.ios_delete_beta_testers, name='ios_delete_beta_testers'),
]