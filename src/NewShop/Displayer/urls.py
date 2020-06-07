from django.urls import include, path, re_path
from django.contrib.auth import views as auth_views
from . import views
from django.conf.urls import url


urlpatterns = [ 
    path('',views.redir),
    path('home', views.home, name='home'),     # 예를 들어 기본 주소/home은 views.home을 부르는 url이 됨. Displayer/views.py로 이동
    path('product',views.product,name='product'),
    path('product/<str:keyword>',views.search,name='search'),
    path('API', views.api, name='API'),
    path('API/<str:keyword>',views.api_search,name='api_get'),
    path('mypage', views.myPage, name='mypage'),
    path('change_pw', views.change_pw, name='change_pw'),
    path('hpchange',views.hpChange,name='hp_change'),
]