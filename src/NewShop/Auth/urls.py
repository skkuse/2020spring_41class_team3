from django.urls import include, path, re_path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [ 
    path('login/',views.sign_in,name='login'),
    path('signup/',views.sign_up,name='signup'),
    path('signup/verification/',views.verify,name='verification'),
    path('logout',views.sign_out,name='logout'),
    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate, name='activate'),
    re_path(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.pw_reset_by_mail, name='pw_reset'),
    path('find-user/',views.id_finder,name='idfind'),
    path('find-pw/',views.pw_finder,name='pwfind'),
    path('reset-pw/<int:usr>',views.pw_reset,name='pw_reset2'),
    path('reset-pw/',views.pw_reset2,name='pw_reset3'),
]