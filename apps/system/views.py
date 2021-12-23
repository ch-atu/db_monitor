# standard
import json
import logging
from datetime import timedelta

# pro
from system.models import Users
from system.models import AlertLog, AlarmConf, AlarmInfo
from apps.system.serializers import AlertLogSerializer, AlarmConfSerializer, AlarmInfoSerializer, SetupLogSerializer
from utils.tools import mysql_django_query, get_zero_time
from system.tasks import mysql_setup

# third-part
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.shortcuts import HttpResponse
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from rest_framework import permissions
from rest_framework import generics
from rest_framework import filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer

logger = logging.getLogger('system')


class UserInfo(APIView):
    """
    获取用户信息
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        token = (json.loads(request.body))['token']
        obj = Token.objects.get(key=token).user
        result = {
            'name': obj.username,
            'user_id': obj.id,
            'access': list(obj.get_all_permissions()) + ['admin'] if obj.is_superuser else list(
                obj.get_all_permissions()),
            # 'access':['hello'],
            'token': token,
            'avatar': 'https://file.iviewui.com/dist/a0e88e83800f138b94d2414621bd9704.png'
        }
        # print('用户的信息为', result)
        return HttpResponse(json.dumps(result))


class UserLogout(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        token = (json.loads(request.body))['token']
        obj = Token.objects.get(key=token)
        obj.delete()
        result = {
            "status": True
        }
        return HttpResponse(json.dumps(result))


class CustomBackend(ModelBackend):
    """
    用户名字/邮箱名字 登录
    :param request:
    :return:
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = Users.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            logger.error(e)
            return None


class Menu(APIView):

    def post(self, request):
        result = [
            # 资源管理
            {
                "path": '/assets',
                "name": 'assets',
                "meta": {
                    "icon": 'ios-cloud',
                    "title": '资源管理'
                },
                "component": 'Main',
                "children": [
                    # MySQL数据库
                    {
                        'path': 'mysql-list',
                        'name': 'mysql-list',
                        'meta': {
                            'access': ['assets.view_mysqllist'],
                            'icon': 'ios-menu',
                            'title': 'MySQL数据库'
                        },
                        'component': 'assets/mysql-list'
                    },
                    # Linux主机
                    {
                        'path': 'linux-list',
                        'name': 'linux-list',
                        'meta': {
                            'access': ['assets.view_linuxlist'],
                            'icon': 'ios-menu',
                            'title': 'Linux主机'
                        },
                        'component': 'assets/linux-list'
                    },
                    # Redis
                    {
                        'path': 'redis-list',
                        'name': 'redis-list',
                        'meta': {
                            'access': ['assets.view_redislist'],
                            'icon': 'ios-menu',
                            'title': 'Redis'
                        },
                        'component': 'assets/redis-list'
                    }
                ]
            },
            # 实例列表
            {
                "path": '/monlist',
                "name": '实例列表',
                "meta": {
                    "icon": 'ios-apps',
                    "title": '实例列表'
                },
                "component": 'Main',
                "children": [
                    # MySQL列表
                    {
                        'path': 'mysql',
                        'name': 'mysql',
                        'meta': {
                            'icon': 'ios-menu',
                            'title': 'MySQL列表',
                            'access': ['mysql.view_mysqlstat'],
                        },
                        'component': 'mysql/stat-list'
                    },
                    # Redis列表
                    {
                        'path': 'redis',
                        'name': 'redis',
                        'meta': {
                            'icon': 'ios-menu',
                            'title': 'Redis列表',
                            'access': ['rds.view_redisstat'],
                        },
                        'component': 'redis/stat-list'
                    },
                    # Linux列表
                    {
                        'path': 'linux',
                        'name': 'linux',
                        'meta': {
                            'icon': 'ios-menu',
                            'title': 'Linux列表',
                            'access': ['linux.view_linuxstat'],
                        },
                        'component': 'linux/stat-list'
                    }
                ],

            },
            # 监控告警
            {
                "path": '/alarm',
                "name": 'alarm',
                "meta": {
                    "icon": 'ios-warning',
                    "title": '监控告警'
                },
                "component": 'Main',
                "children": [
                    # 告警记录
                    {
                        'path': 'alarm-info',
                        'name': 'alarm-info',
                        'meta': {
                            'access': ['system.view_alarminfo'],
                            'icon': 'ios-menu',
                            'title': '告警记录'
                        },
                        'component': 'system/alarm-info'
                    },
                    # 告警配置
                    {
                        'path': 'alarm-conf',
                        'name': 'alarm-conf',
                        'meta': {
                            'access': ['system.view_alarmconf'],
                            'icon': 'ios-menu',
                            'title': '告警配置'
                        },
                        'component': 'system/alarm-conf'
                    }
                ]
            },
            # 数据库部署
            {
                "path": '/setup',
                "name": 'setup',
                "meta": {
                    "icon": 'ios-build',
                    "title": '数据库部署',
                    'hideInMenu': 'true',
                },
                "component": 'Main',
                "children": [
                    # MySQL
                    {
                        'path': 'MySQL',
                        'name': 'MySQL',
                        'meta': {
                            'access': ['system.view_alarminfo'],
                            'icon': 'ios-menu',
                            'title': 'MySQL'
                        },
                        'component': 'system/mysql-setup'
                    }
                ]
            },
            # Linux主机监控
            {
                "path": '/linux',
                "name": 'Linux',
                "meta": {
                    'hideInMenu': 'true',
                    "icon": 'ios-apps',
                    "title": 'Linux主机监控'
                },
                "component": 'Main',
                "children": [
                    # Linux概览
                    {
                        'path': ':tags/view',
                        'name': 'linux-view',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': 'Linux概览',
                            'access': ['linux.view_linuxstat'],
                        },
                        'component': 'linux/view'
                    },
                    # 磁盘IO
                    {
                        'path': ':tags/io',
                        'name': 'linux-io',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': '磁盘IO',
                            'access': ['linux.view_linuxstat'],
                        },
                        'component': 'linux/io'
                    },
                    # 内存 & 虚拟内存
                    {
                        'path': ':tags/memory',
                        'name': 'linux-memory',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': '内存&虚拟内存',
                            'access': ['linux.view_linuxstat'],
                        },
                        'component': 'linux/memory'
                    }
                ]
            },
            # MySQL数据库监控
            {
                "path": '/mysql',
                "name": 'MySQL',
                "meta": {
                    'hideInMenu': 'true',
                    "icon": 'ios-apps',
                    "title": 'MySQL数据库监控'
                },
                "component": 'Main',
                "children": [
                    # MySQL概览
                    {
                        'path': ':tags/view',
                        'name': 'mysql-view',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': 'MySQL概览',
                            'access': ['mysql.view_mysqlstat'],
                        },
                        'component': 'mysql/view'
                    },
                    # MyISAM
                    {
                        'path': ':tags/myisam',
                        'name': 'mysql-myisam',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': 'MyISAM',
                            'access': ['mysql.view_mysqlstat'],
                        },
                        'component': 'mysql/myisam'
                    },
                    # Innodb
                    {
                        'path': ':tags/innodb',
                        'name': 'mysql-innodb',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': 'Innodb',
                            'access': ['mysql.view_mysqlstat'],
                        },
                        'component': 'mysql/innodb'
                    },

                    # # todo 后台日志
                    # {
                    #     'path': ':tags/alert-log',
                    #     'name': 'mysql-alert-log',
                    #     'meta': {
                    #         'hideInMenu': 'true',
                    #         'title': '后台日志',
                    #         'access': ['mysql.view_mysqlstat'],
                    #     },
                    #     'component': 'mysql/alert-log'
                    # },
                    # # todo 慢查询
                    # {
                    #     'path': ':tags/slowquery-log',
                    #     'name': 'mysql-slowquery-log',
                    #     'meta': {
                    #         'hideInMenu': 'true',
                    #         'title': '慢查询',
                    #         'access': ['mysql.view_mysqlstat'],
                    #     },
                    #     'component': 'mysql/slowquery-log'
                    # }
                ]

            },
            # Redis数据库监控
            {
                "path": '/redis',
                "name": 'Redis',
                "meta": {
                    'hideInMenu': 'true',
                    "icon": 'ios-apps',
                    "title": 'Redis监控'
                },
                "component": 'Main',
                "children": [
                    # Redis概览
                    {
                        'path': ':tags/view',
                        'name': 'redis-view',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': 'Redis概览',
                            'access': ['rds.view_redisstat'],
                        },
                        'component': 'redis/view'
                    },
                    # Redis实时状态
                    {
                        'path': ':tags/immediate-stats',
                        'name': 'redis-immediate-stats',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': 'Redis实时状态',
                            'access': ['rds.view_redisstat'],
                        },
                        'component': 'redis/immediate-stats'
                    },
                    # Redis配置项
                    {
                        'path': ':tags/config',
                        'name': 'redis-config',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': 'Redis配置项',
                            'access': ['rds.view_redisstat'],
                        },
                        'component': 'redis/config'
                    },
                    # 连接信息
                    {
                        'path': ':tags/clientlist',
                        'name': 'redis-clientlist',
                        'meta': {
                            'hideInMenu': 'true',
                            'title': '连接信息',
                            'access': ['rds.view_redisstat'],
                        },
                        'component': 'redis/clientlist'
                    },

                    # todo 慢查询分析
                    # {
                    #     'path': ':tags/slowlog',
                    #     'name': 'redis-slowlog',
                    #     'meta': {
                    #         'hideInMenu': 'true',
                    #         'title': '慢查询分析',
                    #         'access': ['rds.view_redisstat'],
                    #     },
                    #     'component': 'redis/slowlog'
                    # },

                    # # todo 命令曲线
                    # {
                    #     'path': ':tags/commandstats',
                    #     'name': 'redis-commandstats',
                    #     'meta': {
                    #         'hideInMenu': 'true',
                    #         'title': '命令曲线',
                    #         'access': ['rds.view_redisstat'],
                    #     },
                    #     'component': 'redis/command-stats'
                    # },

                    # # todo 后台日志
                    # {
                    #     'path': ':tags/alert-log',
                    #     'name': 'redis-alert-log',
                    #     'meta': {
                    #         'hideInMenu': 'true',
                    #         'title': '后台日志',
                    #         'access': ['rds.view_redisstat'],
                    #     },
                    #     'component': 'redis/alert-log'
                    # },
                ]

            }
        ]
        return HttpResponse(json.dumps(result))


class ApiAlertLog(generics.ListAPIView):
    queryset = AlertLog.objects.all().order_by('-log_time')
    serializer_class = AlertLogSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filter_fields = ['tags', 'log_level']
    search_fields = ['log_content']
    permission_classes = (permissions.DjangoModelPermissions,)


class ApiAlarmConf(generics.ListCreateAPIView):
    # queryset = AlarmConf.objects.get_queryset().order_by('-type')
    # 模糊查询
    def get_queryset(self):
        name = self.request.query_params.get('name', None)
        if not name:
            return AlarmConf.objects.all().order_by('-type')
        alarm_confs = AlarmConf.objects.filter(name__icontains=name).order_by('-type')
        return alarm_confs
    serializer_class = AlarmConfSerializer
    # filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    # filter_fields = ('type', 'name',)
    # search_fields = ('type', 'name',)
    permission_classes = (permissions.DjangoModelPermissions,)


class ApiAlarmConfDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = AlarmConf.objects.get_queryset().order_by('id')
    serializer_class = AlarmConfSerializer
    permission_classes = (permissions.DjangoModelPermissions,)


# 此接口暂时不用
class ApiAlarmInfo(generics.ListCreateAPIView):
    def get_queryset(self):
        tags = self.request.query_params.get('tags', None)
        if tags:
            # result = AlarmInfo.objects.filter(tags=tags).order_by('-id')
            return AlarmInfo.objects.filter(tags=tags).order_by('-id')  # 倒序
        else:
            return AlarmInfo.objects.all().order_by('-id')  # 倒序

    serializer_class = AlarmInfoSerializer
    permission_classes = (permissions.DjangoModelPermissions,)


# 告警信息查询
class ApiExportAlarmInfo(generics.ListAPIView):
    def get_queryset(self):
        alarm_info = []
        # 获取每个视图页面的告警信息
        tags = self.request.query_params.get('tags', None)
        alarm_type = self.request.query_params.get('alarm_type', None)
        if tags and alarm_type:
            # 获取今天零点到查询时刻的告警信息
            zero_today, now = get_zero_time(0)
            # print('进来了！')
            return AlarmInfo.objects.filter(tags=tags,
                                            alarm_type__icontains=alarm_type,
                                            alarm_time__gte=zero_today,
                                            alarm_time__lte=now
                                            ).order_by('-alarm_time')

        # 获取告警记录页面的告警信息
        day_field = self.request.query_params.get('day', None)
        if day_field and day_field != 'NaN':
            if day_field == '1':
                # 获取今天零点到查询时刻的告警信息
                zero_today, now = get_zero_time(0)

                alarm_info = AlarmInfo.objects.filter(alarm_time__gte=zero_today,
                                                      alarm_time__lte=now
                                                      ).order_by('-alarm_time')
            elif day_field == '-1':
                # 获取昨天的00:00:00点到23:59:59
                zero_yesterday, now = get_zero_time(abs(int(day_field)))
                last_yesterday = zero_yesterday + timedelta(hours=23, minutes=59, seconds=59)

                alarm_info = AlarmInfo.objects.filter(alarm_time__gte=zero_yesterday,
                                                      alarm_time__lte=last_yesterday
                                                      ).order_by('-alarm_time')
            elif day_field == '-7':
                # 获取7天前的00:00:00
                zero_seven, now = get_zero_time(abs(int(day_field)))

                alarm_info = AlarmInfo.objects.filter(alarm_time__gte=zero_seven,
                                                      alarm_time__lte=now
                                                      ).order_by('-alarm_time')
            elif day_field == '-30':
                # 获取30天前的00:00:00
                zero_thirty, now = get_zero_time(abs(int(day_field)))

                alarm_info = AlarmInfo.objects.filter(alarm_time__gte=zero_thirty,
                                                      alarm_time__lte=now
                                                      ).order_by('-alarm_time')
            elif day_field == '-365':
                # 获取一年前的00:00:00
                zero_before_year, now = get_zero_time(abs(int(day_field)))

                alarm_info = AlarmInfo.objects.filter(alarm_time__gte=zero_before_year,
                                                      alarm_time__lte=now
                                                      ).order_by('-alarm_time')
        else:
            # 默认获取今天零点到查询时刻的告警信息
            zero_today, now = get_zero_time(0)

            alarm_info = AlarmInfo.objects.filter(alarm_time__gte=zero_today,
                                                  alarm_time__lte=now
                                                  ).order_by('-alarm_time')

        return alarm_info

    serializer_class = AlarmInfoSerializer


# 日志导出
class ApiExcelAlarmInfo(APIView):
    def get(self, request):
        day_field = request.query_params.get('day', None)
        if day_field == '1':
            # 获取今天零点到查询时刻的告警信息
            zero_today, now = get_zero_time(0)

            alarm_info = AlarmInfo.objects.filter(alarm_time__gte=zero_today,
                                                  alarm_time__lte=now
                                                  ).order_by('-alarm_time')
        elif day_field == '-1':
            # 获取昨天的00:00:00点到23:59:59
            zero_yesterday, now = get_zero_time(abs(int(day_field)))
            last_yesterday = zero_yesterday + timedelta(hours=23, minutes=59, seconds=59)

            alarm_info = AlarmInfo.objects.filter(alarm_time__gte=zero_yesterday,
                                                  alarm_time__lte=last_yesterday
                                                  ).order_by('-alarm_time')
        elif day_field == '-7':
            # 获取7天前的00:00:00
            zero_seven, now = get_zero_time(abs(int(day_field)))

            alarm_info = AlarmInfo.objects.filter(alarm_time__gte=zero_seven,
                                                  alarm_time__lte=now
                                                  ).order_by('-alarm_time')
        elif day_field == '-30':
            # 获取30天前的00:00:00
            zero_thirty, now = get_zero_time(abs(int(day_field)))

            alarm_info = AlarmInfo.objects.filter(alarm_time__gte=zero_thirty,
                                                  alarm_time__lte=now
                                                  ).order_by('-alarm_time')
        elif day_field == '-365':
            # 获取一年前的00:00:00
            zero_before_year, now = get_zero_time(abs(int(day_field)))

            alarm_info = AlarmInfo.objects.filter(alarm_time__gte=zero_before_year,
                                                  alarm_time__lte=now
                                                  ).order_by('-alarm_time')

        serialize = AlarmInfoSerializer(instance=alarm_info, many=True)
        return Response(serialize.data)


class ApiAlarmInfoHis(generics.ListCreateAPIView):
    queryset = AlarmInfo.objects.get_queryset().order_by('-id')
    serializer_class = AlarmInfoSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ('tags',)
    search_fields = ('tags', 'alarm_content',)
    permission_classes = (permissions.DjangoModelPermissions,)


@api_view(['POST'])
def ApiMysqlSetup(request):
    postBody = request.body
    json_result = json.loads(postBody)
    node_info = json_result
    # print(json_result)
    mysql_setup.delay(node_info)
    return HttpResponse('success!')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ApiSetupLog(request):
    sql = "select id,log_type,log_time,log_level,log_content from setup_log"
    setup_log_list = mysql_django_query(sql)
    serializer = SetupLogSerializer(setup_log_list, many=True)
    json = JSONRenderer().render(serializer.data)
    return HttpResponse(json)
