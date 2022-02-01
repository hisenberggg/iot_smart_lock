from django.urls import path

from . import views
from . import views1

from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('restricted', views.restricted, name='restricted'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('logs', views.table_data, name='logs'),
    path('', views.loginPage, name='login'),
    path('form', views.registerPage, name='form'),
    path('video_feed', views.video_feed, name='video_feed'),
    path('rec_feed', views.recognizer_feed, name='rec_feed'),
    path('logout', views.logoutUser, name="logout"),
    path('send_otp', views.send_otp, name="send_otp"),
    path('verify_otp', views.verify_otp, name="verify_otp"),
    path('chat', views1.chatbot, name="chat")
]

urlpatterns += staticfiles_urlpatterns()