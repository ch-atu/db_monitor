from django.urls import path
from django.conf.urls import url
from mysql import views

app_name = "mysql"

urlpatterns = [
    path('api/mysql-stat-list', views.ApiMysqlStatList.as_view()),
    path('api/mysql-stat', views.ApiMysqlStat.as_view()),
    path('api/mysql-stat-his', views.ApiMysqlStatHis.as_view()),
    path('api/mysql-slowquery', views.ApiMysqlSlowquery.as_view()),
    url(r'api/del_mysql_stat/(?P<host>.*)', views.del_mysql_stat)
]

