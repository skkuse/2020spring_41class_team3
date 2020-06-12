from django.urls import include, path, re_path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [ 
    path('',views.redir),
    path('home', views.home, name='home'),     # 예를 들어 기본 주소/home은 views.home을 부르는 url이 됨. Displayer/views.py로 이동
    path('product',views.q2key,name='q2key'),
    path('product/<str:keyword>',views.search,name='search'),
    path('API/<str:keyword>',views.api_search,name='api_get'),
    path('API_xlsx/<str:keyword>', views.api_xlsx, name='api_xlsx'),
    path('API_json/<str:keyword>', views.api_json, name='api_json'),
    path('mypage', views.myPage, name='mypage'),
    path('change_pw', views.change_pw, name='change_pw'),
    path('hpchange',views.hpChange,name='hp_change'),
    path('del/<str:keyword>',views.alarmDelete,name='alarmdel'),
    path('alarm/<str:keyword>',views.alarm_set,name='alarmset'),
    path('tb:<str:keyword>',views.toggleBook,name='togglebook'),
    path('temp/<str:keyword>/next=<str:next>',views.delBook,name='delbook'),
    path('temp/<str:keyword>/',views.delHist,name='delhist'),
    path('please-search-a-keyword',views.toHome,name='home2'),
    path('report',views.report,name='report'),
]