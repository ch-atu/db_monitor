from django.urls import path
from assets import views

from django.conf.urls import url
app_name = "assets"

urlpatterns = [
    path('api/mysql', views.ApiMysqlList.as_view()),
    path('api/mysql/<int:pk>', views.ApiMysqlDetail.as_view()),
    path('api/linux', views.ApiLinuxList.as_view()),
    path('api/linux/<int:pk>', views.ApiLinuxDetail.as_view()),
    path('api/redis', views.ApiRedisList.as_view()),
    path('api/redis/<int:pk>', views.ApiRedisDetail.as_view()),
    # url('^$', views.Test_alarm.as_view())
]

