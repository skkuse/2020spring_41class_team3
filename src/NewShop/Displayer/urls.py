from django.urls import include, path, re_path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [ 
    path('',views.redir),
    path('home', views.home, name='home'),     # 예를 들어 기본 주소/home은 views.home을 부르는 url이 됨. Displayer/views.py로 이동
    path('product',views.product,name='product'),
    path('API', views.api, name='API'),
    path('mypage', views.myPage, name='mypage'),
]