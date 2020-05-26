from django.urls import include, path, re_path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [ 
    path('login/',views.sign_in,name='login'),
    path('signup/',views.sign_up,name='signup'),
    path('signup/verification/',views.verify,name='verification'),
    path('logout',views.sign_out,name='logout'),
    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate, name='activate'),
]